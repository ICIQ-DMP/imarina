// Second, separate Jenkins pipeline for the `publish` step (STEPS.md's
// "Publish" section). Unlike the main Jenkinsfile (download -> build ->
// upload), this one is NOT triggered by the request form / Power Automate
// on submission -- it's triggered by the Microsoft Approval flow's HTTP
// action, only after the requester approves the reviewed file that `upload`
// pushed to SharePoint. This is the human-gated production push to the
// iMarina FTP server.
//
// This file needs its own Jenkins "Pipeline" job (Script Path:
// "Jenkinsfile.publish"), separate from the job running the main
// Jenkinsfile, with "Trigger builds remotely" enabled and an authentication
// token configured -- see CLAUDE.md's "Publish pipeline" section for the
// exact job configuration and how the Power Automate approval flow calls
// this job's buildWithParameters URL. This file only expresses what runs
// once triggered, not how the trigger itself is wired up -- that's Jenkins
// job configuration, not something a Jenkinsfile can declare.
pipeline {
    agent {
        label 'agent jenkins'
    }
    options {
        disableConcurrentBuilds() // one execution only
    }
    parameters {
        string(name: 'ID', defaultValue: '', description: 'ID operation in iMarina, whose approved output should be published to the iMarina FTP server')
        booleanParam(name: 'DRY_RUN', defaultValue: true, description: 'If true, skip the actual FTP push (dry run). Pass false via buildWithParameters to perform a real publish.')
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
        stage('iMarina Publish') {
            steps {
                script {
                    try {
                        echo "Publish process"
                        sh """
                            \$IMARINA_CMD publish --id ${params.ID} --dry-run ${params.DRY_RUN}
                        """
                        echo "Sending published email"
                        sh """
                            \$IMARINA_CMD notify --id ${params.ID} --status published
                        """
                    }
                    catch (Exception e) {
                        echo "Sending error email"
                        sh """
                            \$IMARINA_CMD notify --id ${params.ID} --status error
                        """
                        error "Publish has failed: ${e.message}"
                    }
                }
            }
        }
    }
}
