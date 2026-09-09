# imarina-load-researchers — architecture notes

## What this does

Produces the next iMarina iPublic load spreadsheet from two inputs: an A3 database
dump (employee data snapshot, A3 format) and the previous iMarina iPublic load
(iMarina format). `build` merges/transforms these (plus several static dictionary
files) into the next iMarina-format spreadsheet, which is later pushed to the
iMarina server over FTP (`publish`).

iMarina is ICIQ's CRIS (Current Research Information System) — the software ICIQ
uses to publish which research projects are active and who's working on them.
Since research projects are tied to researchers, keeping iMarina's researcher list
in sync with ICIQ's actual HR records (the A3 database) is a prerequisite for the
CRIS being accurate at all. This repo is the automation that keeps that sync
running without anyone manually re-typing personnel data into iMarina.

The whole workflow is a SharePoint-native app: a Microsoft Form to trigger a
request, a Microsoft List to track it, Power Automate flows to glue the steps
together, SharePoint/OneDrive to move files around, and Microsoft Approvals to
gate the final publish on human sign-off. This repo's Python package is the piece
that does the actual data transformation (`build`) and talks to those Microsoft
services over Graph API (`download`/`upload`/`publish`/`notify`); it can be run
uncoupled from SharePoint, but in production it's always driven by that
integration, since that's what non-technical requesters actually interact with.

Knowing which is the "latest" of a group of files is always deduced from the
file's name, which encodes a datetime at the start (`DATETIME_FORMAT`,
`core/defines.py`) — never from filesystem metadata, except where explicitly
noted otherwise (`select_file_to_upload`'s local mtime fallback — see the
`upload`/`publish` sections below).

## GDPR implications

This workflow moves personal data of ICIQ personnel (the A3 database dump, and
the iMarina upload derived from it) between systems with no human review of
individual records along the way, so its design has to satisfy GDPR's purpose
limitation, data minimization and storage limitation principles, not just
describe who is allowed to click the button.

**Purpose limitation.** The sole purpose of this workflow is to keep the
researcher list in iMarina in sync with ICIQ's HR records, so ICIQ can report
which research staff are currently active. The A3 dump and the resulting
iMarina upload must not be used, forwarded or retained for any other purpose by
anyone who has access to the `runtime/*` SharePoint folders.

**Data minimization / access restriction.** Triggering the workflow is
restricted to a small, named set of people with a legitimate need to do so:
- Dr. Sonia Sayalero, responsible for Institutional Strengthening operations at
  ICIQ and the Severo Ochoa administrator.
- Aleix Mariné-Tena, the data steward of ICIQ who designed, implemented and
  tests this workflow.
- Eventually, an apprentice, in case this project is assigned to them.

The A3 dumps themselves are provided manually, at most once a month, by Human
Resources of ICIQ — specifically Mara Cruz, the head of Human Resources — who
is the only authorized source of the raw HR extract entering the pipeline.

Restricting *who may trigger the workflow* only has GDPR value if it is backed
by matching SharePoint item-level permissions on the
`_Projects/imarina-load-researchers/runtime/*` folders and on the Microsoft
List and Microsoft Form themselves: restricting the form's submit button is
meaningless if the underlying files remain readable by a broader SharePoint
audience than the people named above.

**Storage limitation.** Because the "use the last file" fallback (see
`download` below) depends on every previous A3 dump and iMarina upload
remaining in `runtime/a3` and `runtime/published` indefinitely, this design
currently has no retention or purge policy for historical personal-data files,
which conflicts with the storage limitation principle. A retention period
should be defined, along with a decision on whether older dumps can be deleted
without breaking the "pick the latest" mechanism.

## Microsoft List schema

