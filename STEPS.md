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
Digitalization Sharepoint will work. 


