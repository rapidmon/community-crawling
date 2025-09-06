# -*- coding: utf-8 -*-
"""
GitHub Actions 환경 설정을 위한 초기 설정 스크립트
실행: python setup.py
"""

import os
import json
import sys
from pathlib import Path

def create_project_structure():
    """프로젝트 디렉토리 구조 생성"""
    print("📁 프로젝트 구조 생성 중...")
    
    directories = [
        '.github/workflows',
        'logs',
        'temp',
        'models'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")

def create_gitignore():
    """적절한 .gitignore 파일 생성"""
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 가상환경
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 로그 파일
*.log
logs/

# 임시 파일
temp/
*.tmp
*.csv
*.joblib

# 민감한 정보
service-account-key.json
.env
credentials.json

# OS
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content.strip())
    
    print("✅ .gitignore 파일 생성")

def create_readme():
    """README.md 파일 생성"""
    readme_content = """# 커뮤니티 크롤링 자동화

매일 오전 10시에 자동으로 한국 주요 커뮤니티를 크롤링하여 Google Drive에 저장하는 시스템입니다.

## 🎯 대상 사이트
- 디시인사이드 (베스트)
- FM코리아 (베스트)
- 더쿠 (핫게시판)
- 인스티즈 (이슈)

## 🚀 특징
- GitHub Actions를 이용한 완전 자동화
- 화제성 점수 자동 계산
- 게시글 카테고리 자동 분류
- Google Drive 자동 업로드
- 매일 오전 10시 자동 실행

## 📊 수집 데이터
- 제목, URL, 작성일
- 조회수, 댓글수
- 화제성 점수 (0-11점)
- 예상 카테고리 (정치, 경제, 스포츠 등)

## 🛠️ 설정 방법

### 1. Google Drive API 설정
1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. Google Drive API 활성화
3. 서비스 계정 생성 및 JSON 키 다운로드
4. Google Drive 폴더 생성 후 서비스 계정과 공유

### 2. GitHub Secrets 설정
- `GOOGLE_CREDENTIALS`: 서비스 계정 JSON 키 전체 내용
- `GOOGLE_DRIVE_FOLDER_ID`: Google Drive 폴더 ID

### 3. 실행
자동 실행: 매일 오전 10시 KST
수동 실행: GitHub Actions 탭에서 "Run workflow" 클릭

## 📈 결과 확인
- GitHub Actions 탭에서 실행 로그 확인
- Google Drive에서 CSV 파일 다운로드

## 🔧 문제해결
실행이 실패할 경우:
1. GitHub Actions 로그 확인
2. Google Drive API 권한 확인
3. 서비스 계정 키 유효성 확인

---
Made with ❤️ by Python & GitHub Actions
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README.md 파일 생성")

def check_dependencies():
    """필수 파일들이 있는지 확인"""
    required_files = [
        'bsmain.py',
        'simple.py',
        'train.csv'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ 누락된 파일들: {', '.join(missing_files)}")
        print("이 파일들을 프로젝트 루트에 복사해주세요.")
        return False
    else:
        print("✅ 모든 필수 파일 확인됨")
        return True

def create_test_script():
    """로컬 테스트용 스크립트 생성"""
    test_content = """# -*- coding: utf-8 -*-
'''
로컬 테스트용 스크립트
실행: python test_local.py
'''

import os
from datetime import datetime
from cloud_crawler import main_github_actions

def test_local():
    print("🧪 로컬 테스트 시작")
    
    # 환경변수 확인
    if not os.environ.get('GOOGLE_CREDENTIALS'):
        print("❌ GOOGLE_CREDENTIALS 환경변수가 설정되지 않았습니다")
        print("service-account-key.json 파일을 만들고 다음 명령어를 실행하세요:")
        print("export GOOGLE_CREDENTIALS=$(cat service-account-key.json)")
        return
    
    if not os.environ.get('GOOGLE_DRIVE_FOLDER_ID'):
        print("❌ GOOGLE_DRIVE_FOLDER_ID 환경변수가 설정되지 않았습니다")
        print("export GOOGLE_DRIVE_FOLDER_ID='your-folder-id'")
        return
    
    # 테스트 실행
    result = main_github_actions()
    
    if result['success']:
        print(f"✅ 테스트 성공!")
        print(f"파일: {result['filename']}")
        print(f"게시글 수: {result['total_count']}")
    else:
        print(f"❌ 테스트 실패: {result['error']}")

if __name__ == "__main__":
    test_local()
"""
    
    with open('test_local.py', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ test_local.py 생성")

def show_next_steps():
    """다음 단계 안내"""
    print("\n" + "="*60)
    print("🎉 초기 설정이 완료되었습니다!")
    print("="*60)
    print("\n📋 다음 단계:")
    print("1. Google Cloud Console에서 서비스 계정 생성")
    print("2. Google Drive 폴더 생성 및 공유")
    print("3. GitHub 리포지토리 생성")
    print("4. 코드를 GitHub에 푸시")
    print("5. GitHub Secrets 설정:")
    print("   - GOOGLE_CREDENTIALS")
    print("   - GOOGLE_DRIVE_FOLDER_ID")
    print("6. GitHub Actions에서 테스트 실행")
    
    print("\n🔧 로컬 테스트:")
    print("1. service-account-key.json 파일 준비")
    print("2. 환경변수 설정:")
    print("   export GOOGLE_CREDENTIALS=$(cat service-account-key.json)")
    print("   export GOOGLE_DRIVE_FOLDER_ID='your-folder-id'")
    print("3. python test_local.py")
    
    print("\n📖 자세한 내용은 README.md 파일을 참고하세요!")

def main():
    print("🚀 커뮤니티 크롤링 자동화 시스템 설정")
    print("="*50)
    
    # 1. 프로젝트 구조 생성
    create_project_structure()
    
    # 2. 설정 파일들 생성
    create_gitignore()
    create_readme()
    create_test_script()
    
    # 3. 의존성 확인
    check_dependencies()
    
    # 4. 다음 단계 안내
    show_next_steps()

if __name__ == "__main__":
    main()