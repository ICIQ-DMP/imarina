so this is a Sharepoint native app, which means that uses common services from Sharepoint to be a fully featured
application with interfaces, database, notifications... The 
advantage of having this type of application is that everything is integrated into Sharepoint: user interfaces are 
already built and system 
administration is minimal or depends on IT or on Microsoft engineers. The application itself is actually a workflow, 
which means that the way main usage
case is just one and its usage needs a concrete sequence of steps. 

The software itself is a Python package that can be used uncoupled from Sharepoint ecosystem but is easier to interact 
with by using it in conjunction with Sharepoint. This is specially true for non-technical users, who would need to 
understand how to run a Python application to actually execute the workflow and obtain the needed result. 

The goal of the application is to build a spreadsheet without user interaction in the process. This spreadsheet feeds
researcher data into the 
iMarina system, which is a type of CRIS (Current Research Information System). A CRIS is a software used to publish 
the
research that is being performed in a research entity such as ICIQ (Catalan Institute of Chemistry Research). At ICIQ, 
we use 
iMarina
as CRIS, so we can know which research projects are active within ICIQ using iMarina. This application in particular
serves the goal of updating the researchers that are currently working at ICIQ. Since research projects are usually 
associated to researchers, this is a crucial part of keeping the data of a CRIS updated. 

In general terms the core process of the application needs 2 inputs to get the result: A bulk of the A3 database in 
ICIQ, which contains the data of all
ICIQ personnel; and the last researcher upload to iMarina. Both inputs are provided as a Microsoft Excel spreadsheet.
The output is the next researcher upload to iMarina. This represents one of the particularities of this workflow, as the 
output of one execution will be the input of the next execution. 

Knowing which is the last of a group of files will always be deduced from the name of the file, as it will contain the 
datetime at the beginning of the file name, unless otherwise stated. 

The application is integrated with Microsoft Forms, Microsoft List, Microsoft Approvals, Microsoft Sharepoint and 
Microsoft OneDrive.

The full workflow, using the integrated services is going to be described in the next section:


### GDPR implications
This workflow moves personal data of ICIQ personnel (the A3 database dump, and the iMarina upload derived from it) 
between systems with no human review of individual records along the way, so its design has to satisfy GDPR's purpose 
limitation, data minimization and storage limitation principles, not just describe who is allowed to click the button.

**Purpose limitation.** The sole purpose of this workflow is to keep the researcher list in iMarina in sync with 
ICIQ's HR records, so ICIQ can report which research staff are currently active. The A3 dump and the resulting 
iMarina upload must not be used, forwarded or retained for any other purpose by anyone who has access to the 
`runtime/*` SharePoint folders.

**Data minimization / access restriction.** Triggering the workflow is restricted to a small, named set of people 
with a legitimate need to do so:
- Dr. Sonia Sayalero, responsible for Institutional Strengthening operations at ICIQ and the Severo Ochoa 
  administrator.
- Aleix Mariné-Tena, the data steward of ICIQ who designed, implemented and tests this workflow.
- Eventually, an apprentice, in case this project is assigned to them.

The A3 dumps themselves are provided manually, at most once a month, by Human Resources of ICIQ — specifically Mara 
Cruz, the head of Human Resources — who is the only authorized source of the raw HR extract entering the pipeline.

Restricting *who may trigger the workflow* only has GDPR value if it is backed by matching SharePoint item-level 
permissions on the `_Projects/imarina-load-researchers/runtime/*` folders and on the Microsoft List and Microsoft 
Form themselves: restricting the form's submit button is meaningless if the underlying files remain readable by a 
broader SharePoint audience than the people named above.

**Storage limitation.** Because the "use the last file" fallback (see above) depends on every previous A3 dump and 
iMarina upload remaining in `runtime/a3` and `runtime/published` indefinitely, this design currently has no 
retention or purge policy for historical personal-data files, which conflicts with the storage limitation principle. 
A retention period should be defined, along with a decision on whether older dumps can be deleted without breaking 
the "pick the latest" mechanism.


### Microsoft List field names
- iMarina Excel published link: Link to the Excel file that has been published. Filled by the `publish` command if the 
FTP publishing is successful. 
- iMarina Excel output link: Link to the Excel file that has been generated from the input. It will be the same as the 
published file. Filled by the `upload` 
command with the Excel generated with the `build` command. 
- iMarina Excel input link: Link to the iMarina Excel file that has been used as input. Filled by the form or the 
`download` 
command with the latest iMarina published file. 
- A3 Excel input link: Link to the A3 Excel file that has been used as input. Filled by the form or the `download` 
command with the latest A3 dump. 
- Workflow State: State of the workflow. Updated by the Power Automate workflows and with the different commands 
of the process. Possible values: "New", "Preparing", "Building", "Uploading", "Requested review", "Not published",
"Publishing", "Published" and "Error".
- ID: Unique identifier for this request. Filled by answering the form automatically. 
- Created By: Field of type person that contains who requested this iMarina researcher load. Filled by answering the 
form automatically. 



