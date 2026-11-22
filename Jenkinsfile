pipeline {
    agent any

    environment {
        IMAGE_NAME = "helpdesk-app"
        CONTAINER_NAME = "helpdesk-app"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pytest
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME:${BUILD_NUMBER} -t $IMAGE_NAME:latest .'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f $CONTAINER_NAME || true
                    docker run -d --name $CONTAINER_NAME -p 5000:5000 $IMAGE_NAME:latest
                '''
            }
        }
    }

    post {
        success { echo 'Pipeline succeeded! HelpDesk app running on port 5000.' }
        failure { echo 'Pipeline failed. Check the console output.' }
    }
}