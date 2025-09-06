# -*- coding: utf-8 -*-
'''
로컬 테스트용 스크립트
실행: python test_local.py
'''

import os
from datetime import datetime
from main import main_github_actions

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
