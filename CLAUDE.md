# imarina — architecture notes

## What this does

Produces the next iMarina iPublic load spreadsheet from two inputs: an A3 database
dump (employee data snapshot, A3 format) and the previous iMarina iPublic load
(iMarina format). `build` merges/transforms these (plus several static dictionary
files) into the next iMarina-format spreadsheet, which is later pushed to the
iMarina server over FTP (`publish`).

## CLI commands and the pipeline

Four subcommands, wired in `src/imarina/cli.py`: `download`, `build`, `upload`,
`publish`. They do **not** pass data to each other directly — there is
no manifest or explicit handoff. They communicate purely through a **filesystem
naming convention**: fixed folder names and fixed filenames, all relative to
`PROJECT_DIR = Path.cwd()` (`core/defines.py`). This is the entire contract
between stages; if you rename `FILENAME_PREFIX`/`DATETIME_FORMAT`
(`core/defines.py`) or a default filename in `build`'s options, you silently
break the handoff to the next stage.

The **Jenkinsfile is the authoritative spec** for how these commands compose in
production — it's the only place the end-to-end flow is written down:

```
rm -rf input
imarina download --id <OperationID>   # populates ./input
imarina build                          # reads ./input, writes ./output
imarina upload                         # autodetects latest file in ./output, pushes to SharePoint for review
```

`publish` (FTP → iMarina server) is **deliberately not** part of the automated
pipeline — it's a manual, human-triggered step run after someone reviews the
SharePoint copy that `upload` produced.

### `download` — two independent mechanisms feeding one folder

`commands/download/cli.py`. Target folder defaults to `./input` (`-d/--directory`
override via `DirectoryOpt`, `core/shared_options.py`). Two unrelated things
happen, both writing flat into that same folder:

1. `download_input_from_sharepoint()` (`core/sharepoint.py`) lists **every**
   `.xlsx` file in a fixed SharePoint library folder
   (`Institutional Strengthening/_Projects/iMarina_load_automation/input`) and
   downloads all of them as-is. This is how the 6 static "dictionary" files
   arrive (`countries.xlsx`, `Job_Descriptions.xlsx`, `Personal_web.xlsx`,
   `unit_group.xlsx`, `unit_type.xlsx`, `job_description_entity.xlsx`) — they're
   maintained by hand on SharePoint and just bulk-synced down.
2. `get_parameters_list(operation_id)` looks up an MS List item by the `--id`
   (Operation ID, passed in from the Jenkins job parameter) and reads two
   sharing-link fields off it — "A3 Excel Link" and "iMarina Excel Link" — then
   downloads those two specific files as `A3.xlsx` and `iMarina.xlsx`,
   overwriting anything step 1 already placed under those names.

Net effect / contract: **`download`'s job is to leave exactly the 8 files
`build` expects, under their exact expected filenames, in `./input`** — by
whatever combination of bulk-sync and targeted-link-download is needed. It does
not create any documented substructure; it's flat.

### `build` — the clear one

`commands/build/cli.py`. Reads 8 fixed-filename `.xlsx` inputs from
`./input` by default (all individually overridable as CLI options — see
`build_controller`), writes one output file to
`./output/iMarina_upload_<timestamp>.xlsx` (`DATETIME_FORMAT` /
`FILENAME_PREFIX`/`FILENAME_SUFFIX` in `core/defines.py` define the naming
scheme other commands later parse back out). None of the 8 input files are
committed to git (`input/.gitignore` excludes everything but itself) — they
must be supplied fresh by `download` (or manually) on every run.

### `upload` — review copy, to SharePoint

`commands/upload/cli.py`. If no `--file-path` given, scans `./output/*.xlsx`
and picks the most recent by mtime (not by the timestamp in the filename).
Pushes it to a SharePoint review folder
(`.../iMarina_load_automation/output`) via `upload_file_sharepoint`. This is
the file a human reviews before deciding to `publish`.

### `publish` — the real, human-gated production push

`commands/publish/cli.py`. If no `--file-path` given, `select_file_to_upload()`
first tries to find the newest file by **parsing the timestamp out of the
filename** (`iMarina_upload_<DATETIME_FORMAT>.xlsx`), falling back to mtime
only if none parse. Defaults to `./output` (`OUTPUT_DIR`). Uploads over FTP
to the iMarina server (`core/ftp.py`). `--dry-run` defaults to `True` — you
must explicitly pass `--dry-run false` to actually push. This is intentionally
never called by CI; it's the manual "go" step.

## Key files for this pipeline

- `src/imarina/cli.py` — command registration only
- `src/imarina/core/defines.py` — shared constants: `PROJECT_DIR` (=cwd),
  `OUTPUT_DIR`, filename prefix/suffix/datetime format used to round-trip the
  "latest file" between stages
- `src/imarina/core/sharepoint.py` — all Graph API calls (download, upload,
  MS List lookup)
- `src/imarina/core/ftp.py` — the `publish` FTP push
- `Jenkinsfile` — the authoritative description of the automated portion of
  the pipeline (download → build → upload); publish is manual
- `compose.yml` — local/dev container wiring; mounts `input`, `output`,
  `logs` as volumes

## Known architectural risk

The inter-stage contract is implicit (matching folder/filename conventions
across independently-edited files), not enforced by any shared config or
schema. Changing a default path or the filename format in one command's file
will not raise an error — it will silently desync from what the next stage
expects. If this pipeline is revisited, consider making the contract explicit
(e.g., a single source of truth for expected input/output filenames, or a
Jenkins-stage-to-stage explicit path handoff) rather than relying on cwd-based
convention.
