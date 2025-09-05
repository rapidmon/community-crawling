from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from datetime import datetime
import numpy as np
import multiprocessing as mp
from datetime import datetime, timedelta

def is_today_post(date_str, target_date):
    """당일 게시물인지 확인 (시간 형태는 당일로 간주)"""
    try:
        today = datetime.today()
        
        # 시간 형태 (HH:MM)면 당일로 간주
        if ':' in date_str and not re.search(r'\d{2}\.\d{2}', date_str):
            today_mmdd = today.strftime("%m%d")
            return target_date == today_mmdd
        
        # 날짜 형태에서 MMDD 추출
        date_digits = re.sub(r'[^\d]', '', date_str)[-4:]
        return target_date == date_digits
    except:
        return False

def crawl_dcinside_requests(target_date):    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    results = []
    page = 1
    started_collecting = False
    
    def should_stop_crawling(date_str, target_date):
        # 시간 형태면 계속 진행
        if ':' in date_str and not re.search(r'\d{2}\.\d{2}', date_str):
            return False
        
        try:
            date_digits = re.sub(r'[^\d]', '', date_str)[-4:]
            return date_digits < target_date
        except:
            return False
    
    while True: 
        try:
            url = f"https://gall.dcinside.com/board/lists/?id=dcbest&page={page}&list_num=100&_dcbest=9"
            response = session.get(url, timeout=60)
            
            if response.status_code != 200:
                print(f"❌ {page}페이지 요청 실패: {response.status_code}")
                break
                
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.select('tr.ub-content')
            
            if page == 1:
                rows = rows[2:]
            else:
                rows = rows[1:]
                
            if not rows:
                print(f"{page}페이지: 게시물 없음, 크롤링 종료")
                break
            
            # 해당 페이지의 모든 날짜 먼저 확인
            page_dates = []
            for row in rows:
                try:
                    date_tag = row.select_one('td.gall_date')
                    date = date_tag.get_text(strip=True) if date_tag else ''
                    page_dates.append(date)
                except:
                    continue
            
            # 해당 페이지에 target_date가 있는지 확인
            has_target_date = any(is_today_post(date, target_date) for date in page_dates)
            
            # 모든 날짜가 target_date보다 이전이면 중단
            all_dates_before_target = all(should_stop_crawling(date, target_date) for date in page_dates if date)
            
            if all_dates_before_target and started_collecting:
                print(f"{page}페이지: 모든 게시물이 목표 날짜 이전. 크롤링 종료")
                break
            
            if has_target_date:
                started_collecting = True
                print(f"{page}페이지: 목표 날짜 발견, 수집 시작")
                
                for row in rows:
                    try:
                        # 날짜 먼저 확인
                        date_tag = row.select_one('td.gall_date')
                        date = date_tag.get_text(strip=True) if date_tag else ''
                        
                        if not is_today_post(date, target_date):
                            continue
                            
                        # 기본 정보 추출
                        title_tag = row.select_one('td.gall_tit.ub-word a')
                        title_raw = title_tag.get_text(strip=True) if title_tag else ''
                        post_url = title_tag.get('href') if title_tag else ''
                        
                        if post_url and not post_url.startswith('http'):
                            post_url = f"https://gall.dcinside.com{post_url}"
                        
                        title = re.sub(r'^[\[\(][^\]\)]{1,3}[\]\)]\s*', '', title_raw)
                        
                        view_tag = row.select_one('td.gall_count')
                        view = int(view_tag.text.replace(',', '').strip()) if view_tag and view_tag.text.strip().isdigit() else 0
                        
                        comment_tag = row.select_one('a.reply_numbox span.reply_num')
                        comment = 0
                        if comment_tag:
                            match = re.search(r'\[(\d+)', comment_tag.text.strip())
                            if match:
                                comment = int(match.group(1))
                        
                        results.append({
                            'title': title,
                            'url': post_url,
                            'date': date,
                            'source': '디시인사이드',
                            'content': '',  # requests 방식에서는 본문 없음
                            'views': view,
                            'comments': comment
                        })
                        
                    except Exception as e:
                        continue
            else:
                print(f"⏭️ {page}페이지: 목표 날짜 없음, 스킵")
                
            page += 1
            time.sleep(random.uniform(0.5, 1.0))  # 요청 간격
            
            if len(results) > 300:
                print(f"🔚 결과 수 제한 (300개) 도달, 크롤링 중단")
                break
            
        except Exception as e:
            print(f"⚠️ 디시인사이드 {page}페이지 오류: {e}")
            page += 1
            continue
    
    df = pd.DataFrame(results)
    print(f"✅ 디시인사이드 크롤링 완료 (총 {len(df)}건)")
    return df

