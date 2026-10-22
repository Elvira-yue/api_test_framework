// =========================================================================
// Jenkins Pipeline - API 自动化测试（Windows 本机版，Git 拉取模式）
// =========================================================================
// 前置准备（一次性，已完成）：
//   1. Jenkins 插件：Allure Jenkins Plugin、Git plugin
//   2. Manage Jenkins -> Tools -> Allure Commandline -> Name: allure
//        Home dir: C:\Users\越越\allure
//   3. 仓库为 public，匿名 HTTPS 拉取，无需 Git 凭据
// =========================================================================

pipeline {
    agent { node { label 'built-in'; customWorkspace 'C:/jenkins/ws/api-auto-test' } }

    parameters {
        choice(name: 'ENV', choices: ['dev', 'test', 'prod'], description: '被测环境')
        string(name: 'REPO_URL', defaultValue: 'https://github.com/Elvira-yue/api_test_framework.git', description: '测试 Git 仓库地址')
        booleanParam(name: 'AUTO_START_SERVICES', defaultValue: true, description: '构建前自动启动后端/MySQL')
    }

    tools {
        allure 'allure'
    }

    environment {
        BACKEND_PORT   = "3000"
        MYSQL_PORT     = "3306"
        VENV_DIR       = ".venv"
    }

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    stages {

        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[ url: params.REPO_URL ]]
                ])
            }
        }

        stage('Check Services') {
            steps {
                bat '''
                @echo off
                set "NODE_HOME=C:\\Users\\越越\\AppData\\Local\\Temp\\trae-node\\node-v22.11.0-win-x64"
                set "PATH=%NODE_HOME%;%PATH%"
                echo ========================================
                echo   Check MySQL / Backend
                echo ========================================
                netstat -ano | findstr ":3306 " | findstr "LISTENING" >nul
                if %errorlevel%==0 goto mysql_ok
                if not "%AUTO_START_SERVICES%"=="true" (
                    echo [FAIL] MySQL not running
                    exit /b 1
                )
                echo [INFO] Starting MySQL ...
                start "" /min "C:\\Users\\Public\\mysql\\mysql-8.0.29-winx64\\bin\\mysqld.exe" --datadir=C:\\Users\\Public\\mysql\\data --port=3306
                :wait_mysql
                ping -n 3 127.0.0.1 >nul
                netstat -ano | findstr ":3306 " | findstr "LISTENING" >nul
                if errorlevel 1 goto wait_mysql
                :mysql_ok
                echo [OK] MySQL ready (3306)

                netstat -ano | findstr ":3000 " | findstr "LISTENING" >nul
                if %errorlevel%==0 goto backend_ok
                if not "%AUTO_START_SERVICES%"=="true" (
                    echo [FAIL] Backend not running
                    exit /b 1
                )
                echo [INFO] Starting Backend ...
                start "JenkinsBackend" /d "D:\\projects\\trae项目\\user-management-system\\backend" cmd /c "node src/server.js"
                :wait_backend
                ping -n 3 127.0.0.1 >nul
                netstat -ano | findstr ":3000 " | findstr "LISTENING" >nul
                if errorlevel 1 goto wait_backend
                :backend_ok
                echo [OK] Backend ready (3000)
                echo [DONE] All services ready
                '''
            }
        }

        stage('Setup Python') {
            steps {
                bat '''
                @echo off
                if not exist "%VENV_DIR%\\Scripts\\python.exe" (
                    echo [INFO] Creating venv ...
                    python -m venv "%VENV_DIR%" || exit /b 1
                ) else (
                    echo [OK] venv exists
                )
                call "%VENV_DIR%\\Scripts\\activate.bat"
                python --version
                pip install --upgrade pip -q
                pip install -r requirements.txt -q
                pytest --version
                '''
            }
        }

        stage('Configure') {
            steps {
                bat '''
                @echo off
                call "%VENV_DIR%\\Scripts\\activate.bat"
                python -c "import yaml; p='data/config.yaml'; f=open(p,encoding='utf-8'); c=yaml.safe_load(f); f.close(); c['env']='%ENV%'; f=open(p,'w',encoding='utf-8'); yaml.dump(c,f,allow_unicode=True); f.close(); print('OK env='+c['env'])"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                bat '''
                @echo off
                call "%VENV_DIR%\\Scripts\\activate.bat"
                if exist "allure-results" rmdir /s /q allure-results
                pytest test_cases -v --tb=short --alluredir=allure-results --clean-alluredir --junitxml=allure-results\\junit.xml
                set EXITCODE=%ERRORLEVEL%
                echo EXITCODE=%EXITCODE%
                exit /b %EXITCODE%
                '''
            }
        }

        stage('Allure Report') {
            steps {
                allure includeProperties: false, report: 'allure-report', reportBuildPolicy: 'ALWAYS', results: [[path: 'allure-results']]
            }
        }
    }

    post {
        success  { echo 'DONE - All tests passed!' }
        failure  { echo 'FAILED - Check Allure Report' }
        unstable { echo 'UNSTABLE - Some tests failed or skipped' }
    }
}
