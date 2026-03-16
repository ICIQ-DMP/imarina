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
              echo "DEBUG: Procesando ID: ${OPERATION_ID}"
              sh '''
                 pwd
                 mkdir -p secrets
                 echo -n "$DRIVE_ID" > secrets/DRIVE_ID

                 ACCESS_TOKEN=$(curl -s -X POST "https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token" \
                     -d "client_id=${CLIENT_ID}" \
                     -d "scope=https://graph.microsoft.com/.default" \
                     -d "client_secret=${CLIENT_SECRET}" \
                     -d "grant_type=client_credentials" | jq -r '.access_token')

                 SITE_NAME=$(cat secrets/SITE_NAME)
                 SHAREPOINT_DOMAIN=$(cat secrets/SHAREPOINT_DOMAIN)

                 SITE_ID=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
                      "https://graph.microsoft.com/v1.0/sites/${SHAREPOINT_DOMAIN}:/sites/${SITE_NAME}?\$select=id" | jq -r '.id')

                 ITEM_DATA=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
                      "https://graph.microsoft.com/v1.0/sites/${SITE_ID}/lists/imarina%20form/items/${OPERATION_ID}?expand=fields")

                 URL_A3=$(echo $ITEM_DATA | jq -r '.fields.A3ExcelLink // .fields.A3 Excel Link')
                 URL_IMARINA=$(echo $ITEM_DATA | jq -r '.fields.iMarinaExcelLink // .fields.iMarina Excel Link')


                 if [ "$URL_A3" != "null" ]; then
                     $IMARINA_CMD download --url "$URL_A3" --out "input/A3_export.xlsx"
                 fi

                 if [ "$URL_IMARINA" != "null" ]; then
                     $IMARINA_CMD download --url "$URL_IMARINA" --out "input/imarina_export.xlsx"
                 fi

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
