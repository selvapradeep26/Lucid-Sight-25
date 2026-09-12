pipeline {
    agent any

    stages {

        stage('Deploy to EC2') {
            steps {

                sshagent(['ec2-ssh1']) {

                    sh '''
                        ssh \
                            -o StrictHostKeyChecking=no \
                            -o BatchMode=yes \
                            -o ConnectTimeout=15 \
                            ec2-user@184.192.255.135 \
                            "
                            set -e

                            echo '===== Connected to EC2 ====='
                            hostname
                            whoami

                            echo '===== Go to project ====='
                            cd /home/ec2-user/Lucid-Sight-25

                            echo '===== Pull latest code ====='
                            git fetch origin
                            git reset --hard origin/main

                            echo '===== Docker versions ====='
                            docker --version
                            docker compose version
                            docker buildx version

                            echo '===== Stop existing containers ====='
                            docker compose down || true

                            echo '===== Build Docker images ====='
                            docker compose build

                            echo '===== Start application ====='
                            docker compose up -d

                            echo '===== Verify containers ====='
                            docker compose ps

                            echo '===== Verify backend ====='
                            curl --fail --retry 5 --retry-delay 2 http://localhost:5000/api/health

                            echo '===== DEPLOYMENT SUCCESSFUL ====='
                            "
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