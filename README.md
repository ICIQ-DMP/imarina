<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="[https://github.com/ICIQ-DMP/imarina](https://github.com/ICIQ-DMP/imarina)">
    <img src="https://raw.githubusercontent.com/ICIQ-DMP/ICIQ-DMP.github.io/refs/heads/master/assets/images/logo-ICIQ-horizontal-catalan.png" alt="Logo" width="all" height="all">
  </a>

<h3 align="center">iMarina-load</h3>

  <p align="center">
    Scripts to obtain A3 data, transform it into iMarina load format, and upload it to iMarina server using SFTP
    <br />
    <a href="https://iciq-dmp.github.io/_posts/iMarina/2025-07-07-iMarina-load.html"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ICIQ-DMP/imarina">View Demo</a>
    &middot;
    <a href="https://github.com/ICIQ-DMP/imarina/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/ICIQ-DMP/imarina/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

 
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#built-with">Built With</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li>
          <a href="#prerequisites">Prerequisites</a>
        </li>
        <li>
          <a href="#installation">Installation</a>
        </li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#run-program">Run program</a></li>
        <ul>
          <li><a href="#run-in-host">Run in host</a></li>
          <li><a href="#run-in-docker">Run in Docker</a></li>
        </ul>
      </ul>
    </li>
    <li>
      <a href="#testing">Testing</a>
      <ul>
        <li><a href="#prerequisites-1">Prerequisites</a></li>
        <li><a href="#execute-tests">Execute tests</a></li>
        <ul>
          <li><a href="#in-host">In host</a></li>
          <li><a href="#other-useful-testing-commands">Other useful testing commands</a></li>
          <li><a href="#in-docker-">In Docker 🐳</a></li>
          <li><a href="#in-cicd-automated-testing-github-actions">In CI/CD automated testing (GitHub actions)</a></li>
        </ul>
      </ul>
    </li>
    <li>
      <a href="#roadmap-issues">Roadmap (issues)</a>
    </li>
    <li>
      <a href="#contributing">Contributing</a>
    </li>
    <li>
      <a href="#top-contributors">Top contributors</a>
    </li>
    <li>
      <a href="#license">License</a>
    </li>
    <li>
      <a href="#contact">Contact</a>
    </li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built with