### Preparation
The first thing is to ask for the bulk of the A3 database to HHRR. They will provide a file with that data.

The file must be uploaded to Sharepoint. Any location within the channel of Institutional Strengthening, under the 
Digitalization Sharepoint will work; but to keep an order we will be saving it into 
`_Projects/imarina-load-researchers/runtime/a3`. The name can be anything but to keep an order we will be using:
`{DATETIME}__listado_personal_A3.xlsx`. `DATETIME` will be in the format `YYYY-MM-DD_HH-mm-ss`. For example: 
`2025-03-12_12-00-00`. This date will be the date in which the a3 dump was performed. If the hour is not specified, 
we will be using 12 AM (`12-00-00`), but it is not relevant for the algorithm because if an hour is not provided it 
means that has been obtained manually. We do not need that much precision, as we will not be getting more than one A3
per month.
Providing this file is optional. If it is not provided, it will be used the last 
A3 database dump. 

The second thing should be getting the file with the last upload into iMarina. This is optional. If no file is provided 
with this information, the last upload to iMarina will be used. The uploads to iMarina will be located at 
`_Projects/imarina-load-researchers/runtime/published`. The name will be 
`2026-05-01_12-00-00__icl_ag_personal_12539.xlsx`. The date at the beginning of the file will follow the same pattern
as the `DATETIME` from the A3 database dump. If the file is provided, it must be uploaded to Sharepoint. It can be 
uploaded to any location within the channel of Institutional Strengthening, but to keep an order we will be uploading it
into `_Projects/imarina-load-researchers/runtime/imarina`. The file name can be anything, but to keep an order it will
be the same as in the uploads. 

If you are providing the A3 database dump you must generate and copy a direct link to the file. If you are providing an 
iMarina file you must generate and copy a direct link to it. 


### Validating the upload of input files
When uploading files into `_Projects/imarina-load-researchers/runtime/imarina`,  
`_Projects/imarina-load-researchers/runtime/input` and 
`_Projects/imarina-load-researchers/runtime/a3` a Microsoft Power Automate is triggered to validate the names of the 
files there. It specifically checks that the names conform to the specification of names that appear in the "Preparation" and 
"Build"
sections of this document.

### Answering the request form
To start the workflow you must answer the form and provide optionally the link to the A3 database dump and the iMarina
file upload. 

When you end up clicking the submit button on the form, the answers are recorded into a Microsoft List with a unique ID.
The "Workflow State" field of the new item defaults to "New" on creation.
The modification or creation of this element in the Microsoft List triggers the execution of a Power Automate workflow.
This Power Automate Workflow sends a request into a Jenkins server, providing the ID of the request to the service. 

This request into the Jenkins server triggers the execution of a workflow. This part is not exposed to the user.


### Jenkins workflow
###### Preparation (download)
The first part of the workflow is the preparation of the files used in the generation of the iMarina load file. 
As previously explained, we need an A3 database dump and a previous iMarina researcher load. We will also need the 
files that are needed for the translation. 

At the start of this step, the field "Workflow State" of the request is updated to "Preparing".

The files needed for the translations will be assumed to be at 
`_Projects/imarina-load-researchers/runtime/input`. All files in this location will be downloaded into `input/` folder.

The A3 database dump will be downloaded from the link of the Microsoft List if it is specified into `input/A3.xlsx`. If 
there is no link, the last upload from the A3 database will be selected from the corresponding Sharepoint folder 
`_Projects/imarina-load-researchers/runtime/a3` and put into `input/A3.xlsx`. If this happens, a link will be generated 
to that file and used to update the field "A3 Excel input link" of the request with the supplied ID. Unlike the iMarina 
case, the file does not need to be copied: `_Projects/imarina-load-researchers/runtime/a3` is already both where the A3 
dump is manually uploaded (see "Preparation") and where this fallback selects the last dump from, so the file is already 
in the folder that is the source of truth.

The iMarina load file will be downloaded from the link of the Microsoft List if it is specified into 
`input/iMarina.xlsx`. If there is no link, the last upload to iMarina will be selected from the corresponding 
Sharepoint folder `_Projects/imarina-load-researchers/runtime/published` and put into `input/iMarina.xlsx`. If this 
happens, this file will be copied into `_Projects/imarina-load-researchers/runtime/imarina`, a link generated into the 
file and used to update the field "iMarina Excel input link" of the request with the supplied ID. The file is copied 
and not linked, because the source of truth that the commands use are the files present in the folders. If we link a 
file in `_Projects/imarina-load-researchers/runtime/published` as the iMarina input file, we can not use a 
mechanism such as OneDrive for Linux. Moreover, to get the latest published file we would need to loop through the list
and check the last item with a filled "iMarina Excel published link". 


###### Build
This is the core step of the workflow because it is the one that builds the output Excel.

The build step of the workflow will take `input/A3.xlsx`, `input/iMarina.xlsx` and the translation files will be assumed
to be at `input/`. This will be specified via arguments to the program. 

