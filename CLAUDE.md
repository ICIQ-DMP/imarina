# imarina — architecture notes

## What this does

Produces the next iMarina iPublic load spreadsheet from two inputs: an A3 database
dump (employee data snapshot, A3 format) and the previous iMarina iPublic load
(iMarina format). `build` merges/transforms these (plus several static dictionary
files) into the next iMarina-format spreadsheet, which is later pushed to the
iMarina server over FTP (`publish`).

## CLI commands and the pipeline

Five subcommands, wired in `src/imarina/cli.py`: `download`, `build`, `upload`,
`publish`, `notify`. They do **not** pass data to each other directly — there is
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
imarina download <OperationID>            # positional int arg, not --id; populates ./input
imarina build                              # reads ./input, writes ./output
imarina upload                             # autodetects latest file in ./output, pushes to SharePoint for review
imarina notify --id <OperationID> --status success   # or --status error from a catch block
```

`publish` (FTP → iMarina server) is **deliberately not** part of the automated
pipeline — it's a manual, human-triggered step run after someone reviews the
SharePoint copy that `upload` produced.

### `download` — two independent mechanisms feeding one folder

`commands/download/cli.py`. Target folder defaults to `./input` (`-d/--directory`
override via `DirectoryOpt`, `core/shared_options.py`). Two unrelated things
happen, both writing flat into that same folder:

1. `download_files_in_folder_from_sharepoint()` (`core/sharepoint.py`) lists
   **every** `.xlsx` file in a fixed SharePoint library folder
   (`SHAREPOINT_INPUT_FOLDER`, `core/defines.py` —
   `Institutional Strengthening/_Projects/iMarina_load_automation/input`) and
   downloads all of them as-is. This is how the 6 static "dictionary" files
   arrive (`countries.xlsx`, `Job_Descriptions.xlsx`, `Personal_web.xlsx`,
   `unit_group.xlsx`, `unit_type.xlsx`, `job_description_entity.xlsx`) — they're
   maintained by hand on SharePoint and just bulk-synced down.
2. `get_parameters_list(operation_id)` looks up an MS List item by
   `id_element` (Operation ID — a required positional int argument, not a
   `--id` flag, passed in from the Jenkins job parameter) and reads two
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

### `notify` — build-result email to the requester

`commands/notify/cli.py`, backed by `core/mail.py` (Graph API access-token/
creator-lookup helpers, SMTP send, email-body templates — no CLI concerns).
Called from the Jenkinsfile's `iMarina upload` stage, once per branch of a
try/catch around `upload`: `--status success` after `upload` succeeds,
`--status error` from the `catch` block. `--id` is the same Operation ID
passed to `download`, used to look up the MS List item's creator (so the
email goes to whoever triggered the run) — required, no default.
`--sharepoint-path` defaults to `DEFAULT_TARGET_FOLDER` (`core/defines.py`),
the same SharePoint review folder `upload` pushes to, and is only used to
word the success email body. Prior to this
command existing, Jenkins ran `core/mail.py` directly as a standalone
script (`python3 src/imarina/core/mail.py --id ... --status ...`); it's now
invoked like any other subcommand (`imarina notify --id ... --status ...`),
so it goes through `cli_global_callback` for logging setup like the rest of
the app instead of needing its own `configure_logging_from_settings()` call.

## Key files for this pipeline

- `src/imarina/cli.py` — command registration only
- `src/imarina/core/defines.py` — shared constants: `PROJECT_DIR` (=cwd),
  `INPUT_DIR`/`OUTPUT_DIR`, filename prefix/suffix/datetime format used to
  round-trip the "latest file" between stages, `MADRID_TZ` (see Dates
  below), and every CLI option's `DEFAULT_*` value. This is the single
  source of truth for `PROJECT_DIR` — don't recompute a project root
  elsewhere (e.g. by walking up from `__file__`); import it from here.
- `src/imarina/core/sharepoint.py` — all Graph API calls (download, upload,
  MS List lookup)
- `src/imarina/core/ftp.py` — the `publish` FTP push
- `src/imarina/core/shared_options.py` — every Typer `Option`/`Argument`
  annotation used by any command — metadata (help text, flags) only, no
  default values. Controller functions in `commands/*/cli.py` import the
  `*Opt` type from here and the matching `DEFAULT_*` constant from
  `core/defines.py` (`param: SomeOpt = DEFAULT_SOME`) rather than calling
  `typer.Option(...)` inline in the signature — see "Adding a new CLI
  option" below.
- `src/imarina/core/secret.py`, `secret_name.py`, `vault.py` — see Secrets
  below.
- `Jenkinsfile` — the authoritative description of the automated portion of
  the pipeline (download → build → upload → notify); publish is manual.
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
next to whatever it's derived from (`INPUT_DIR`, `NOW`,
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

## Linting/type-checking notes

- `pyproject.toml`'s `[tool.ruff]` has no explicit `select`/`ignore`, but
  `ruff check` here still enforces a broad rule set (bugbear, flake8-blind-
  except, flake8-datetimez, flake8-simplify, tryceratops, pep8-naming,
  pylint, flake8-bandit, pyupgrade, RUF, ...) — not just the bare
  E4/E7/E9/F ruff defaults you'd expect from an empty config. Don't assume
  a rule category is off just because it isn't listed in `pyproject.toml`;
  run `ruff check --show-settings <file>` to see what's actually enabled.
- `[tool.black] target-version = ["py314"]` is pinned explicitly rather than
  left to Black's auto-detection. With `requires-python = ">=3.14"`
  (unbounded) and no pinned target, Black infers the target version from
  that specifier as "3.14 or newer," which can include a Python version
  newer than the interpreter actually running Black — producing "Python
  3.14 cannot parse code formatted for Python 3.15" warnings even though
  nothing in the code needs 3.15.
- `[tool.mypy] strict = true` includes `no_implicit_reexport`: if module
  `A` does `from B import name` and module `C` does
  `from A import name`, mypy treats that as an error unless `A` explicitly
  re-exports `name` — either `__all__ = [..., "name"]` (the convention used
  in this codebase, e.g. `sharepoint.py` re-exporting `get_token_manager`
  from `token_manager.py`, `secret.py` re-exporting `SecretName` from
  `secret_name.py`) or `from B import name as name`. Locally-defined names
  (functions/classes written directly in `A`) are never subject to this —
  it only applies to names that are themselves just imports.
