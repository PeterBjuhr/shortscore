pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'docker build -t shortscore:1 .'
      }
    }
    stage('Test') {
      steps {
        sh 'docker run --rm shortscore:1 python -m unittest test.shortScoreTests'
      }
    }
  }
}
