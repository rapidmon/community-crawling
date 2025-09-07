# -*- coding: utf-8 -*-
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
        print("\n환경변수 설정 방법:")
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
