pipeline {
    agent any

    environment {
        EMAIL_FROM = credentials('email-from')
        EMAILPWD   = credentials('email-password')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test Docker') {
            steps {
                sh 'echo "DOCKER_HOST=$DOCKER_HOST"'
                sh 'docker info'
            }
        }

        stage('Test EC2 SSH') {
            steps {
                sshagent(['ec2-ssh']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no \
                            ec2-user@16.171.21.197 \
                            "echo EC2 SSH connection successful && hostname"
                    '''
                }
            }
        }

        stage('Build Docker images') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Stop Existing Containers') {
            steps {
                sh 'docker compose down'
            }
        }

        stage('Start app') {
            steps {
                sh 'docker compose up -d'
            }
        }

        stage('Verify container') {
            steps {
                sh 'docker compose ps'
            }
        }

        stage('Verify backend') {
            steps {
                sh 'curl --fail --retry 5 --retry-delay 2 http://localhost:5000/api/health'
            }
        }
    }

    post {
        success {
            echo 'LucidSight Deployed Successfully'
        }

        failure {
            echo 'LucidSight Deployment failed'
        }

        always {
            sh 'docker compose logs --tail=50 || true'
        }
    }
}