The request-tracking Microsoft List backing this workflow has these fields
(internal Graph API names, and the four-Hyperlink-columns-recreated-as-Text
gotcha, are in `core/sharepoint_fields.py`'s module docstring):

- **iMarina Excel published link** — link to the Excel file that has been
  published. Filled by `publish` if the FTP publish succeeds.
- **iMarina Excel output link** — link to the Excel file generated from the
  input (the same file that ends up published). Filled by `upload` with the
  file `build` generated.
- **iMarina Excel input link** — link to the iMarina Excel file used as input.
  Filled by the request form, or by `download`'s fallback with the latest
  published iMarina file.
- **A3 Excel input link** — link to the A3 Excel file used as input. Filled by
  the request form, or by `download`'s fallback with the latest A3 dump.
- **Workflow State** — state of the workflow, updated by both the Power
  Automate workflows and the CLI commands as the request progresses
  (`WorkflowState(StrEnum)`, `core/sharepoint_fields.py`). Values, in the
  order a normal run passes through them:
  1. `New` — set when the request form is submitted.
  2. `Preparing (Power Automate)` — set by the first Power Automate workflow
     (Request intake), just before it POSTs to Jenkins to start
     `download`/`build`/`upload` (see "Answering the request form" below).
  3. `Preparing` — set by `download` itself, once the Jenkins job actually
     starts running.
  4. `Building` — set by `build`.
  5. `Uploading` — set by `upload`, before it pushes the file to SharePoint.
  6. `Requested review` — set by the second Power Automate workflow (Upload
     review → approval → publish trigger), just before it starts the
     Microsoft Approval asking the requester for permission to publish (see
     "Publish pipeline" below).
  7. `Not published` — set by that same Power Automate workflow if the
     requester rejects the approval; the workflow ends here.
  8. `Approved publication` — set by that same Power Automate workflow,
     immediately on approval, before it POSTs to the second Jenkins job to
     start `publish`.
  9. `Publishing` — set by `publish` itself, once its Jenkins job starts running.
  10. `Published` — set by `publish` on a successful FTP push.
  11. `Error` — set by `notify --status error`, the common failure handler
      called from every step's catch block (not duplicated in
      `download`/`build`/`upload`/`publish` themselves).
