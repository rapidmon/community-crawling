# 커뮤니티 크롤링 자동화

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
