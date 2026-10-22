// =========================================================================
// Jenkins Pipeline - API 自动化测试（Windows 本机版）
// =========================================================================
// 前置准备（一次性）：
//   1. Jenkins 装插件：Allure Jenkins Plugin、Git plugin
//   2. Manage Jenkins -> Tools -> Allure Commandline -> Add:
//        Name: allure
//        Home dir: C:\Users\越越\allure          ← 本机 Allure CLI 解压根目录（含 bin/config/lib/plugins）
//   3. Manage Jenkins -> Credentials -> Add Username with password:
//        ID: GIT_CREDENTIALS, User: 你的 Git 账号, Pass: 你的 Git Token
//   4. 确保后端已启动（双击 start-all.bat）
// =========================================================================

pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['dev', 'test', 'prod'], description: '被测环境')
        string(name: 'REPO_URL', defaultValue: 'https://github.com/Elvira-yue/api_test_framework.git', description: '测试 Git 仓库地址')
        booleanParam(name: 'AUTO_START_SERVICES', defaultValue: true, description: '构建前自动启动后端/MySQL')
    }

    tools {
        allure 'allure'
    }

    environment {
        START_ALL_BAT  = "D:/projects/trae项目/start-all.bat"
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
                    branches: [[name: 'main']],
                    userRemoteConfigs: [[ url: params.REPO_URL, credentialsId: 'GIT_CREDENTIALS' ]]
                ])
            }
        }

        stage('Check Services') {
            steps {
                bat '''
                @echo off
                echo ========================================
                echo   Check MySQL / Backend
                echo ========================================
                netstat -ano | findstr ":3306 " | findstr "LISTENING" >nul
                if %errorlevel%==0 (
                    echo [OK] MySQL running on 3306
                ) else (
                    if "%AUTO_START_SERVICES%"=="true" (
                        echo [INFO] Starting services...
                        call "%START_ALL_BAT%"
                    ) else (
                        echo [FAIL] MySQL not running
                        exit /b 1
                    )
                )
                timeout /t 2 /nobreak >nul
                netstat -ano | findstr ":3000 " | findstr "LISTENING" >nul
                if %errorlevel%==0 (
                    echo [OK] Backend running on 3000
                ) else (
                    if "%AUTO_START_SERVICES%"=="true" (
                        timeout /t 8 /nobreak >nul
                        netstat -ano | findstr ":3000 " | findstr "LISTENING" >nul
                        if %errorlevel%==0 (
                            echo [OK] Backend started
                        ) else (
                            echo [FAIL] Backend start failed
                            exit /b 1
                        )
                    ) else (
                        echo [FAIL] Backend not running
                        exit /b 1
                    )
                )
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
                allure includePattern: 'allure-results/*-result.json', disabled: false, noSkips: false
            }
        }
    }

    post {
        success  { echo 'DONE - All tests passed!' }
        failure  { echo 'FAILED - Check Allure Report' }
        unstable { echo 'UNSTABLE - Some tests failed or skipped' }
    }
}
