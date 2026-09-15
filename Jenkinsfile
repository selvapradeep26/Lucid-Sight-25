pipeline {
    agent any

    stages {

         stage('Test AWS Connection') {
            steps {

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'AWS-ECR']
                ]) {

                    sh '''
                        echo "===== Testing AWS CLI ====="

                        aws --version

                        echo "===== Checking AWS Identity ====="

                        aws sts get-caller-identity

                        echo "===== Checking ECR ====="

                        aws ecr describe-repositories \
                            --region us-east-1 \
                            --repository-names lucidsight-backend lucidsight-frontend

                        echo "===== AWS ECR CONNECTION SUCCESSFUL ====="
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {

                withCredentials([
                    string(credentialsId: 'email-from', variable: 'EMAILUSER'),
                    string(credentialsId: 'email-password', variable: 'EMAILPWD')
                ]) {

                    sshagent(['ec2-ssh1']) {

                        sh '''
                            set +x

                            ENV_FILE=$(mktemp)
                            chmod 600 "$ENV_FILE"

                            trap 'rm -f "$ENV_FILE"' EXIT

                            printf '%s\\n' \
                                "EMAILUSER=$EMAILUSER" \
                                "EMAILPWD=$EMAILPWD" \
                                > "$ENV_FILE"

                            echo "===== Copy .env to EC2 ====="

                            scp \
                                -o StrictHostKeyChecking=no \
                                -o BatchMode=yes \
                                "$ENV_FILE" \
                                ec2-user@44.198.227.101:/home/ec2-user/Lucid-Sight-25/.env

                            echo "===== Deploy to EC2 ====="

                            ssh \
                                -o StrictHostKeyChecking=no \
                                -o BatchMode=yes \
                                -o ConnectTimeout=15 \
                                ec2-user@44.198.227.101 \
                                "
                                set -e

                                echo '===== Connected to EC2 ====='
                                hostname
                                whoami

                                cd /home/ec2-user/Lucid-Sight-25

                                echo '===== Secure .env ====='
                                chmod 600 .env

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
                                curl --fail --retry 5 --retry-delay 2 \
                                    http://localhost:5000/api/health

                                echo '===== DEPLOYMENT SUCCESSFUL ====='
                                "
                        '''
                    }
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