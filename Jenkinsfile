pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        ECR_REGISTRY = '065194293194.dkr.ecr.us-east-1.amazonaws.com'
        BACKEND_REPO = 'lucidsight-backend'
        FRONTEND_REPO = 'lucidsight-frontend'
    }

    stages {

        stage('Build and Push Backend to ECR') {

            steps {

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'AWS-ECR']
                ]) {

                    sh '''
                        echo "===== Login to Amazon ECR ====="

                        aws ecr get-login-password \
                            --region $AWS_REGION \
                            | docker login \
                            --username AWS \
                            --password-stdin \
                            $ECR_REGISTRY


                        echo "===== Build Backend Docker Image ====="

                        docker build \
                            -t $BACKEND_REPO:$BUILD_NUMBER \
                            ./backend


                        echo "===== Tag Backend Image ====="

                        docker tag \
                            $BACKEND_REPO:$BUILD_NUMBER \
                            $ECR_REGISTRY/$BACKEND_REPO:$BUILD_NUMBER


                        echo "===== Push Backend Image to ECR ====="

                        docker push \
                            $ECR_REGISTRY/$BACKEND_REPO:$BUILD_NUMBER


                        echo "===== Backend Image Successfully Pushed ====="

                        echo "Backend image:"
                        echo "$ECR_REGISTRY/$BACKEND_REPO:$BUILD_NUMBER"
                    '''
                }
            }
        }


        stage('Build and Push Frontend to ECR') {

            steps {

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'AWS-ECR']
                ]) {

                    sh '''
                        echo "===== Login to Amazon ECR ====="

                        aws ecr get-login-password \
                            --region $AWS_REGION \
                            | docker login \
                            --username AWS \
                            --password-stdin \
                            $ECR_REGISTRY


                        echo "===== Build Frontend Docker Image ====="

                        docker build \
                            -t $FRONTEND_REPO:$BUILD_NUMBER \
                            .


                        echo "===== Tag Frontend Image ====="

                        docker tag \
                            $FRONTEND_REPO:$BUILD_NUMBER \
                            $ECR_REGISTRY/$FRONTEND_REPO:$BUILD_NUMBER


                        echo "===== Push Frontend Image to ECR ====="

                        docker push \
                            $ECR_REGISTRY/$FRONTEND_REPO:$BUILD_NUMBER


                        echo "===== Frontend Image Successfully Pushed ====="

                        echo "Frontend image:"
                        echo "$ECR_REGISTRY/$FRONTEND_REPO:$BUILD_NUMBER"
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

                                export IMAGE_TAG=${BUILD_NUMBER}

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


                                echo '===== Login to Amazon ECR ====='

                                aws ecr get-login-password \
                                    --region us-east-1 \
                                    | docker login \
                                    --username AWS \
                                    --password-stdin \
                                    065194293194.dkr.ecr.us-east-1.amazonaws.com


                                echo '===== Stop existing containers ====='

                                docker compose down || true


                                echo '===== Pull images from ECR ====='

                                docker compose pull


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