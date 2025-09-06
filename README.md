# 커뮤니티 크롤링 자동화

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
