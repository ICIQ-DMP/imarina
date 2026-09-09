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
  <a href="[https://github.com/ICIQ-DMP/imarina-load-researchers](https://github.com/ICIQ-DMP/imarina-load-researchers)">
    <img src="https://raw.githubusercontent.com/ICIQ-DMP/ICIQ-DMP.github.io/refs/heads/master/assets/images/logo-ICIQ-horizontal-catalan.png" alt="Logo" width="all" height="all">
  </a>

<h3 align="center">imarina-load-researchers</h3>

  <p align="center">
    Scripts to obtain A3 data, transform it into iMarina load format, and upload it to iMarina server using SFTP
    <br />
    <a href="https://iciq-dmp.github.io/_posts/iMarina/2025-07-07-imarina.html"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ICIQ-DMP/imarina-load-researchers">View Demo</a>
    &middot;
    <a href="https://github.com/ICIQ-DMP/imarina-load-researchers/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/ICIQ-DMP/imarina-load-researchers/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
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

Install Python version 3.13 or above, `git` and other essentials for building the project.

In Ubuntu is:

```shell
 sudo apt install python3.13-venv gcc build-essential git -y
```

### Installation

###### Clone repository
```shell
git clone https://github.com/ICIQ-DMP/imarina-load-researchers.git
```


###### Initialize venv
```shell
cd imarina-load-researchers
make install
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
<!-- TODO: remove specific data from share point
After following the steps, OneDrive will be syncing the folder `_Projects/imarina-load-researchers/input`-->
`_Projects/imarina-load-researchers/input` from Sharepoint into `services/onedrive/data`. Add 
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
`make install` installs the `imarina-load-researchers` console script into the virtualenv. To see the available subcommands:
```shell
./venv/bin/imarina-load-researchers --help
```

Equivalently, you can invoke it as a module:
```shell
./venv/bin/python -m imarina_load_researchers --help
```

The automated pipeline is `download` → `build` → `upload` (see the [Jenkinsfile](Jenkinsfile) for the exact
invocation used in CI); `publish` is a separate, manually-triggered step. `build`, `upload` and `publish` all
accept an optional `--id <OperationID>` so they can keep the originating request's status in sync as the
pipeline progresses; it's not required for a standalone/local run. For example, to run the build step alone:
```shell
./venv/bin/imarina-load-researchers build
```

###### Example of a full execution
```shell
REQUEST=66
./venv/bin/imarina-load-researchers download $REQUEST && ./venv/bin/imarina-load-researchers build --id $REQUEST && ./venv/bin/imarina-load-researchers upload --id $REQUEST
```

#### Run in Docker

Use the provided `Dockerfile` and `compose.yml` to build and run the imarina-load-researchers service in a containerized 
environment.  

`Dockerfile` Builds a lightweight Python 3.14 Alpine image that installs dependencies and runs the `imarina-load-researchers`
CLI as its entrypoint (`compose.yml` passes the subcommand to run, e.g. `command: "build"`).

`compose.yml` Defines a service that builds and runs the imarina-load-researchers container, mounts input/output folders, 
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
  sudo docker build . -t aleixmt/imarina-load-researchers --progress=plain
```

##### Access the container shell
```shell
  docker compose run --rm app sh
```

#####
Run production:
```shell
docker compose -f compose.prod.yml up --build --remove-orphans
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Testing

### Prerequisites
Install the dev dependencies declared in `pyproject.toml` (`[project.optional-dependencies].dev`: black, pytest,
mypy, ruff, pre-commit):
```shell
make dev
```


### Execute tests
#### In host
<!-- convert into makefile target -->
We have to be at the root of the project, otherwise we will get an error
```shell
cd ~/Desktop/imarina-load-researchers
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


## Deploy to production

Generate keys:
```shell
ssh-keygen -t ed25519 -C "jenkins@imarina-load-researchers-agent" -N "" -f services/jenkins_agent_keys/id_rsa
```

Copy the public key into .env.

Enter into jenkins, create or modify agent, and select 

```shell
docker compose -f compose.prod.yml up --build --remove-orphans 
```


<!-- ROADMAP for issues -->
## Roadmap (issues)

 
      

See the [open issues](https://github.com/ICIQ-DMP/imarina-load-researchers/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>






<!-- CONTRIBUTING -->
## Contributing

Contributions are welcome and what make the open source community such an amazing place to learn, inspire, and create. 
Any contributions you make are **greatly appreciated**.

If you’d like to report a bug, request a feature, or propose an improvement, please follow these steps:

### Create an Issue

Create a new Issue [in here](https://github.com/ICIQ-DMP/imarina-load-researchers/issues/new).

* Title: A short, descriptive summary of the issue.
* Description: Provide as much context as possible.
* For bugs: steps to reproduce, expected vs. actual behavior, environment (OS, Python version, etc.).
* For features: explain the motivation and the expected outcome.
* Screenshots or logs (if applicable).

The maintainers will review it and may ask for further clarification.

### Create a Pull Request

[Fork](https://github.com/ICIQ-DMP/imarina-load-researchers/fork) the repository, implement the changes that you want on your fork 
and create a Pull Request in [here](https://github.com/ICIQ-DMP/imarina-load-researchers/compare).

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

Distributed under the GNU GPL v3. See [LICENSE](https://github.com/ICIQ-DMP/imarina-load-researchers/blob/master/LICENSE) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

* Mario Piqué - [mpique@iciq.es](mpique@iciq.es)
* Aleix Mariné - [amarine@iciq.es](amarine@iciq.es)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

 

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/ICIQ-DMP/imarina-load-researchers.svg?style=for-the-badge&color=purple
[contributors-url]: https://github.com/ICIQ-DMP/imarina-load-researchers/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ICIQ-DMP/imarina-load-researchers.svg?style=for-the-badge&color=orange
[forks-url]: https://github.com/ICIQ-DMP/imarina-load-researchers/forks
[stars-shield]: https://img.shields.io/github/stars/ICIQ-DMP/imarina-load-researchers.svg?style=for-the-badge&color=yellow
[stars-url]: https://github.com/ICIQ-DMP/imarina-load-researchers/stargazers
[issues-shield]: https://img.shields.io/github/issues/ICIQ-DMP/imarina-load-researchers.svg?style=for-the-badge&color=brightgreen
[issues-url]: https://github.com/ICIQ-DMP/imarina-load-researchers/issues
[license-shield]: https://img.shields.io/github/license/ICIQ-DMP/imarina-load-researchers.svg?style=for-the-badge&color=red
[license-url]:https://github.com/ICIQ-DMP/imarina-load-researchers/blob/master/LICENSE

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
