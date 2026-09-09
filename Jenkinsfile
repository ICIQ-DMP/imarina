pipeline {
    agent {
        label 'imarina-load-researchers-agent'
    }
    options {
        disableConcurrentBuilds() // one execution only
    }
    parameters {
        string(name: 'ID', defaultValue: '', description: 'ID operation in iMarina')
    }

    environment {
        PYTHON_PATH = "/usr/bin/python3"
        IMARINA_CMD = "venv/bin/imarina-load-researchers"
    }

    stages {
        stage('Prepare Python environment and dependencies') {
            steps {
                echo "Creating virtual environment and update dependencies..."
                sh """
                    make install
                """
            }
        }
        stage('iMarina Download') {
            steps {
                script {
                    try {
                        sh """
                            \$IMARINA_CMD -v download ${params.ID}
                        """
                    }
                    catch (Exception e) {
                        echo "Sending error email"
                        sh """
                            \$IMARINA_CMD notify --id ${params.ID} --status error
                        """
                        error "Download has failed: ${e.message}"
                    }
                }
            }
        }
        stage('iMarina Build') {
            steps {
                script {
                    try {
                        echo "Build process for iMarina"
                        sh """
                            \$IMARINA_CMD build --id ${params.ID}
                        """
                    }
                    catch (Exception e) {
                        echo "Sending error email"
                        sh """
                            \$IMARINA_CMD notify --id ${params.ID} --status error
                        """
                        error "Build has failed: ${e.message}"
                    }
                }
            }
        }
        stage('iMarina upload') {
            steps {
                script {
                    try {
                        echo "Upload process"
                        sh """
                            \$IMARINA_CMD upload --id ${params.ID}
                        """
                    }
                    catch (Exception e) {
                        echo "Sending error email"
                        sh """
                            \$IMARINA_CMD notify --id ${params.ID} --status error
                        """
                        error "Upload has failed: ${e.message}"
                    }
                }
            }
        }
        stage('iMarina notify') {
            steps {
                script {
                    echo "Sending success email"
                    sh """
                        \$IMARINA_CMD notify --id ${params.ID} --status success
                    """
                }
            }
        }
    }
}
