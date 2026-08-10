pipeline {
    agent {
        label 'agent jenkins'
    }
    options {
         disableConcurrentBuilds() // one execution only
    }
    parameters {
         string(name: 'ID', defaultValue: '' , description: 'ID operation in iMarina')
         string(name: 'EMAIL', defaultValue: '', description: 'Creator email')
         string(name: 'NAME', defaultValue: '', description: 'Creator name')
    }

    environment {
         PYTHON_PATH = "/usr/bin/python3"
         IMARINA_CMD = "venv/bin/imarina"
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
                  \$IMARINA_CMD download ${params.ID}
                  ls -R input
              """
        }
    }
       stage(' iMarina Build ') {
       steps {
          echo "Build process for iMarina"
          sh "$IMARINA_CMD build"
        }
    }
       stage('iMarina upload') {
         steps {
          script {
              try {
                  echo "Upload process"
                  sh '${IMARINA_CMD} upload'
                  echo "Sending success email"
                  sh '${IMARINA_CMD} notify --id ${OPERATION_ID} --status success'
              }
              catch (Exception e) {
                  echo "Sending error email"
                  sh '${IMARINA_CMD} notify --id ${OPERATION_ID} --status error'
                  error "Upload ha fallat: ${e.message}"
              }
          }
       }
    }


    }

}
