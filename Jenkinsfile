pipeline {
    agent {
        label 'agent docker'
    }
    options {
         disableConcurrentBuilds() // one execution only
    }
    parameters {
        string(name: 'ID', defaultValue: '' , description: 'ID operation in iMarina')
    }
    // environment variables
    environment {
         PYTHON_PATH = "./venv/bin/python3"
         IMARINA_CMD = "./venv/bin/python3 -m imarina"
    }

    stages {

        // Python venv and dependencies
        stage('Prepare Python environment and dependencies') {
        steps {
           echo "Creating virtual environment and update dependencies..."
           sh'''
                python3 -m venv venv
                ./venv/bin/pip install --upgrade pip
                ./venv/bin/pip install -r requirements.txt
           '''
        }

    }
        // imarina download
        stage('iMarina Download') {
          steps {
              sh "./venv/bin/python3 -m imarina download --id ${params.ID}"
        }
    }

       // imarina build
       stage(' iMarina Build ') {
       steps {
          echo "Build process for iMarina"
          sh "${IMARINA_CMD} build"
        }
    }

    // imarina upload
    stage('iMarina upload') {
         // TODO steps

    }

        // execute main
        stage('Run main.py') {
        steps {
        echo "Starting main execute"
        sh '''
           ./venv/bin/python src/main.py
        '''

    }

    }

    }

}
