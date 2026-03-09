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
              sh """
                 $IMARINA_CMD download --id ${params.ID}
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
