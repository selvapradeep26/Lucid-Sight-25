pipeline {
    agent any

    environment {
        EMAIL_FROM = credentials('email-from')
        EMAILPWD   = credentials('email-password')
    }

    stages {

        stage('Deploy to EC2') {
            steps {

                sshagent(['ec2-ssh']) {

                    sh '''
                        ssh -o ec2-ssh1 ec2-user@184.192.255.135<< 'EOF'

                        set -e

                        echo "======================================"
                        echo "       Connected to EC2"
                        echo "======================================"

                        hostname

                        echo "======================================"
                        echo "       Go to project"
                        echo "======================================"

                        cd /home/ec2-user/Lucid-Sight-25

                        echo "======================================"
                        echo "       Pull latest code"
                        echo "======================================"

                        git fetch origin
                        git reset --hard origin/main

                        echo "======================================"
                        echo "       Docker Compose check"
                        echo "======================================"

                        docker compose version

                        echo "======================================"
                        echo "       Stop existing containers"
                        echo "======================================"

                        docker compose down

                        echo "======================================"
                        echo "       Build Docker images"
                        echo "======================================"

                        docker compose build

                        echo "======================================"
                        echo "       Start application"
                        echo "======================================"

                        docker compose up -d

                        echo "======================================"
                        echo "       Container status"
                        echo "======================================"

                        docker compose ps

                        echo "======================================"
                        echo "       Backend health check"
                        echo "======================================"

                        curl --fail --retry 5 --retry-delay 2 \
                            http://localhost:5000/api/health

                        echo ""
                        echo "======================================"
                        echo "       DEPLOYMENT SUCCESSFUL"
                        echo "======================================"

                        EOF
                    '''
                }
            }
        }
    }

    post {

        success {
            echo 'LucidSight deployed successfully to EC2'
        }

        failure {
            echo 'LucidSight deployment failed'
        }
    }
}