- **ID** — unique identifier for the request (the "Operation ID" passed
  around the CLI as `--id`, or as `download`'s positional argument). Filled
  automatically on form submission.
- **Created By** — a person-type field with whoever submitted the request.
  Filled automatically on form submission; `notify` reads it (via
  `get_creator_email`) to know who to email.

Every Workflow State write from a CLI command is best-effort (see "Known
architectural risk" below) — a write failing here never turns an otherwise-
successful step into a hard failure, but it also means the list's state can
silently drift from reality.

## Requesting a load

### Answering the request form

The workflow starts with a human filling in the Microsoft Form, optionally
supplying links to an A3 database dump and/or a previous iMarina upload (see
"Where the raw inputs come from" below — both are optional, and `download`
falls back to the latest matching file if either is omitted). Submitting the
form creates an item in the Microsoft List with a unique ID and Workflow
State `New`.

That item's creation/modification triggers the first Power Automate workflow
("Request intake", `power-automate/README.md`), which sets Workflow State to
`Preparing (Power Automate)` and then POSTs to the main Jenkins job's
`buildWithParameters` endpoint, passing the item's ID — this is what actually
starts `download` → `build` → `upload` (see "CLI commands and the pipeline"
below). Everything from here on is not exposed to whoever submitted the form.

### Where the raw inputs come from

The A3 database dump is obtained by asking HR for a bulk export; providing a
link to it on the request form is optional — if omitted, `download` falls
back to the latest dump already sitting in
`_Projects/imarina-load-researchers/runtime/a3`. Uploaded dumps are named
`{DATETIME}__listado_personal_A3.xlsx`, where `DATETIME` is
`YYYY-MM-DD_HH-mm-ss` (e.g. `2025-03-12_12-00-00`) and represents when the A3
dump was actually taken — if the hour isn't known (a dump obtained manually,
without that precision), `12-00-00` is used; this doesn't need to be more
precise since there's at most one A3 dump a month.

The previous iMarina upload works the same way: optional on the form, and if
omitted, `download` falls back to the latest file in
`_Projects/imarina-load-researchers/runtime/published`
(`2026-05-01_12-00-00__icl_ag_personal_12539.xlsx`-style names, same
`DATETIME` convention). If a file is supplied instead, it should be uploaded
under `_Projects/imarina-load-researchers/runtime/imarina`, named the same way
as a published upload.

### Validating uploaded file names

Whenever a file lands in `runtime/imarina`, `runtime/input` or `runtime/a3`, a
separate Power Automate flow ("Input file name validation",
`power-automate/README.md`) checks the uploaded name against the conventions
above (and `build`'s translation-dictionary filenames, `TRANSLATION_FILES` in
`core/defines.py`); if it doesn't match, whoever last modified the file is
notified.

## CLI commands and the pipeline

Five subcommands, wired in `src/imarina_load_researchers/cli.py`: `download`, `build`, `upload`,
`publish`, `notify`. They do **not** pass data to each other directly — there is
no manifest or explicit handoff. They communicate purely through a **filesystem
naming convention**: fixed folder names and fixed filenames, all relative to
`PROJECT_DIR = Path.cwd()` (`core/defines.py`). This is the entire contract
between stages; if you rename `FILENAME_PREFIX`/`FILENAME_IMARINA_SUFFIX`/
`FILENAME_A3_SUFFIX`/`DATETIME_FORMAT` (`core/defines.py`) or a default
filename in `build`'s options, you silently break the handoff to the next
stage.

The **Jenkinsfile is the authoritative spec** for how these commands compose in
production — it's the only place the end-to-end flow is written down:

```
rm -rf input
imarina-load-researchers download <OperationID>                       # positional int arg, not --id; populates ./input
imarina-load-researchers build --id <OperationID>                     # reads ./input, writes ./output
imarina-load-researchers upload --id <OperationID>                    # autodetects latest file in ./output, pushes to SharePoint for review
imarina-load-researchers notify --id <OperationID> --status success   # or --status error from a catch block
```

`download`, `build` and `upload` are each individually wrapped in a
try/catch in the Jenkinsfile, calling `notify --id <OperationID> --status
error` from their own catch block — not just `upload`, as an earlier version
of this pipeline did. `--id` on `build`/`upload` (both optional, unlike
`download`'s required positional one — see each command's own section below)
is what lets each stage keep the MS List request's Workflow State field in
sync as the pipeline progresses.

`publish` (FTP → iMarina server) is **deliberately not** part of the automated
pipeline — it's a manual, human-triggered step run after someone reviews the
SharePoint copy that `upload` produced.

### `download` — two independent mechanisms feeding one folder, plus a fallback

`commands/download/cli.py`. Target folder defaults to `./input` (`-d/--directory`
override via `DirectoryOpt`, `core/shared_options.py`). Two unrelated things
happen, both writing flat into that same folder:

1. `download_files_in_folder_from_sharepoint()` (`core/sharepoint.py`) lists
   **every** `.xlsx` file in a fixed SharePoint library folder
   (`SHAREPOINT_INPUT_DIR`, `core/defines.py` —
   `_Projects/imarina-load-researchers/runtime/input`) and
   downloads all of them as-is. This is how the 7 static "dictionary" files
   (`TRANSLATION_FILES`, `core/defines.py`) arrive — they're maintained by
   hand on SharePoint and just bulk-synced down.
2. `get_parameters_list(operation_id)` looks up an MS List item by
   `id_element` (Operation ID — a required positional int argument, not a
   `--id` flag, passed in from the Jenkins job parameter) and reads two
   sharing-link fields off it — "A3 Excel input link" and "iMarina Excel input
   link" (see "Microsoft List schema" above) — then downloads those two
   specific files as `A3.xlsx` and `iMarina.xlsx`, overwriting anything step 1
   already placed under those names.

If either link is missing (both are optional on the request form — see
"Where the raw inputs come from" above), `download` falls back to selecting
the latest matching file from a dedicated SharePoint folder rather than just
skipping the file — this is implemented by `_fallback_a3`/`_fallback_imarina`
in `commands/download/cli.py`, built on `select_latest_remote_file()`
(`core/sharepoint.py`, the remote counterpart of `select_file_to_upload()` —
"latest" always means by the filename-encoded datetime, no mtime fallback,
unlike the local selector). The two fallbacks are **not symmetric**, by
design:
- **A3**: falls back to the latest dump in `runtime/a3`, downloads it to
  `A3.xlsx`, generates a sharing link straight to that file, and writes it
  back to the "A3 Excel input link" field. No copy needed — `runtime/a3` is
  already both where dumps are manually uploaded and where this fallback
  reads from.
- **iMarina**: falls back to the latest file in `runtime/published`,
  downloads it to `iMarina.xlsx`, then **re-uploads that same local file**
  into `runtime/imarina` (via the existing `upload_file()`, not a Graph
  server-side copy — see `core/sharepoint_fields.py`'s docstring for why),
  generates a sharing link to *that* copy, and writes it back to the
  "iMarina Excel input link" field. The re-upload exists so the field always
  points at a file living in the folder used as an input, not the
  published-archive folder.

Both write-backs are best-effort (broad `except` + `logger.exception`, same
as everything else in this file) — a metadata-write failure must not turn an
otherwise-successful download into a hard failure.

Net effect / contract: **`download`'s job is to leave exactly the 9 files
`build` expects, under their exact expected filenames, in `./input`** — by
whatever combination of bulk-sync, targeted-link-download and fallback
selection is needed. It does not create any documented substructure; it's
flat.

### `build` — the clear one

`commands/build/cli.py`. Reads the 9 fixed-filename `.xlsx` inputs listed in
`REQUIRED_INPUT_FILES` (`core/defines.py` — the A3 dump, the previous iMarina
upload, and the 7 translation dictionaries in `TRANSLATION_FILES`) from
`./input` by default. Each file's path can be overridden individually via its
own CLI option (e.g. `--countries-dict`), or all of them at once via
`--input-dir <dir>` (files are then looked up under `<dir>` using the same
standard names from `REQUIRED_INPUT_FILES`); a per-file option always takes
precedence over `--input-dir` for that one file — see `build_controller`'s
`_resolve_input_path` helper. Writes one output file to
`./output/<DATETIME_FORMAT>__icl_ag_personal_12539.xlsx` (`OUTPUT_FILENAME`,
built from `DATETIME_FORMAT` + `FTP_FILENAME` in `core/defines.py`; the
`FILENAME_PREFIX`/`FILENAME_IMARINA_SUFFIX`/`FILENAME_A3_SUFFIX` constants
define the naming scheme other commands later parse back out via
`parse_datetime_from_filename()` — one suffix per file kind, since A3 dumps
and iMarina files/build output don't share a filename suffix). None of the 9 input files are
committed to git (`input/.gitignore` excludes everything but itself) — they
must be supplied fresh by `download` (or manually) on every run.

Each of `build`'s per-file options also has an out-of-the-box default pointing
at its corresponding SharePoint-synced local folder (`runtime/a3`,
`runtime/published`, `runtime/input` mirrored locally under
`services/onedrive/data`, see `SHAREPOINT_LOCAL_*` in `core/defines.py`), which
lets `build` be run directly against files kept in sync by OneDrive for Linux,
skipping `download` entirely — useful when developing locally.

`build` also takes an optional `--id`, unlike `download`'s positional,
required one. It's used for nothing except updating the request's Workflow
State field to "Building" (best-effort) — it plays no part in resolving
input/output files. `build` didn't have any ID parameter before per-step
Workflow State tracking (see "Microsoft List schema" above) was introduced.

### `upload` — review copy, to SharePoint

`commands/upload/cli.py`. If no `--file-path` given, scans `./output/*.xlsx`
and picks the most recent by mtime (not by the timestamp in the filename).
Pushes it to a SharePoint review folder
(`.../imarina-load-researchers/output`) via `upload_file_sharepoint`. This is
the file a human reviews before deciding to `publish`.

Optional `--id`: if given, `upload` writes the request's Workflow State to
"Uploading" before the push, then after a successful upload generates a
sharing link for the uploaded item and writes it to the "iMarina Excel
output link" field — this is what's supposed to be the trigger for the
second Power Automate workflow that starts the Microsoft Approval asking the
requester whether to `publish` (the actual Power Automate wiring that watches
this field is outside this repo — see "Publish pipeline" below). `upload`
does not itself set Workflow State to "Requested review": that write belongs
to the second Power Automate workflow, made just before it starts the
approval, since at that point the load file is already built and the
workflow is about to ask for permission to publish it. Both `upload` writes
above are best-effort — a metadata-write failure must not turn a successful
upload into exit(1).

### `publish` — the real, human-gated production push

`commands/publish/cli.py`. If no `--file-path` given: with no `--id` either,
`select_file_to_upload()` first tries to find the newest file by **parsing
the timestamp out of the filename** (`<DATETIME_FORMAT>__icl_ag_personal_12539.xlsx`,
via `parse_datetime_from_filename()` with `FILENAME_IMARINA_SUFFIX`),
falling back to mtime only if none parse, from `./output` (`LOCAL_OUTPUT_DIR`); with
`--id`, the file is instead sourced from that request's "iMarina Excel output
link" field (downloaded via `download_shared_link_content()`) — see
`_resolve_file_path()`. Uploads over FTP to the iMarina server (`core/ftp.py`).
`--dry-run` defaults to `True` — you must explicitly pass `--dry-run false` to
actually push. This is intentionally never called by CI; it's the manual "go"
step.

On a successful (non-dry-run) publish, `_archive_published_file()` uploads
the published file to `runtime/published` **unconditionally**, regardless of
`--id` — this is what the next `download`'s iMarina fallback reads "the
latest published file" from (see "Where the raw inputs come from" above), so
it must happen even for a no-`--id` publish. Only the MS List write-back (the
"iMarina Excel published link" field + Workflow State "Published") is gated
on `--id` being given. Publishing an explicit `--file-path` with no `--id`
still works but logs a warning — this publishes with no record of it kept
anywhere.

### `notify` — build-result email to the requester

`commands/notify/cli.py`, backed by `core/mail.py` (Graph API access-token/
creator-lookup helpers, SMTP send, email-body templates — no CLI concerns).
Called from the Jenkinsfile's `iMarina upload` stage, once per branch of a
try/catch around `upload`: `--status success` after `upload` succeeds,
`--status error` from the `catch` block. `--id` is the same Operation ID
passed to `download`, used to look up the MS List item's creator (so the
email goes to whoever triggered the run) — required, no default.
`--sharepoint-path` defaults to `DEFAULT_NOTIFY_SHAREPOINT_PATH`
(`core/defines.py`, itself just `SHAREPOINT_REMOTE_OUTPUT_DIR`),
the same SharePoint review folder `upload` pushes to, and is only used to
word the success email body. Prior to this
command existing, Jenkins ran `core/mail.py` directly as a standalone
script (`python3 src/imarina_load_researchers/core/mail.py --id ... --status ...`); it's now
invoked like any other subcommand (`imarina-load-researchers notify --id ... --status ...`),
so it goes through `cli_global_callback` for logging setup like the rest of
the app instead of needing its own `configure_logging_from_settings()` call.
On `--status error`, `notify` also writes the request's Workflow State field
to "Error" (best-effort) — since it's already the common failure handler
called from every step's catch block, this is the single place that write
happens, rather than duplicating it in `download`/`build`/`upload`/`publish`
themselves. `--status` has a third value, `published` (`WorkflowStatus.PUBLISHED`,
`core/mail.py`), used only by `Jenkinsfile.publish` (see "Publish pipeline"
below) — it exists because reusing `success`'s email body
(`build_success_body`, worded "the generated file is available on SharePoint
... for review") would tell a requester whose file has *already been
published* to go review it, which is wrong. `build_published_body` says the
file was published instead.

## Publish pipeline

The human-gated FTP push described in "Answering the request form" and the
`upload`/`publish` sections above — `upload` writes an output link → the
second Power Automate workflow sets Workflow State to "Requested review" just
before it starts a Microsoft Approval asking the requester whether to publish
→ on approval, that same workflow sets Workflow State to "Approved
publication" and then makes an HTTP call that triggers `publish` — is split
across three things, only two of which are in this repo:

- **`Jenkinsfile.publish`** (repo root, alongside the main `Jenkinsfile`) —
  a second, separate Jenkins pipeline: install deps, run
  `publish --id <ID> --dry-run false`, then `notify --status published` on
  success or `notify --status error` (from a catch block) on failure. It is
  **not** triggered by the same job as the main pipeline and has no
  `ID`-defaulting/autodetection behavior of its own — it's a thin wrapper
  that assumes an `ID` was supplied by whatever triggered it.
- **A second Jenkins job**, configured (not code — this is Jenkins UI/job
  configuration, so it can't live in this repo without adopting Jenkins
  Configuration as Code, which hasn't been done) to run `Jenkinsfile.publish`
  as its Script Path, with **"Trigger builds remotely"** enabled and an
  authentication token set. That gives a URL of the shape
  `https://<jenkins-host>/job/<job-name>/buildWithParameters?token=<TOKEN>&ID=<id>`.
- **The Power Automate approval flow** (documented, not yet exported, in
  `power-automate/README.md`) calls that URL from its "on approval" branch,
  passing the MS List item's `ID`. The token must be stored as a secured
  value in the flow's connection, never inline/committed — this touches
  personnel data, same reasoning as the "GDPR implications" section above.

A duplicate trigger (retry, double-click) is mostly harmless: `publish`
archives to `runtime/published` and sets Workflow State to "Published" on
every successful run regardless of how many times it's called for the same
`ID`.

Because `publish --id` sources its file by re-downloading whatever currently
sits behind the "iMarina Excel output link" (see "`publish`" above), not a
snapshot taken when `upload` first wrote that field, the reviewer is free to
open the SharePoint file during the review window and correct errors in
place before approving — those corrections are what gets published, with no
separate resubmission step. This is intentional and is the documented
behavior on the "review" step of
`docs/docs/how-to/request-an-imarina-load.md`: approving after editing the
file publishes the edited version; only rejecting discards it.

The Microsoft Approval itself sits waiting indefinitely until the requester
accepts or rejects it, but Microsoft Approvals can optionally be configured
with a timeout. What Workflow State a timed-out approval should land on is
still undecided (probably also "Not published", same as an explicit
rejection) — see `power-automate/README.md`'s flow #3 "on timeout" bullet.

## Key files for this pipeline

- `src/imarina_load_researchers/cli.py` — command registration only
- `src/imarina_load_researchers/core/defines.py` — shared constants: `PROJECT_DIR` (=cwd),
  `LOCAL_INPUT_DIR`/`LOCAL_OUTPUT_DIR` (and their `SHAREPOINT_REMOTE_*`/
  `SHAREPOINT_LOCAL_*` counterparts), filename prefix/suffix/datetime format
  used to round-trip the "latest file" between stages, `MADRID_TZ` (see Dates
  below), and every CLI option's `DEFAULT_*` value. This is the single
  source of truth for `PROJECT_DIR` — don't recompute a project root
  elsewhere (e.g. by walking up from `__file__`); import it from here.
- `src/imarina_load_researchers/core/sharepoint.py` — all Graph API calls: file
  download/upload, MS List *read* (`get_parameters_list`,
  `get_list_item_link_field`) and *write* (`update_list_item_fields`),
  sharing-link creation (`create_sharing_link`), and remote "pick the latest
  file" (`select_latest_remote_file`, backing `download`'s fallbacks).
- `src/imarina_load_researchers/core/sharepoint_fields.py` — the MS List schema:
  `WorkflowState(StrEnum)` (the 11 values from "Microsoft List schema" above)
  and the field-name constants every read/write in `sharepoint.py` goes
  through. All five are confirmed against production. As of 2026-08-25 the
  four link fields (`FIELD_A3_EXCEL_INPUT_LINK`/`FIELD_IMARINA_EXCEL_INPUT_LINK`/
  `FIELD_IMARINA_EXCEL_OUTPUT_LINK`/`FIELD_IMARINA_EXCEL_PUBLISHED_LINK`) are
  plain single-line-of-text SharePoint columns, **not** Hyperlink/Picture
  columns — they were originally created as Hyperlink/Picture, which Graph's
  `.../items/{id}/fields` PATCH cannot write under any value format (always
  `400 invalidRequest`), and which Graph also refuses to convert to Text in
  place, so the columns were deleted and recreated as Text (same
  displayName/description) to unblock writes. That's also why their internal
  names carry a trailing `0` (`A3ExcelInputLink0`, etc.) — Graph auto-suffixes
  a new column's name when a same-named column is still in the site's recycle
  bin. `FIELD_WORKFLOW_STATE` is unrelated to that — it's always been a
  Choice column and was never affected. The module's own docstring has the
  full investigation and what to do if any of these columns is ever recreated
  again.
- `src/imarina_load_researchers/core/ftp.py` — the `publish` FTP push
- `src/imarina_load_researchers/core/shared_options.py` — every Typer `Option`/`Argument`
  annotation used by any command — metadata (help text, flags) only, no
  default values. Controller functions in `commands/*/cli.py` import the
  `*Opt` type from here and the matching `DEFAULT_*` constant from
  `core/defines.py` (`param: SomeOpt = DEFAULT_SOME`) rather than calling
  `typer.Option(...)` inline in the signature — see "Adding a new CLI
  option" below. `IdOpt` (optional `int`) is the one exception shared across
  multiple commands (`build`/`upload`/`publish`) rather than defined
  per-command, since all three need the exact same "MS List item ID,
  optional" shape.
- `src/imarina_load_researchers/core/secret.py`, `secret_name.py`, `vault.py` — see Secrets
  below.
- `Jenkinsfile` — the authoritative description of the automated portion of
  the pipeline. `download`, `build` and `upload` are each wrapped in their
  own try/catch calling `notify --status error` on failure (not just
  `upload`, as before); publish is manual.
- `Jenkinsfile.publish` — the separate, approval-triggered publish pipeline.
  See "Publish pipeline" above.
- `power-automate/README.md` — how the Power Automate flows this workflow
  depends on are exported/version-controlled (Power Platform CLI
  unpack/pack/import), plus a plain-language spec of each flow's
  trigger/action. No flow has actually been exported into this repo yet —
  see that file's "Current status".
- `compose.yml` — local/dev container wiring; mounts `input`, `output`,
  `logs` as volumes

## Secrets

`core/secret.py`'s `read_secret(name: SecretName)` is the only way application
code should read a credential. It tries, in order: `/run/secrets/<name>`
(Docker secrets) → `<PROJECT_DIR>/secrets/<name>` (local file) → environment
variable → HashiCorp Vault (`core/vault.py`). Each source's "not found" is a
specific, expected exception type (`OSError`/`KeyError`/`ValueError`/
`requests.exceptions.RequestException`); read_secret narrows the catch to
exactly those so a genuine bug in a source doesn't get silently swallowed
and treated as "just try the next source."

- `core/secret_name.py` holds `SecretName(StrEnum)` — the exhaustive list of
  secret names the app can resolve. It's deliberately its own file, not
  merged into `secret.py` or `vault.py`: `secret.py` imports from `vault.py`
  (for the Vault fallback), so if the enum lived in either of those two
  files, the other would need a circular import to use it.
- `core/vault.py`'s `_SECRET_MAP` maps `SecretName → (vault subpath, field)`.
  Not every `SecretName` needs an entry — Vault is only the last-priority
  fallback, so a name with no mapping just means "this one is never
  Vault-backed," not a bug.
- **Gotcha**: use `enum.StrEnum`, not `class X(str, Enum)`, for any enum
  whose members get f-string-interpolated into things like file paths.
  `class X(str, Enum)` members are real `str`s for `==`/hashing/dict-lookup
  purposes, but `Enum.__str__` still wins in f-strings/`format()`, so
  `f"{X.FOO}"` renders as `"X.FOO"`, not `"FOO"`. `StrEnum` (3.11+) fixes
  `__str__`/`__format__` to use the plain value. This broke the
  `/run/secrets/<name>` file lookup the first time `SecretName` was written
  as `(str, Enum)` — only equality-based checks (`in os.environ`, dict
  lookups) happened to still work, which is why it wasn't caught by tests.

## Dates

All datetimes in this codebase are deliberately timezone-aware, pinned to
`core/defines.MADRID_TZ` (`zoneinfo.ZoneInfo("Europe/Madrid")`) rather than
naive or UTC — ICIQ is in Tarragona, Spain, and the dates flowing through
`sanitize_date()`/`PERMANENT_CONTRACT_DATE`/etc. represent that institution's
real wall-clock business data (contract dates, run timestamps), not
abstract instants that should be UTC-normalized. Naive `datetime.now()` was
avoided too: it depends on the host's system timezone, which can silently
differ between a dev laptop and a UTC-configured CI/Docker runner.

**Gotcha**: `sanitize_date()` (`core/date_utile.py`) has multiple branches
(pandas `Timestamp` passthrough, string-parsed via `strptime`) that all feed
into the same downstream comparisons/subtractions against each other and
against `PERMANENT_CONTRACT_DATE`. All branches must stay consistently
aware (or consistently naive) — making only one branch tz-aware doesn't
just crash loudly on the naive/aware `TypeError` you'd expect; the `==`/`!=`
comparisons in `imarina_excel.py`'s permanent-contract check would keep
running but silently return the wrong answer instead, corrupting output
without any error being raised.

## Logging

`print()` is not used anywhere in `src/`; everything goes through
`logger = get_logger(__name__)` (`core/log_utils.py`), which adds a custom
`TRACE` level below `DEBUG`. Rough severity convention used throughout:
progress/step markers → `logger.info`; expected/anticipated failures (e.g. a
known 404 case) → `logger.error`; an exception being logged right before
`raise`/re-raise → `logger.exception(...)` (attaches the traceback
automatically — don't also pass the exception object as the message, that's
redundant); per-item chatter inside a loop over many files → `logger.debug`;
a "nothing to do" condition that's still worth surfacing → `logger.warning`.

**Gotcha**: ruff's `BLE001` (blind `except Exception`) does not fire on a
handler whose body calls `logger.exception(...)` — it treats that as
sufficient evidence the exception isn't being silently swallowed. If you
add a `# noqa: BLE001` and then also add `logger.exception(...)` to the same
handler, re-run ruff before committing — the noqa will likely become an
"unused directive" error.

## Adding a new CLI option

Don't call `typer.Option(...)`/`typer.Argument(...)` as a function-argument
default inline in a `commands/*/cli.py` controller — ruff's `B008` flags
this when the default expression involves a call (dict subscript, `Path`
`/`, f-string, etc.), and even where it doesn't get flagged it's
inconsistent with the rest of the codebase. Instead: in
`core/shared_options.py`, add `SomeOpt = Annotated[Type, typer.Option(help=...)]`
(metadata only — no default value inside the `typer.Option()` call, and no
`DEFAULT_*` constant in this file); if the default isn't a trivial literal,
add a separate `DEFAULT_SOME = ...` constant in `core/defines.py` instead,
next to whatever it's derived from (`LOCAL_INPUT_DIR`, `NOW`,
`REQUIRED_INPUT_FILES`, etc.). Reference both in the controller —
`SomeOpt` from `shared_options`, `DEFAULT_SOME` from `defines`:
`param: SomeOpt = DEFAULT_SOME`.
For a *required* option, skip the default entirely (`param: SomeOpt`, no
`=`) rather than using Typer's `...`-means-required idiom — a bare `...`
default type-checks against a non-Optional annotation just fine at runtime,
but mypy strict has no special case for it and will report a spurious
`Incompatible default` error; omitting the default avoids the problem
entirely, since Python requires no-default params to come before ones that
have a default anyway.

## Known architectural risk

The inter-stage contract is implicit (matching folder/filename conventions
across independently-edited files), not enforced by any shared config or
schema. Changing a default path or the filename format in one command's file
will not raise an error — it will silently desync from what the next stage
expects. If this pipeline is revisited, consider making the contract explicit
(e.g., a single source of truth for expected input/output filenames, or a
Jenkins-stage-to-stage explicit path handoff) rather than relying on cwd-based
convention.

Related, newer risk: every Workflow State / MS List field write introduced
for per-step Workflow State tracking (`update_list_item_fields` calls
throughout `download`, `build`, `upload`, `notify`, `publish`) is
deliberately best-effort — wrapped in a broad `except` that logs and
continues, so a metadata-write failure never turns an otherwise-successful
pipeline step into a hard failure. The trade-off is that these writes can
silently fail with no visible symptom beyond a log line: the MS List's
Workflow State can drift out of sync with what actually happened, and
nothing downstream checks for that. This isn't hypothetical — it's exactly
how `upload`'s output-link write-back stayed broken in production for a
while: the four link columns in `core/sharepoint_fields.py` were originally
SharePoint Hyperlink/Picture columns, which Graph's field-PATCH endpoint
silently 400s on regardless of field name or value format, and every
caller's best-effort `except` swallowed that into a log line with no other
symptom (see that module's docstring for the fix — they're plain Text
columns now). If any MS List column backing these fields is ever changed
again, watch for the same silent-failure shape.

## Linting/type-checking notes

- `pyproject.toml`'s `[tool.ruff.lint]` has an explicit
  `select = ["E", "F", "B", "I", "UP", "SIM", "S", "TRY", "DTZ", "PL", "N", "RUF"]`
  — bugbear, isort, pyupgrade, flake8-simplify, flake8-bandit, tryceratops,
  flake8-datetimez, pylint, pep8-naming, and Ruff's own rules, not just the
  bare E4/E7/E9/F defaults. `"tests/*"` is exempted from `S101` (bare
  `assert`) via `[tool.ruff.lint.per-file-ignores]`. Run
  `ruff check --show-settings <file>` if you need to check exactly what's
  enabled for a given file.
- `[tool.black] target-version = ["py313"]` is pinned explicitly rather than
  left to Black's auto-detection. With `requires-python = ">=3.13"`
  (unbounded) and no pinned target, Black infers the target version from
  that specifier as "3.13 or newer," which can include a Python version
  newer than the interpreter actually running Black — producing "Python
  3.13 cannot parse code formatted for Python 3.14" warnings even though
  nothing in the code needs 3.14.
- `[tool.mypy] strict = true` includes `no_implicit_reexport`: if module
  `A` does `from B import name` and module `C` does
  `from A import name`, mypy treats that as an error unless `A` explicitly
  re-exports `name` — either `__all__ = [..., "name"]` (the convention used
  in this codebase, e.g. `sharepoint.py` re-exporting `get_token_manager`
  from `token_manager.py`, `secret.py` re-exporting `SecretName` from
  `secret_name.py`) or `from B import name as name`. Locally-defined names
  (functions/classes written directly in `A`) are never subject to this —
  it only applies to names that are themselves just imports.