def crawl_fmkorea_selenium_simple(target_date):    
    driver = setup_driver()
    results = []

    def get_views_from_post(driver, url, wait_sec=10):
        origin = driver.current_window_handle
        try:
            # 새 탭으로 열기 (뒤로가기보다 안정적)
            driver.execute_script("window.open(arguments[0], '_blank');", url)
            driver.switch_to.window(driver.window_handles[-1])

            # 상세 페이지 로드 대기: side 영역 등장
            WebDriverWait(driver, wait_sec).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.side.fr span"))
            )

            # 보통 '조회 1,234' 형태. 여러 span 중 '조회' 포함 텍스트를 우선 파싱
            spans = driver.find_elements(By.CSS_SELECTOR, "div.side.fr span")
            views = 0
            for s in spans:
                t = s.text.strip()
                m = re.search(r'조회\s*([\d,]+)', t)
                if m:
                    views = int(m.group(1).replace(",", ""))
                    break

            # 위 패턴이 없으면 첫 span에서 숫자만 추출(백업)
            if views == 0 and spans:
                m = re.search(r'([\d,]+)', spans[0].text)
                if m:
                    views = int(m.group(1).replace(",", ""))

            # 탭 정리
            driver.close()
            driver.switch_to.window(origin)
            return views

        except Exception:
            # 문제 생겨도 세션 복구
            try:
                if len(driver.window_handles) > 1:
                    driver.close()
            finally:
                driver.switch_to.window(origin)
            return 0
    
    def extract_date_mmdd(date_text):
        date_text = str(date_text).strip()
        now = datetime.now(KST)
        
        # HH:MM 형식 확인
        if ':' in date_text and not re.search(r'\d{2,4}[.\-/]\d{2}[.\-/]\d{2}', date_text):
            time_match = re.search(r'(\d{1,2}):(\d{2})', date_text)
            if time_match:
                hour, minute = int(time_match.group(1)), int(time_match.group(2))
                
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    post_time_today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    if post_time_today > now:
                        yesterday = now - timedelta(days=1)
                        return yesterday.strftime("%m%d")
                    else:
                        return now.strftime("%m%d")
        
        # 전체 날짜 형식 (YYYY.MM.DD)
        full_match = re.search(r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})', date_text)
        if full_match:
            _, month, day = full_match.groups()
            return f"{int(month):02d}{int(day):02d}"
    
    def get_page_last_date(page_num):
            try:
                url = f"https://www.fmkorea.com/index.php?mid=best&page={page_num}"
                driver.get(url)
                
                WebDriverWait(driver, 6).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.li"))
                )
                time.sleep(0.4)
                
                posts = driver.find_elements(By.CSS_SELECTOR, "div.li")
                if not posts:
                    return None

                for post in reversed(posts):
                    try:
                        date_elem = post.find_element(By.CSS_SELECTOR, "span.regdate")
                        html = date_elem.get_attribute('innerHTML') or ""
                        m = re.search(r'<!--\s*(\d{1,2}:\d{2})\s*-->', html)
                        date_text = (m.group(1).strip() if m else date_elem.text.strip())

                        return extract_date_mmdd(date_text)
                        
                    except Exception:
                        continue
                    
                return None
                
            except Exception as e:
                print(f"페이지 {page_num} 확인 실패: {e}")
                return None
            
    def find_start_page_by_regdate(target_date: str, start_page: int) -> int:
        page = start_page
        
        while True:
            last_date = get_page_last_date(page)
            if not last_date:
                page += 1
                continue
            
            # 날짜 비교
            if last_date > target_date:
                page += 1
                continue
            elif last_date < target_date:
                page = max(1, page - 1)
                continue
            else:
                break
        
        print(f"시작 페이지 확정: p{page}")
        return page

    start_page = find_start_page_by_regdate(target_date, start_page=5)

    page = start_page
    step = 0

    while True:
        step += 1
        url = f"https://www.fmkorea.com/index.php?mid=best&page={page}"
        driver.get(url)
        time.sleep(2.0)

        posts = driver.find_elements(By.CSS_SELECTOR, "div.li")
        if not posts:
            print(f"📄 p{page}: 게시물 없음 → 종료")
            break

        page_count = 0
        found_target_on_page = False

        for post in posts:
            try:
                date_elem = post.find_element(By.CSS_SELECTOR, "span.regdate")
                html = date_elem.get_attribute('innerHTML') or ""
                m = re.search(r'<!--\s*(\d{1,2}:\d{2})\s*-->', html)
                date_text = (m.group(1).strip() if m else date_elem.text.strip())

                mmdd = extract_date_mmdd(date_text)
                if mmdd != target_date:
                    continue  # 어제 것만

                found_target_on_page = True
                page_count += 1

                title_elem = post.find_element(By.CSS_SELECTOR, "h3.title a")
                title_text = title_elem.text.strip()
                post_url = title_elem.get_attribute('href')

                cmtm = re.search(r'\[(\d+)\]', title_text)
                comments = int(cmtm.group(1)) if cmtm else 0
                clean_title = re.sub(r'\s*\[\d+\]$', '', title_text)

                views = get_views_from_post(driver, post_url)

                results.append({
                    'title': clean_title,
                    'url': post_url,
                    'date': date_text,
                    'source': 'FM코리아',
                    'content': '',
                    'views': views,
                    'comments': comments
                })
            except Exception:
                continue

        if found_target_on_page:
            print(f"✅ p{page}: {page_count}개 수집")
            page += 1
        else:
            print(f"⭐ p{page}: 어제 게시물 없음 → 수집 종료")
            break

    driver.quit()

    df = pd.DataFrame(results)
    print(f"{len(df)}개 수집")
    return df