* [![Python][Python]][Python-url]
* [![Pytest][Pytest]][Pytest-url]
* [![Docker][Docker]][Docker-url]
* [![OneDriveLinux][OneDriveLinux]][OneDriveLinux-url]
* [![SharePoint][SharePoint]][SharePoint-url]
* [![Excel][Excel]][Excel-url]
* [![GitHubActions][GitHubActions]][GitHubActions-url]
* [![SFTP][SFTP]][SFTP-url]
* [![Alpine][Alpine]][Alpine-url]
* [![Git][Git]][Git-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>







<!-- GETTING STARTED -->
## Getting Started
Follow these steps to set up the project locally.

### Prerequisites

Install Python version 3.12.3 or above, `git` and other essentials for building the project. 

In Ubuntu is:

```shell
 sudo apt install python3.12-venv gcc build-essential git -y
```

### Installation

###### Clone repository
```shell
git clone https://github.com/ICIQ-DMP/iMarina-load.git
```


###### Initialize venv
```shell
cd iMarina
python3 -m venv venv
./venv/bin/pip install -r requirements.txt 
```

Install the requirements
```shell
./venv/bin/pip install --upgrade pip
```

```shell
./venv/bin/pip install -r requirements.txt
```

###### Obtaining translations
First you will need to obtain the spreadsheets with the translations. By default, they are read from the `input/` 
folder, but 
you can change the location of these expected files with the following arguments:
* `--imarina-input /path/to/iMarina.xlsx`
* `--a3-input /path/to/A3.xlsx`
* `--countries-dict /path/to/countries.xlsx`
* `--jobs-dict /app/input/Job_Descriptions.xlsx`

You can either download them manually from Sharepoint, or you can use the Dockerized OneDrive service to sync files 
from Sharepoint to your host computer automatically in the background.

To do so you should do the following:
```shell
cd services/onedrive
bash run.sh
# The program will display a link and ask you to authenticate and paste the answered URL into the terminal
```

After following the steps, OneDrive will be syncing the folder 
`Institutional Strengthening/_Projects/iMarina_load_automation/input` from Sharepoint into `services/onedrive/data`. Add 
or change the necessary arguments to read from this new source, instead of `input/`, so that data consumed by the 
program is always updated. 

You can leave OneDrive running so that the files are always in sync. 

There are two configuration options active in `services/onedrive/conf/config` to make OneDrive delete things that have 
been deleted in Sharepoint `cleanup_local_files = "true"` and to only do downloads, not uploads (one-way sync) 
`download_only = "true"`. You may remove these two options to change the behaviour from one-way sync to two-way sync.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Usage
### Run program
#### Run in host
To start the program execute this command:
```shell
./venv/bin/python src/main.py 
```


#### Run in Docker

Use the provided `Dockerfile` and `compose.yml` to build and run the iMarina-load service in a containerized 
environment.  

`Dockerfile` Builds a lightweight Python 3.12 Alpine image that installs dependencies and 
runs the main script with predefined input file paths.

`compose.yml` Defines a service that builds and runs the iMarina-load container, mounts input/output folders, 
and securely injects FTP credentials as secrets for automated data processing.

First, you will need to create a `.env` file at the root of the project with the `UID` and `GID` of the user on your 
host that looks like this:

```.env
UID=1015
GID=1015
```

We used 1015 as example, but you can create a `.env` with the correct values with:
```shell
cat <<EOF > .env
UID=${UID:-$(id -u)}
GID=${GID:-$(id -g)}
EOF
```

In any case, you need to pass the variables `UID` and `GID` to `docker compose` to make it work.  

To build the Docker image and run it you can use:
```shell
  docker compose up --build
```

Other useful commands:
##### Build Docker image
```shell
  sudo docker build . -t aleixmt/imarina-load --progress=plain
```

##### Access the container shell
```shell
  docker compose run --rm app sh
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Testing

### Prerequisites
Install the `requirements-dev.txt` to install the dependencies for the tests.
```shell
./venv/bin/pip install -r requirements-dev.txt
```


### Execute tests
#### In host
We have to be at the root of the project, otherwise we will get an error
```shell
cd ~/Desktop/iMarina-load
```

After that, we can use this to run all tests at the same time:
```shell
pytest -v
```

####  Other useful testing commands
* Display prints or logs during tests:
```shell
pytest -s -v
```

* Stop at the first fail in the test:
```shell
pytest -x
```

* Run specific tests for example (by name):
```shell
pytest -k "name"
```


#### In Docker 🐳 
Run the following command to build the test image and execute the tests against it:

```shell
docker compose -f compose.yml -f compose.test.yml up --build 
```


#### In CI/CD automated testing (GitHub actions)
Our project uses **GitHub Actions** to run the tests against every pushed commit to the `master` branch.

The workflow installs dependencies, runs all pytest tests, and builds the Docker image only if all tests pass.
The workflow is defined in `.github/workflows/docker.yml`


<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- ROADMAP for issues -->
## Roadmap (issues)

 
      

See the [open issues](https://github.com/ICIQ-DMP/iMarina-load/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>






<!-- CONTRIBUTING -->
## Contributing

Contributions are welcome and what make the open source community such an amazing place to learn, inspire, and create. 
Any contributions you make are **greatly appreciated**.

If you’d like to report a bug, request a feature, or propose an improvement, please follow these steps:

### Create an Issue

Create a new Issue [in here](https://github.com/ICIQ-DMP/iMarina-load/issues/new).

* Title: A short, descriptive summary of the issue.
* Description: Provide as much context as possible.
* For bugs: steps to reproduce, expected vs. actual behavior, environment (OS, Python version, etc.).
* For features: explain the motivation and the expected outcome.
* Screenshots or logs (if applicable).

The maintainers will review it and may ask for further clarification.

### Create a Pull Request

[Fork](https://github.com/ICIQ-DMP/iMarina-load/fork) the repository, implement the changes that you want on your fork 
and create a Pull Request in [here](https://github.com/ICIQ-DMP/iMarina-load/compare).

The maintainers will try to integrate it into the `master` branch.

<p align="right">(<a href="#readme-top">back to top</a>)</p>












### Top contributors:

<a href="https://github.com/AleixMT">
   <img src="https://avatars.githubusercontent.com/AleixMT" width="80px" alt="usuario"/>
</a>

<a href="https://github.com/MARIO31XD">
   <img src="https://avatars.githubusercontent.com/MARIO31XD" width="80px" alt="usuario"/>
</a>


<!-- LICENSE -->
## License

Distributed under the GNU GPL v3. See [LICENSE](https://github.com/ICIQ-DMP/iMarina-load/blob/master/LICENSE) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

* Mario Piqué - [mpique@iciq.es](mpique@iciq.es)
* Aleix Mariné - [amarine@iciq.es](amarine@iciq.es)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

 

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/ICIQ-DMP/imarina.svg?style=for-the-badge&color=purple
[contributors-url]: https://github.com/ICIQ-DMP/imarina/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ICIQ-DMP/imarina.svg?style=for-the-badge&color=orange
[forks-url]: https://github.com/ICIQ-DMP/imarina/forks
[forks-url]: https://img.shields.io/badge/Forks-blue?style=for-the-badge
[stars-shield]: https://img.shields.io/github/stars/ICIQ-DMP/imarina.svg?style=for-the-badge&color=yellow
[stars-url]: https://github.com/ICIQ-DMP/imarina/stargazers
[issues-shield]: https://img.shields.io/github/issues/ICIQ-DMP/imarina.svg?style=for-the-badge&color=brightgreen
[issues-url]: https://github.com/ICIQ-DMP/imarina/issues
[issues-url]: https://img.shields.io/badge/Issues-red?style=for-the-badge&logo=github&logoColor=white
[license-shield]: https://img.shields.io/github/license/ICIQ-DMP/imarina.svg?style=for-the-badge
[license-url]: https://github.com/ICIQ-DMP/imarina/blob/master/LICENSE

[license-shield]: https://img.shields.io/github/license/ICIQ-DMP/imarina.svg?style=for-the-badge&color=red
[license-url]:https://github.com/ICIQ-DMP/imarina/blob/master

[linkedin-shield]: https://img.shields.io/badge/LinkedIn-blue?style=for-the-badge&logo=linkedin&logoColor=white
[linkedin-url]: https://es.linkedin.com/company/iciq


<!-- Build with section -->
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/

[Pytest]: https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white
[Pytest-url]: https://docs.pytest.org/

[Docker]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/

[OneDriveLinux]: https://img.shields.io/badge/OneDrive%20for%20Linux-0078D4?style=for-the-badge&logo=onedrive&logoColor=white
[OneDriveLinux-url]: https://github.com/abraunegg/onedrive

[SharePoint]: https://img.shields.io/badge/SharePoint-0078D4?style=for-the-badge&logo=sharepoint&logoColor=white
[SharePoint-url]: https://www.microsoft.com/sharepoint

[Excel]: https://img.shields.io/badge/Microsoft%20Excel-217346?style=for-the-badge&logo=excel&logoColor=white
[Excel-url]: https://www.microsoft.com/microsoft-365/excel

[GitHubActions]: https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white
[GitHubActions-url]: https://github.com/features/actions

[SFTP]: https://img.shields.io/badge/SFTP-3A3A3A?style=for-the-badge&logo=ssh&logoColor=white
[SFTP-url]: https://datatracker.ietf.org/doc/html/draft-ietf-secsh-filexfer

[Alpine]: https://img.shields.io/badge/Alpine%20Linux-0D597F?style=for-the-badge&logo=alpine-linux&logoColor=white
[Alpine-url]: https://www.alpinelinux.org/

[Git]: https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white
[Git-url]: https://git-scm.com/
