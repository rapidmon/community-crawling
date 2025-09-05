# -*- coding: utf-8 -*-
import os
import sys
import json
import logging
from datetime import datetime, timedelta, timezone
import pandas as pd
from io import BytesIO

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))

class HotScoreCalculator:
    def __init__(self):
        self.site_stats = {}
    
    def collect_stats(self, data):
        for site_name, df in data.items():
            if len(df) > 0:
                # 조회수와 댓글수 컬럼 확인
                views_col = 'views' if 'views' in df.columns else None
                comments_col = 'comments' if 'comments' in df.columns else None
                
                # 기본값 설정
                max_views = 1
                max_comments = 1
                
                if views_col and df[views_col].notna().any():
                    max_views = max(df[views_col].max(), 1)
                
                if comments_col and df[comments_col].notna().any():
                    max_comments = max(df[comments_col].max(), 1)
                
                self.site_stats[site_name] = {
                    'max_views': max_views,
                    'max_comments': max_comments
                }
                
                print(f"   {site_name}: 최고 조회수 {max_views:,}, 최고 댓글 {max_comments}")
    
    def calculate_hot_score(self, views, comments, source):
        """화제성 점수 계산 (최대 11점)"""
        if source not in self.site_stats:
            return 0.0
        
        stats = self.site_stats[source]
        
        # 조회수 점수 (최대 1점)
        view_score = min(views / stats['max_views'], 1.0)
        
        # 댓글 점수 (최대 10점)  
        comment_score = min((comments / stats['max_comments']) * 10, 10.0)
        
        # 총합 (최대 11점)
        total_score = view_score + comment_score
        
        return round(total_score, 2)

def setup_chrome_for_github_actions():
    """GitHub Actions 환경에 맞는 Chrome 설정"""
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-logging")
    opts.add_argument("--disable-web-security")
    opts.add_argument("--remote-debugging-port=9222")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    
    # GitHub Actions에서 chromium 사용
    opts.binary_location = "/usr/bin/chromium-browser"
    
    # 메모리 최적화
    opts.add_argument("--memory-pressure-off")
    opts.add_argument("--max_old_space_size=2048")
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    
    return driver

def upload_to_google_drive(df, filename, folder_id):
    """Google Drive에 DataFrame을 CSV로 업로드"""
    try:
        from googleapiclient.discovery import build
        from google.oauth2.service_account import Credentials
        from googleapiclient.http import MediaIoBaseUpload
        
        # 환경변수에서 Google 인증 정보 가져오기
        credentials_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not credentials_json:
            raise ValueError("GOOGLE_CREDENTIALS 환경변수가 설정되지 않았습니다")
            
        credentials_info = json.loads(credentials_json)
        credentials = Credentials.from_service_account_info(credentials_info)
        
        service = build('drive', 'v3', credentials=credentials)
        
        # DataFrame을 CSV로 변환
        csv_buffer = BytesIO()
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        csv_buffer.write(csv_data.encode('utf-8-sig'))
        csv_buffer.seek(0)
        
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(
            csv_buffer,
            mimetype='text/csv',
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,webViewLink'
        ).execute()
        
        logger.info(f"✅ Google Drive 업로드 성공: {filename}")
        logger.info(f"🔗 파일 링크: {file.get('webViewLink')}")
        
        return file.get('id')
        
    except Exception as e:
        logger.error(f"❌ Google Drive 업로드 실패: {e}")
        raise

def run_classification(df):
    """크롤링 결과에 분류 추가"""
    try:
        # simple.py의 분류 모델 로드 및 실행
        logger.info("🤖 게시글 분류 시작...")
        
        # 임시 CSV 파일 생성
        temp_file = "temp_predict.csv"
        df[['title']].to_csv(temp_file, index=False, header=False, encoding='utf-8-sig')
        
        # 분류 실행
        from simple import classify_file
        classify_file(temp_file, "temp_predicted.csv", "news_model.joblib")
        
        # 결과 읽기
        classified_df = pd.read_csv("temp_predicted.csv", encoding='utf-8-sig')
        
        # 원본 데이터에 분류 결과 추가
        df['predicted_category'] = classified_df['pred']
        
        # 임시 파일 삭제
        os.remove(temp_file)
        os.remove("temp_predicted.csv")
        
        logger.info(f"✅ 분류 완료: {len(df)}개 게시글")
        return df
        
    except Exception as e:
        logger.error(f"⚠️ 분류 실패: {e}")
        logger.info("분류 없이 원본 데이터 반환")
        return df

