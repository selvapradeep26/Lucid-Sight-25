pipeline{
    agent any

    environment{
        EMAIL_FROM = credentials('email-from')
        EMAILPWD = credentials('email-password')

    }

    stages{
        stage('Checkout'){
            steps{
                checkout scm
            }
        }

        stage('Test Docker') {
            steps {
                sh 'echo "DOCKER_HOST=$DOCKER_HOST"'
                sh 'docker info'
            }
        }

        stage('Build Dock images'){
            steps{
                sh 'docker compose build'
            }
        }

        stage('stops Existing Containers'){
            steps{
                sh 'docker compose down'
            }
        }
        stage('Start app'){
            steps{
                sh 'docker compose up -d'
            }
        }
        
        stage('Verify container'){
            steps{
            sh 'docker compose ps'
            }
        }
        stage('verify backend'){
            steps{
                sh'''
                    ehco "checking backend health points"
                    sh 'curl --fail --retry 5 --retry-delay 2 http://localhost:5000/health'
                '''
            }
        }
        
    }


    post{

        success{
            echo 'LucidSight Deployed Successfully'
        }
        failure{
            echo 'LucidSight Deployment failed'
        }
        always{
            sh 'docker compose logs --tail=50 || true'
        }
    }
}
