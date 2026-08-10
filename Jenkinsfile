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

    environment {
         PYTHON_PATH = "/usr/bin/python3"
         IMARINA_CMD = "venv/bin/imarina"
    }

    stages {
        stage('Prepare Python environment and dependencies') {
        steps {
           echo "Creating virtual environment and update dependencies..."
           sh"""
                make install
           """
        }
    }
        stage('iMarina Download') {
          steps {
              sh """
                  \$IMARINA_CMD download ${params.ID}
              """
        }
    }
       stage('iMarina Build') {
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
                  sh '${IMARINA_CMD} notify --id ${params.ID} --status success'
              }
              catch (Exception e) {
                  echo "Sending error email"
                  sh '${IMARINA_CMD} notify --id ${params.ID} --status error'
                  error "Upload has failed: ${e.message}"
              }
          }
       }
    }


    }

}
