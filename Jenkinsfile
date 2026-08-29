pipeline {
    agent any

    stages {
        stage('Deploy to EC2') {
            steps {
                sshagent(['ec2-ssh']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ec2-user@13.48.58.241 << 'EOF'

                        echo "===== Connected to EC2 ====="
                        hostname

                        echo "===== Go to project ====="
                        cd /home/ec2-user/Lucid-Sight-25

                        echo "===== Pull latest code ====="
                        git pull origin main

                        echo "===== Build Docker images ====="
                        docker compose build

                        echo "===== Stop existing containers ====="
                        docker compose down

                        echo "===== Start application ====="
                        docker compose up -d

                        echo "===== Verify containers ====="
                        docker compose ps

                        echo "===== Verify backend ====="
                        curl --fail --retry 5 --retry-delay 2 \
                            http://localhost:5000/api/health

                        EOF
                    '''
                }
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
    }
}