Like `download`, `upload`, `notify` and `publish`, `build` accepts an ID argument. Unlike those commands, this ID is 
used for nothing other than updating the "Workflow State" field: it plays no part in resolving input/output files, 
which are still governed entirely by the arguments described below and by `input/`/`output/` conventions. At the 
start of this step, if an ID is supplied, the field "Workflow State" of the request is updated to "Building".

It must be known (for developers) that the 
defaults of these options are:
- The last a3 dump (from the datetime at the filename) at `_Projects/imarina-load-researchers/runtime/a3` with the name 
`{DATETIME}__listado_personal_A3.xlsx` for the a3 dump. 
- The last iMarina upload (from the datetime at the filename) at `_Projects/imarina-load-researchers/runtime/published`
with the name 
`2026-05-01_12-00-00__icl_ag_personal_12539.xlsx` for the iMarina upload. 
- The translations located at `_Projects/imarina-load-researchers/runtime/input`. The assumed names will be 
`Pais nacimiento _ [A3] to País de Nacimiento [iMarina].xlsx`, 
`Puesto de trabajo [A3] to Categoría Investigadora Docente [iMarina].xlsx`,
`Puesto de trabajo [A3] to Web personal [iMarina].xlsx`,
`Grupo Unidad [A3] to Entidad (Nivel 1) [iMarina].xlsx`,
`Entidad (Nivel 1) [iMarina] to Tipo de Entidad [iMarina].xlsx`,
`Puesto de trabajo [A3] to Entidad (Nivel 1) [iMarina].xlsx` and
`Sexo [A3] to Sexo [iMarina].xlsx`.

This allows to skip the `download` command and use OneDrive for Linux to keep the files updated, which is useful while 
we are developing the application.

The algorithm will build the output Excel file and put it into `output/` with the name 
`{DATETIME}__icl_ag_personal_12539.xlsx`. 


###### Upload
At the start of this step, if an ID is supplied, the field "Workflow State" of the request is updated to "Uploading".

This step:
- Takes the latest file at `output/` with the name 
`{DATETIME}__icl_ag_personal_12539.xlsx` and uploads it into Sharepoint 
`_Projects/imarina-load-researchers/runtime/output` or the specified file via argument.
- If an ID is supplied it generates the link to the uploaded file and updates the field "iMarina Excel output link".
- Updating the file link in the Microsoft List triggers the execution of a Power Automate workflow that notifies the 
requester of the 
success via triggering an 
approval request using Microsoft Approvals. Once this approval request has been sent, the field "Workflow State" is 
updated to "Requested review". The approval sends the link to the output file, informs of the success and
asks if the requester wants to publish that into iMarina servers. If the user says yes, an HTTP request is made against
a Jenkins server that executes the last `publish` step.

The approval will sit there indefinitely until it is accepted or rejected. Microsoft Approvals may define a timeout for
requests though. If the requester rejects the approval, the field "Workflow State" is updated to "Not published" and 
the workflow ends. If the requester accepts, the `publish` step described below is triggered.



###### Notify 
Notify is executed after upload or publish, or if an error happens in any other previous step of either the request
pipeline (download/build/upload) or the publish pipeline. It receives an ID where notify will 
read the information to compose and email the requester. If the ID is not supplied, individual arguments can be 
supplied to provide the information needed
to compose the email:
- Email of the email destinatary (requester).
- A3 Excel input link
- iMarina Excel input link
- result of the operation (success, published, or error).
- iMarina Excel output link. Only needed if the result is success.

The wording of the email differs by result: "success" tells the requester their file is ready for review at a
SharePoint link (the outcome of `upload`); "published" tells them their file has been published to iMarina (the
outcome of `publish`) — these are two different, non-interchangeable messages, since a requester whose file was
already published should not be told to go review it.

If notify is called with a failure status and an ID, it also updates the field "Workflow State" to "Error". This is 
the single place this is done, rather than in each of `download`, `build` and `upload`, since notify is already the 
common failure handler called from every step's error path.


###### Publish
Publish step downloads the output of the supplied id and uploads it to the iMarina FTP server. Finishing the workflow.

At the start of this step, if an ID is supplied, the field "Workflow State" of the request is updated to "Publishing".

Publish receives ID which will trigger the download of the corresponding output file from the list row of
that ID for its upload. Instead, publish can receive a valid output file, which will also be uploaded to the iMarina 
FTP server. Since publishing without keeping a record can cause problems, a warning will be shown in this case. Since 
there is no ID in this case, there is no request whose "Workflow State" can be updated either.

If the file is successfully published, the file will be uploaded to 
`_Projects/imarina-load-researchers/runtime/published` and a link will be generated to that file, updating the field 
"iMarina Excel published link" of the corresponding request with the supplied ID. If an ID was supplied, the field 
"Workflow State" is also updated to "Published".

This step is only triggered after a human review, which acts as sanity check. 

This step is triggered by its own, separate Jenkins job — not the one running download/build/upload — started by the
HTTP request described in the "Upload" section above. After it finishes, notify is called with the supplied ID:
"published" on success, "error" on failure, so the requester who approved the publish learns whether it actually
went through.






