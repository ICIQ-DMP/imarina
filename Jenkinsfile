pipeline {
    agent {
        label 'agent jenkins'
    }
    options {
         disableConcurrentBuilds() // one execution only
    }
    parameters {
         string(name: 'ID', defaultValue: '' , description: 'ID operation in iMarina')
    }

    // environment variables
    environment {
         PYTHON_PATH = "/usr/bin/python3"
         IMARINA_CMD = "venv/bin/python3 -m imarina"
         OPERATION_ID = "${params.ID}"
         TENANT_ID = credentials('TENANT_ID')
         CLIENT_ID = credentials('CLIENT_ID')
         DRIVE_ID = credentials('DRIVE_ID')
         CLIENT_SECRET = credentials('CLIENT_SECRET')
         FTP_PASSWORD = credentials('FTP_PASSWORD')

    }

    stages {
        // Python venv and dependencies
        stage('Prepare Python environment and dependencies') {
        steps {
           echo "Creating virtual environment and update dependencies..."
           sh"""
                $PYTHON_PATH -m venv venv
                ./venv/bin/pip install --upgrade pip
                venv/bin/pip install .
           """
        }
    }

        // stage imarina download
        stage('iMarina Download') {
          steps {
              echo "DEBUG: ID recibido: ${params.ID}"
              sh '''
                 pwd
                 mkdir -p secrets
                 echo -n "$DRIVE_ID" > secrets/DRIVE_ID

                 python3 - <<'PYEOF'
        import os, requests
        token = requests.post(
            f"https://login.microsoftonline.com/{os.environ['TENANT_ID']}/oauth2/v2.0/token",
            data={
                "grant_type" : "client_credentials",
                "client_id" : os.environ["CLIENT_ID"],
                "client_secret" : os.environ["CLIENT_SECRET"],
                "scope": "https://graph.microsoft.com/.default",

            }

        ).json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        fields = requests.get(
            f"https://graph.microsoft.com/v1.0/sites/{os.environ['MS_SITE_ID']}/lists/{os.environ['MS_LIST_ID']}/items/${params.ID}?expand=fields",
            headers=headers
        ).json()["fields"]

        for url, filename in [(fields["A3 Excel Link"], "input/A3.xlsx"), (fields["iMarina Excel Link"], "input/iMarina.xlsx")]:
            open(filename, "wb").write(requests.get(url, headers=headers).content)
            print(f"Descargado: {filename}")
        PYEOF
                    \$IMARINA_CMD download
                    ls -R input

              '''
        }
    }

       // imarina build
       stage(' iMarina Build ') {
       steps {
          echo "Build process for iMarina"
          sh "$IMARINA_CMD build"
        }
    }
    // imarina upload
    stage('iMarina upload') {
         steps {
         echo "Upload process - TODO "
         }
    }
        // execute main
        stage('Run main.py') {
        steps {
        echo "Starting main execute - TODO "
        sh """
           venv/bin/python3 src/main.py
        """

    }

    }

    }

}
