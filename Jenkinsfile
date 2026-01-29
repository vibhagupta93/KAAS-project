


pipeline {
    agent { label 'default' }

    environment {
        IMAGE_NAME = 'test_bench'
        IMAGE_TAG = "${GIT_COMMIT}"
    }


    stages {
        stage('Build Image') {
            steps {
                echo 'build image'
                sh """
                    docker build --pull --no-cache \
                    -t ${IMAGE_NAME}:${IMAGE_TAG} \
                    -f docker/Dockerfile .
                """                
            }
        }
        stage('Linting') {
            steps {
                echo 'Linting..'
                sh "mkdir ${WORKSPACE}/report"
                sh """
                    docker run --rm -v ${WORKSPACE}/report:/tests/reports ${IMAGE_NAME}:${IMAGE_TAG} tox -c tox_rpi_bench.ini -e pylint
                """
            }
        }
        stage('Testing') {
            steps {
                echo 'Testing..'
                sh """
                    docker run --rm -v ${WORKSPACE}/report:/tests/reports ${IMAGE_NAME}:${IMAGE_TAG} tox -c tox_rpi_bench.ini -e py310
                """
            }
        }
    }

    post { 
        always { 
            //sh "tar -zcvf report.tar.gz ${WORKSPACE}/report"
            //archiveArtifacts artifacts: 'report.tar.gz', fingerprint: true

            sh "docker rmi -f ${IMAGE_NAME}:latest || exit 0"
            sh "docker rmi -f ${IMAGE_NAME}:${IMAGE_TAG} || exit 0"

            cleanWs()
            dir("${workspace}@tmp") {
                deleteDir()
            }
            
        }
    }
}