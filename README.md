파이썬 버전 = 3.11.9

(1) .env
- openai의 apikey
- model_manager에서 모델의 메타데이터 저장에 사용되는 스프레드 시트의 ID

(2) my-google-sheet-api-key.json


위 두개의 파일이 루트디렉토리에 존재해야 하며,
.gitignore에 등록되어있음.


파일은 bny 드라이브의 앱개발->secret->customgpt 에 존재함
(.env파일은 숨김파일이므로 command+shift+. 으로 확인가능)

이 두 파일을 루트디렉토리에 붙여넣기 해야 정상적으로 실행 가능함



(.gitignore)


가상환경을 먼저 생성하고 git clone을 해서,
터미널에서 실행할때 자꾸 상위폴더를 기점으로 파일을 실행하는 경우

프로젝트 루트디렉토리에

mkdir .vscode
cd .vscode
touch launch.json

(.vscode 폴더를 만들어서 들어가고 그안에 launch.json 파일을 만듬)

그 파일 안에 아래 값을 복붙하면 현재파일을 기준으로 실행하게됨

{
    "version": "0.2.0",
    "configurations": [
        
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${fileDirname}"
        }
    ]
}