def main_github_actions():
    """GitHub Actions용 메인 함수"""
    try:
        logger.info("🚀 GitHub Actions 크롤링 시작")
        
        # 환경변수 확인
        folder_id = os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
        if not folder_id:
            raise ValueError("GOOGLE_DRIVE_FOLDER_ID 환경변수가 설정되지 않았습니다")
        
        # 타겟 날짜 설정
        today_kst = datetime.now(KST).date()
        yesterday = today_kst - timedelta(days=1)
        target_date = yesterday.strftime("%m%d")
        logger.info(f"📅 타겟 날짜: {target_date}")
        
        # 기존 크롤링 함수들을 import
        from crawling import (
            crawl_dcinside_requests,
            crawl_fmkorea_selenium_simple,
            crawl_theqoo_requests,
            crawl_instiz_requests,
            calculate_hot_scores
        )
        
        # 각 사이트별 크롤링 실행
        all_results = {}
        hot_calc = HotScoreCalculator()
        
        logger.info("📊 디시인사이드 크롤링...")
        try:
            dc_df = crawl_dcinside_requests(target_date)
            all_results['디시인사이드'] = dc_df
            logger.info(f"✅ 디시인사이드: {len(dc_df)}개")
        except Exception as e:
            logger.error(f"❌ 디시인사이드 실패: {e}")
            all_results['디시인사이드'] = pd.DataFrame()
        
        logger.info("📊 FM코리아 크롤링...")
        try:
            fm_df = crawl_fmkorea_selenium_simple(target_date)
            all_results['FM코리아'] = fm_df
            logger.info(f"✅ FM코리아: {len(fm_df)}개")
        except Exception as e:
            logger.error(f"❌ FM코리아 실패: {e}")
            all_results['FM코리아'] = pd.DataFrame()
        
        logger.info("📊 더쿠 크롤링...")
        try:
            theqoo_df = crawl_theqoo_requests(target_date)
            all_results['더쿠'] = theqoo_df
            logger.info(f"✅ 더쿠: {len(theqoo_df)}개")
        except Exception as e:
            logger.error(f"❌ 더쿠 실패: {e}")
            all_results['더쿠'] = pd.DataFrame()
        
        logger.info("📊 인스티즈 크롤링...")
        try:
            instiz_df = crawl_instiz_requests(target_date)
            all_results['인스티즈'] = instiz_df
            logger.info(f"✅ 인스티즈: {len(instiz_df)}개")
        except Exception as e:
            logger.error(f"❌ 인스티즈 실패: {e}")
            all_results['인스티즈'] = pd.DataFrame()
        
        # 화제성 점수 계산
        logger.info("🔥 화제성 점수 계산...")
        calculate_hot_scores(all_results, hot_calc)
        
        # 데이터 통합
        combined_data = []
        total_count = 0
        
        for site_name, df in all_results.items():
            if len(df) > 0:
                combined_data.append(df)
                total_count += len(df)
        
        if not combined_data:
            logger.warning("⚠️ 크롤링된 데이터가 없습니다")
            return {'success': False, 'error': 'No data crawled'}
        
        # 최종 DataFrame 생성
        final_df = pd.concat(combined_data, ignore_index=True)
        final_df = final_df.sort_values('hot_score', ascending=False)
        
        logger.info(f"📊 총 {total_count}개 게시글 수집")
        
        # 게시글 분류 추가 (선택사항)
        try:
            final_df = run_classification(final_df)
        except Exception as e:
            logger.warning(f"분류 실패, 원본 데이터 사용: {e}")
        
        # 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"community_crawling_{target_date}_{timestamp}.csv"
        
        # Google Drive에 업로드
        file_id = upload_to_google_drive(final_df, filename, folder_id)
        
        # 결과 요약
        logger.info("🎉 크롤링 완료!")
        logger.info(f"📁 파일명: {filename}")
        logger.info(f"📊 총 게시글: {len(final_df)}개")
        
        # 사이트별 통계
        site_stats = final_df['source'].value_counts()
        for site, count in site_stats.items():
            logger.info(f"   - {site}: {count}개")
        
        # 화제성 통계
        if 'hot_score' in final_df.columns:
            avg_score = final_df['hot_score'].mean()
            max_score = final_df['hot_score'].max()
            high_score_count = len(final_df[final_df['hot_score'] >= 5.5])
            
            logger.info(f"🔥 화제성 통계:")
            logger.info(f"   - 평균 점수: {avg_score:.2f}")
            logger.info(f"   - 최고 점수: {max_score:.2f}")
            logger.info(f"   - 고화제성(5.5+): {high_score_count}개")
        
        return {
            'success': True,
            'filename': filename,
            'file_id': file_id,
            'total_count': len(final_df),
            'date': target_date,
            'site_stats': site_stats.to_dict()
        }
        
    except Exception as e:
        logger.error(f"❌ 전체 프로세스 실패: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    result = main_github_actions()
    
    if result['success']:
        print(f"✅ 크롤링 성공: {result['filename']}")
        print(f"📊 총 {result['total_count']}개 게시글")
    else:
        print(f"❌ 크롤링 실패: {result['error']}")
        sys.exit(1)