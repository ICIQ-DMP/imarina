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

In general therms the core process of the application needs 2 inputs to get the result: A bulk of the A3 database in 
ICIQ, which contains the data of all
ICIQ personnel; and the last researcher upload to iMarina. Both inputs are provided as a Microsoft Excel spreadsheet.
The output is the next researcher upload to iMarina. This represents one of the particularity of this workflow, as the 
output of one execution will be the input of the next execution. 

The application is integrated with Microsoft Forms, Microsoft List, Microsoft Approvals, Microsoft Sharepoint and 
Microsoft OneDrive.

The full workflow, using the integrated services is going to be described in the next section:

### Preparation
The first thing is to ask for the bulk of the A3 database to HHRR. They will provide a file with that data.

The file must be uploaded to Sharepoint. Any location within the channel of Institutional Strengthening, under the 
Digitalization Sharepoint will work; but to keep an order we will be saving it into 
`_Projects/imarina-load-researchers/runtime/a3`. The name can be anything but to keep an order we will be using:
`{DATETIME}__listado_personal_A3.xlsx`. `DATETIME` will be in the format `YYYY-MM-DD_HH-mm-ss`. For example: 
`2025-03-12_12-00-00`. The date will be the data in which the a3 dump take was performed. If the hour is not specified, 
we will be using 12 AM (`12-00-00`). Providing this file is optional. If it is not provided, it will be used the last 
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


### Answering the request form
To start the workflow you must answer the form and provide optionally the link to the A3 database dump and the iMarina
file upload. 

When you end up clicking the submit button on the form, the answers are recorded into a Microsoft List with a unique ID.
The modification or creation of this element in the Microsoft List triggers the execution of a Power Automate workflow.
This Power Automate Workflow sends a request into a Jenkins server, providing the ID of the request to the service. 

This request into the Jenkins server triggers the execution of a workflow. This part is not exposed to the user.


### Jenkins workflow
###### Preparation (download)
The first part of the workflow is the preparation of the files used in the generation of the iMarina load file. 
As previously explained, we need an A3 database dump and a previous iMarina researcher load. We will also need the 
files that are needed for the translation. 

The files needed for the translations will be assumed to be at 
`_Projects/imarina-load-researchers/runtime/input`. All files in this location will be downloaded into `input/` folder.

The A3 database dump will be downloaded from the link of the Microsoft List if it is specified into `input/A3.xlsx`. If 
there is no link, the last upload from the A3 database will be selected from the corresponding Sharepoint folder 
`_Projects/imarina-load-researchers/runtime/a3` and put into `input/A3.xlsx`.

The iMarina load file will be downloaded from the link of the Microsoft List if it is specified into 
`input/iMarina.xlsx`. If there is no link, the last upload to iMarina will be selected from the corresponding 
Sharepoint folder `_Projects/imarina-load-researchers/runtime/published` and put into `input/iMarina.xlsx`.

###### Build
This is the core step of the workflow because it is the one that builds the output Excel.

The build step of the workflow will take `input/A3.xlsx`, `input/iMarina.xlsx` and the translation files will be assumed
to be at `input/`. This will be specified via arguments to the program. 

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
This step:
- Takes the latest file at `output/` with the name 
`{DATETIME}__icl_ag_personal_12539.xlsx` and uploads it into Sharepoint 
`_Projects/imarina-load-researchers/runtime/output`. 
- It generates the link to that file and updates the request 
of the list with the link to the output file. 
- Triggers the execution of a Power Automate workflow that notifies the requester of the success via triggering an 
approval request using Microsoft Approvals. The approval sends the link to the output file, informs of the success and
asks if the requester wants to publish that into iMarina servers. If the user says yes, an HTTP request is made against
a Jenkins server that executes the last `publish` step.

###### Publish
Publish step downloads the output of the supplied id and uploads it to the iMarina FTP server. Finishing the workflow. 






