pipeline {
    agent any

    environment {
        EMAIL_FROM = credentials('email-from')
        EMAILPWD   = credentials('email-password')
    }

    stages {
        stage('Test EC2 SSH') {
            steps {
                sshagent(['ec2-ssh']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no \
                            ec2-user@13.48.58.241 \
                            "echo EC2 SSH connection successful && hostname"

                            cd /home/ec2-user/Lucid-Sight-25

                            git pull origin main 

                            docker compose build

                            docker compose down

                            docker compose up -d

                            docker compose ps

                            curl --fail http://localhost:5000/api/health
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

        always {
            sh 'docker compose logs --tail=50 || true'
        }
    }
}