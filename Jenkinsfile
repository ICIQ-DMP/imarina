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
         MS_LIST_ID = credentials('MS_LIST_ID')
         MS_SITE_ID = credentials('MS_SITE_ID')
         SHAREPOINT_DOMAIN = credentials('SHAREPOINT_DOMAIN')
         SITE_NAME = credentials('SITE_NAME')
         LIST_NAME = credentials('LIST_NAME')

    }

    stages {
        // Python venv and dependencies
        stage('Prepare Python environment and dependencies') {
        steps {
           echo "Creating virtual environment and update dependencies..."
           sh"""
                rm -rf venv
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
                 rm -rf input

              '''
              sh """
                  \$IMARINA_CMD download --id ${params.ID}
                  ls -R input
              """
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
         echo "Upload process "
         sh '${IMARINA_CMD} upload'
         }
    }


    }

}