def crawl_theqoo_selenium(target_date):
    results = []
    target_page = 1

    def extract_date_mmdd_theqoo(date_text):
        if ':' in date_text and not re.search(r'\d{2,4}\.\d{2}\.\d{2}', date_text):
            return datetime.today().strftime("%m%d")
        
        month_day_match = re.search(r'(\d{1,2})[\.\-/](\d{1,2})', date_text)
        if month_day_match:
            month, day = month_day_match.groups()
            return f"{int(month):02d}{int(day):02d}"
        
        return "0000"

    def crawl_single_page(page_num):        
        driver = setup_driver()
        page_results = []
        
        try:
            url = f"https://theqoo.net/hot?page={page_num}"            
            driver.get(url)
            
            # 페이지 로딩 대기
            time.sleep(random.uniform(3, 6))
            
            # 페이지 로드 대기
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.theqoo_board_table"))
                )
                
                # 스크롤로 lazy loading 요소 활성화
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
            except:
                print(f"{page_num}페이지 로드 실패")
                return [], False
            
            rows = driver.find_elements(
                By.CSS_SELECTOR, 
                "table.theqoo_board_table tbody tr:not(.notice):not(.notice_expand)"
            )
            
            if not rows:
                print(f"{page_num}페이지: 게시물 없음")
                return [], False
                        
            page_count = 0
            found_target_date = False
            
            for row in rows:
                try:
                    # 공지사항 추가 필터링
                    try:
                        class_attr = row.get_attribute('class') or ''
                        data_attr = row.get_attribute('data-permanent-notice') or ''
                        if ('notice' in class_attr.lower() or 
                            data_attr == 'Y' or
                            'sticky' in class_attr.lower()):
                            continue
                    except:
                        pass
                    
                    # 날짜 추출
                    try:
                        time_elem = row.find_element(By.CSS_SELECTOR, "td.time")
                        date_text = time_elem.text.strip()
                    except:
                        continue
                    
                    if not date_text:
                        continue
                    
                    post_mmdd = extract_date_mmdd_theqoo(date_text)
                    
                    if post_mmdd == target_date:
                        found_target_date = True
                        page_count += 1
                        
                        try:
                            # 제목과 URL
                            title_elem = row.find_element(By.CSS_SELECTOR, "td.title a[href]")
                            title_text = title_elem.text.strip()
                            post_url = title_elem.get_attribute('href')
                            
                            if not title_text:
                                continue
                            
                            if post_url and not post_url.startswith('http'):
                                post_url = f"https://theqoo.net{post_url}"
                            
                            # 댓글 수 (안전하게)
                            comments = 0
                            try:
                                reply_elem = row.find_element(By.CSS_SELECTOR, "td.title a.replyNum")
                                comment_text = reply_elem.text.strip()
                                comment_match = re.search(r'(\d+)', comment_text)
                                if comment_match:
                                    comments = int(comment_match.group(1))
                            except:
                                comments = 0
                            
                            # 조회수 (안전하게)
                            views = 0
                            try:
                                views_elem = row.find_element(By.CSS_SELECTOR, "td.m_no")
                                views_text = views_elem.text.strip().replace(",", "")
                                if views_text.isdigit():
                                    views = int(views_text)
                            except:
                                views = 0
                            
                            page_results.append({
                                'title': title_text,
                                'url': post_url,
                                'date': date_text,
                                'source': '더쿠',
                                'content': '',
                                'views': views,
                                'comments': comments
                            })
                            
                        except Exception as e:
                            continue
                        
                except Exception:
                    continue
            return page_results, found_target_date
            
        except Exception as e:
            print(f"{page_num}페이지 처리 중 오류: {e}")
            return [], False
        
        finally:
            try:
                driver.quit()
            except:
                pass
    
    # 메인 크롤링 루프
    consecutive_empty_pages = 0
    
    while True:
        # 페이지 간 랜덤 대기 (봇 탐지 회피)
        if True:
            wait_time = random.uniform(5, 10)
            time.sleep(wait_time)
        
        # 단일 페이지 크롤링 (새 세션)
        page_results, found_target = crawl_single_page(target_page)
        
        # 결과 누적
        results.extend(page_results)
        
        if found_target and len(page_results) > 0:
            consecutive_empty_pages = 0
            target_page += 1
        else:
            consecutive_empty_pages += 1
            
            if consecutive_empty_pages >= 2:
                break
                
            target_page += 1
    
    df = pd.DataFrame(results)
    print(f"\n더쿠 크롤링 완료 총 {len(df)}개 수집")
    return df

