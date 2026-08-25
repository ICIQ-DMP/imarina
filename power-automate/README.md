# Power Automate flows — source control

This project's workflow depends on three Power Automate flows living in the
ICIQ tenant (Microsoft Forms / Microsoft List / SharePoint / Jenkins glue —
see STEPS.md). Today they only exist as live flow definitions edited through
the browser designer, with no history, no diff, and no record of *why* a
given change was made. This directory is where their definitions get
version-controlled instead, using Power Platform's own export/unpack
tooling.

**Nothing in this directory is a live sync of the real flows yet** — see
"Current status" at the bottom. The rest of this file documents the process
so the first real export follows a consistent convention from day one.

## Why this shape, not something simpler

Power Automate flows aren't files — they're JSON definitions stored in a
Power Platform environment (optionally inside a Dataverse "Solution"). The
Microsoft-supported way to get them into a plain-text, diffable, git-friendly
form is:

1. Put the flow(s) in a **Solution** (a container Power Platform already
   understands for packaging/moving flows between environments).
2. Export the Solution as an unmanaged `.zip`.
3. Unpack that zip into individual JSON/XML files with the **Power Platform
   CLI** (`pac`) — this is what makes it diffable; the raw exported zip isn't.
4. Commit the unpacked files. Review changes the normal way (PR diff).
5. To push an edit back to the tenant: pack the files back into a zip and
   import the Solution.

This repo intentionally does **not** wire this into automated CI (no
GitHub Action / Jenkins stage that auto-imports on merge). With three
small, infrequently-changed flows in a single environment, that's more
pipeline than the problem needs — the value here is the diffable history and
PR review, not push-button deploy. Re-evaluate this if the number of flows or
environments grows.

## One-time setup

Install the Power Platform CLI (see
[Microsoft's install docs](https://learn.microsoft.com/power-platform/developer/cli/introduction)
— it's a dotnet tool or a standalone installer, not a Python package, so it's
independent of this project's own `venv`):

```shell
pac auth create --url https://<your-tenant>.crm.dynamics.com
```

(Use the Dataverse/Power Platform environment URL for the environment the
ICIQ flows actually live in — ask whoever administers the Power Platform
tenant if you don't have it.)

## Exporting a flow into this repo (first time, or after editing in the browser)

1. In [make.powerapps.com](https://make.powerapps.com), if the flow isn't
   already in a Solution, add it to one (create a new Solution if needed,
   e.g. `imarinaLoadResearchersWorkflow`).
2. Export that Solution as **unmanaged**, download the zip.
3. Unpack it into this directory:
   ```shell
   pac solution unpack --zipfile /path/to/downloaded/Solution.zip --folder power-automate/<SolutionName> --packagetype Unmanaged
   ```
4. Review the diff (`git diff power-automate/`), commit with a message
   explaining *what changed and why* — the flow's own JSON diff won't tell a
   future reader that, the same way a code diff alone doesn't explain intent.

## Importing a reviewed change back into the tenant

```shell
pac solution pack --zipfile /tmp/Solution.zip --folder power-automate/<SolutionName> --packagetype Unmanaged
pac solution import --path /tmp/Solution.zip
```

Re-export afterward (previous section) so the repo reflects any
environment-side ID/version bump the import produces.

## The three flows (STEPS.md)

These are documented here as a plain-language spec of what each flow needs
to do — not a substitute for the actual exported definition, which will live
under a per-Solution subfolder once someone with tenant access does the
first real export (see "Current status" below).

### 1. Input file name validation

- **STEPS.md section**: "Validating the upload of input files"
- **Trigger**: a file is created/uploaded in any of
  `_Projects/imarina-load-researchers/runtime/imarina`,
  `.../runtime/input`, or `.../runtime/a3`.
- **Action**: check the uploaded file's name against the naming
  specification in STEPS.md's "Preparation" and "Build" sections (the
  `{DATETIME}__listado_personal_A3.xlsx` / `{DATETIME}__icl_ag_personal_12539.xlsx`
  patterns, or the fixed translation-dictionary filenames). 

### 2. Request intake

- **STEPS.md section**: "Answering the request form"
- **Trigger**: an item is created or modified in the MS List backing the
  request form (see `core/sharepoint_fields.py`'s field-name docstring for
  the exact field names this flow reads/writes).
- **Action**: POST to the main Jenkins job's `buildWithParameters` endpoint
  (see the main `Jenkinsfile`), passing the list item's `ID` field as the
  `ID` build parameter. This is what starts `download` → `build` → `upload`.

### 3. Upload review → approval → publish trigger

- **STEPS.md section**: "Upload" (and "Publish")
- **Trigger**: the "iMarina Excel output link" field is updated on an MS
  List item (written by `upload --id ...` on success — see
  `commands/upload/cli.py`).
- **Action**:
  - Start a Microsoft Approval, assigned to the item's `Created By` (the
    requester), with the output link and a success message.
  - **On approval**: POST to the *second* Jenkins job's
    `buildWithParameters` endpoint (`Jenkinsfile.publish` — see CLAUDE.md's
    "Publish pipeline" section for the job configuration and trigger URL),
    passing the same `ID`.
  - **On rejection**: update the item's "Workflow State" field to
    "Not published" (`core/sharepoint_fields.py`'s `WorkflowState.NOT_PUBLISHED`)
    — no Jenkins job runs in this case.
  - **On timeout** (if Microsoft Approvals is configured with one): STEPS.md
    flags this as still undecided — pick a Workflow State to land on
    (probably also "Not published") before implementing this branch.

