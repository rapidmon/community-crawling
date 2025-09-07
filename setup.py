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

매일 오전 10시에 자동으로 한국 주요 커뮤니티를 크롤링하여 GitHub Release에 저장하는 시스템입니다.

## 🎯 대상 사이트
- 디시인사이드 (베스트)
- FM코리아 (베스트)
- 더쿠 (핫게시판)
- 인스티즈 (이슈)

## 🚀 특징
- GitHub Actions를 이용한 완전 자동화
- 화제성 점수 자동 계산 (0-11점)
- GitHub Release 자동 업로드
- 매일 오전 10시 자동 실행
- 완전 무료 운영

## 📊 수집 데이터
- 제목, URL, 작성일
- 조회수, 댓글수
- 화제성 점수 (0-11점)
- 출처 사이트

## 🛠️ 설정 방법

### 1. GitHub Personal Access Token 생성
1. GitHub.com → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. 권한 선택: `repo`, `workflow`
5. 토큰 복사 (한 번만 표시됨!)

### 2. GitHub Secrets 설정
리포지토리 → Settings → Secrets and variables → Actions에서 추가:
- `GITHUB_TOKEN`: 생성한 Personal Access Token
- `REPO_OWNER`: GitHub 사용자명
- `REPO_NAME`: 리포지토리명

### 3. 실행
- **자동 실행**: 매일 오전 10시 KST
- **수동 실행**: GitHub Actions 탭 → "Run workflow" 클릭

## 📈 결과 확인
1. **GitHub Actions**: 실행 로그 확인
2. **Releases 탭**: 새로운 릴리즈와 CSV 파일 다운로드
3. **파일명 형식**: `community_crawling_MMDD_HHMM.csv`

## 📂 데이터 위치
- 리포지토리 → **Releases** 탭
- 릴리즈명: `data-YYYYMMDD` 형식
- CSV 파일 직접 다운로드 가능

## 🔧 문제해결
실행이 실패할 경우:
1. GitHub Actions 로그 확인
2. GitHub Token 권한 확인
3. 환경변수 설정 확인

## 💰 비용
- **GitHub Actions**: 무료 (월 2,000분 제공)
- **GitHub Releases**: 무료 (무제한)
- **총 운영비용**: 0원

## 📋 수집 통계
- 평균 800-1000개 게시글/일
- 사이트별 화제성 점수 분석
- 고화제성 게시글(5.5점 이상) 필터링

---
Made with ❤️ by Python & GitHub Actions
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README.md 파일 생성")

def check_dependencies():
    """필수 파일들이 있는지 확인"""
    required_files = [
        'main.py'  # 통합된 파일
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ 누락된 파일들: {', '.join(missing_files)}")
        print("main.py 파일을 프로젝트 루트에 복사해주세요.")
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
from main import main_github_actions

def test_local():
    print("🧪 로컬 테스트 시작")
    
    # GitHub 환경변수 확인
    required_vars = ['GITHUB_TOKEN', 'REPO_OWNER', 'REPO_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 누락된 환경변수: {', '.join(missing_vars)}")
        print("\\n환경변수 설정 방법:")
        print("export GITHUB_TOKEN='your_token_here'")
        print("export REPO_OWNER='your_username'")
        print("export REPO_NAME='your_repo_name'")
        return
    
    # 테스트 실행
    print("환경변수 확인 완료, 크롤링 시작...")
    result = main_github_actions()
    
    if result['success']:
        print(f"✅ 테스트 성공!")
        print(f"파일: {result['filename']}")
        print(f"게시글 수: {result['total_count']}")
        
        if result['upload_result']['success']:
            print(f"📤 GitHub Release 업로드 성공")
            print(f"🔗 다운로드: {result['upload_result']['download_url']}")
        else:
            print(f"📁 로컬 저장: {result['upload_result'].get('local_file')}")
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
    print("1. GitHub Personal Access Token 생성")
    print("   - GitHub.com → Settings → Developer settings")
    print("   - Personal access tokens → Generate new token")
    print("   - 권한: repo, workflow")
    print()
    print("2. GitHub Secrets 설정:")
    print("   - GITHUB_TOKEN: 생성한 토큰")
    print("   - REPO_OWNER: GitHub 사용자명")
    print("   - REPO_NAME: 리포지토리명")
    print()
    print("3. GitHub 리포지토리 생성 및 코드 푸시")
    print("4. GitHub Actions에서 테스트 실행")
    print()
    print("🔧 로컬 테스트:")
    print("1. 환경변수 설정:")
    print("   export GITHUB_TOKEN='your_token'")
    print("   export REPO_OWNER='your_username'")
    print("   export REPO_NAME='your_repo'")
    print("2. python test_local.py")
    print()
    print("📈 결과 확인:")
    print("- GitHub 리포지토리 → Releases 탭")
    print("- 매일 오전 10시 자동 실행")
    print("- CSV 파일 직접 다운로드")
    print()
    print("📖 자세한 내용은 README.md 파일을 참고하세요!")

def main():
    print("🚀 커뮤니티 크롤링 자동화 시스템 설정 (GitHub Release)")
    print("="*60)
    
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