def crawl_instiz_requests(target_date):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    results = []
    today_str = datetime.today().strftime('%m.%d')
    
    for page in range(1, 31):  # 30페이지까지
        try:
            url = f"https://www.instiz.net/pt?page={page}&srt=3&srd=4"
            response = session.get(url, timeout=120)
            
            if response.status_code != 200:
                print(f"{page}페이지 요청 실패: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.select('td.listsubject')
            
            page_results = []
            target_date_found = False
            
            for row in rows:
                try:
                    if not any(cls.startswith('r') for cls in row.get('class', [])):
                        continue

                    title_link = row.select_one('a')
                    if not title_link:
                        continue

                    # a 태그 안의 div.sbj에서 제목 추출
                    title_raw = title_link.select_one('div.sbj')
                    if not title_raw:
                        continue

                    # 날짜 먼저 확인
                    info_elem = row.select_one('div.listno.regdate')
                    if not info_elem:
                        continue
                        
                    info_text = info_elem.get_text(" ", strip=True)
                    if ':' in info_text and not re.search(r'\d{2}\.\d{2}', info_text):
                        date = today_str
                    else:
                        date_match = re.search(r'\d{2}\.\d{2}', info_text)
                        date = date_match.group() if date_match else today_str

                    # 해당 날짜가 아니면 즉시 스킵
                    if not is_today_post(date, target_date):
                        continue

                    target_date_found = True

                    # URL은 이미 위에서 찾은 title_link에서 추출
                    post_url = title_link.get('href', '')

                    # 절대 경로 변환
                    if post_url and not post_url.startswith('http'):
                        if post_url.startswith('/'):
                            post_url = f"https://www.instiz.net{post_url}"
                        else:
                            post_url = f"https://www.instiz.net/{post_url}"

                    title_text = title_raw.get_text(" ", strip=True)
                    comment_tag = title_raw.select_one('span.cmt2')
                    comments = int(comment_tag.get_text(strip=True)) if comment_tag else 0
                    title = re.sub(r'\s*\[\d+\]$', '', title_text.split('(', 1)[0].strip())

                    views_match = re.search(r'조회\s([\d,]+)', info_text)
                    views = int(views_match.group(1).replace(',', '')) if views_match else 0

                    page_results.append({
                        'title': title,
                        'url': post_url,
                        'date': date,
                        'source': '인스티즈',
                        'content': '',  # requests 방식에서는 본문 없음
                        'views': views,
                        'comments': comments
                    })
                    
                except Exception:
                    continue
            
            results.extend(page_results)
            time.sleep(random.uniform(5.0, 10.0))  # 요청 간격
                
        except Exception as e:
            print(f"인스티즈 {page}페이지 오류: {e}")
            continue
    
    df = pd.DataFrame(results)
    print(f"인스티즈 크롤링 완료 (총 {len(df)}건)")
    return df

def calculate_hot_scores(data, hot_calc):
    """화제성 점수 계산 (필터링 없이 전체)"""
    print("\n🔥 화제성 점수 계산 중...")
    
    # 1️⃣ 먼저 모든 사이트의 최고값 수집
    hot_calc.collect_stats(data)
    
    # 2️⃣ 각 사이트별로 화제성 점수 계산 (필터링 없음)
    for site_name, df in data.items():
        if len(df) > 0:
            print(f"📊 {site_name} 화제성 점수 계산 중...")
            df['hot_score'] = df.apply(
                lambda row: hot_calc.calculate_hot_score(
                    row.get('views', 0), 
                    row.get('comments', 0), 
                    row['source']
                ), axis=1
            )
            
            # 전체 게시물 유지 (필터링 제거)
            print(f"   전체: {len(df)}개 게시물")
            if len(df) > 0:
                print(f"   평균 화제성: {df['hot_score'].mean():.2f}")
                print(f"   최고 화제성: {df['hot_score'].max():.2f}")
                print(f"   최저 화제성: {df['hot_score'].min():.2f}")
    
    print("✅ 화제성 점수 계산 완료!")
    return data
