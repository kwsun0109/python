from datetime import datetime
import os
import webbrowser
import feedparser

# 점검할 주요 언론사 RSS 피드 주소 리스트
RSS_FEEDS = {
    "KBS": "https://world.kbs.co.kr/rss/rss_news.xml?lang=k",
    "SBS": "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01&plink=RSS&cooper=NAVER",
    "MBC": "https://imnews.imbc.com/rss/news/news_00.xml",
    "조선일보": "https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml",
    "중앙일보": "https://rss.joins.com/joins_news_list.xml",
    "동아일보": "https://rss.donga.com/total.xml",
    "머니투데이": "https://rss.mt.co.kr/mt_news.xml",
    "아시아경제": "https://www.asiae.co.kr/rss/",
    "이데일리": "https://rss.edaily.co.kr/edaily_news.xml",
    "연합뉴스": "https://www.yna.co.kr/rss/news.xml",
    "한국경제": "https://www.hankyung.com/feed/all-news",
    "서울신문": "https://www.seoul.co.kr/rss/rss.xml",
    "한겨레": "https://www.hani.co.kr/rss/",
    "경향신문": "https://www.khan.co.kr/rss/rssdata/total_news.xml",
    "매일경제": "https://www.mk.co.kr/rss/30000001/",
}

def get_diverse_breaking_news():
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"[*] 오늘 날짜 ({today_str}) 기준 속보 수집 중...")
    
    collected_news = []
    seen_titles = set()
    error_logs = {}  # 언론사별 에러 내역을 담을 딕셔너리
    
    # 1단계: 각 언론사별로 순회하며 수집 시도
    for press_name, rss_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(rss_url)
            
            # feedparser는 에러가 나도 객체를 반환하므로 entries가 비어있거나 status 체크
            if not feed.entries:
                error_logs[press_name] = "데이터(Entries)가 비어있거나 접근이 거부되었습니다."
                continue
                
            # 정상 수집된 경우 중복 체크 후 1개 담기
            success_count = 0
            for entry in feed.entries:
                title = getattr(entry, 'title', '').strip()
                link = getattr(entry, 'link', '').strip()
                
                if not title or not link:
                    continue
                    
                if title in seen_titles:
                    continue
                
                # 아직 10개가 안 채워졌거나, 10개가 채워졌어도 언론사별 첫 대표 기사는 수집 목록에 활용 가능
                if len(collected_news) < 10:
                    collected_news.append({
                        "press": press_name,
                        "title": title,
                        "link": link
                    })
                    seen_titles.add(title)
                
                success_count += 1
                break # 언론사당 대표 1개씩 우선 확보
                
            if success_count == 0:
                error_logs[press_name] = "유효한 기사 항목을 찾지 못했습니다."
                
        except Exception as e:
            # 예외 발생 시 에러 사유 기록
            error_logs[press_name] = str(e)

    # 만약 수집된 뉴스가 10개 미만이라면, 기존에 성공한 언론사에서 추가로 가져와서 10개를 채움
    if len(collected_news) < 10:
        for press_name, rss_url in RSS_FEEDS.items():
            if len(collected_news) >= 10:
                break
            if press_name in error_logs:
                continue # 에러 난 곳은 스킵
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries:
                    if len(collected_news) >= 10:
                        break
                    title = getattr(entry, 'title', '').strip()
                    link = getattr(entry, 'link', '').strip()
                    
                    if title in seen_titles:
                        continue
                        
                    collected_news.append({
                        "press": press_name,
                        "title": title,
                        "link": link
                    })
                    seen_titles.add(title)
            except:
                continue

    return collected_news[:10], error_logs

def create_html_and_open(news_list, error_logs):
    today_formatted = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
    
    # 에러 로그를 하단에 보여줄 HTML 문자열 생성
    error_html = ""
    if error_logs:
        error_items = "".join([f"<li><b>{press}</b>: {reason}</li>" for press, reason in error_logs.items()])
        error_html = f"""
        <div class="error-section">
            <h3>⚠️ 수집 실패 또는 점검 중인 언론사 안내</h3>
            <ul>
                {error_items}
            </ul>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>언론사별 골라보기 속보 TOP 10</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }}
            .container {{ max-width: 850px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; text-align: center; font-size: 24px; margin-bottom: 5px; }}
            .subtitle {{ text-align: center; color: #7f8c8d; font-size: 14px; margin-bottom: 30px; }}
            .news-item {{ padding: 15px 0; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; }}
            .news-item:last-child {{ border-bottom: none; }}
            .news-content {{ display: flex; align-items: center; gap: 15px; width: 85%; }}
            .rank {{ font-weight: bold; color: #e74c3c; font-size: 18px; width: 25px; text-align: center; }}
            .press {{ background: #2980b9; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; white-space: nowrap; font-weight: bold; }}
            .title a {{ text-decoration: none; color: #333; font-size: 15px; font-weight: 600; }}
            .title a:hover {{ color: #2980b9; text-decoration: underline; }}
            .time {{ font-size: 12px; color: #95a5a6; width: 15%; text-align: right; }}
            
            /* 하단 에러 로그 스타일 (작은 글씨) */
            .error-section {{ margin-top: 40px; padding-top: 20px; border-top: 1px dashed #ccc; color: #7f8c8d; }}
            .error-section h3 {{ font-size: 13px; color: #e67e22; margin-bottom: 8px; }}
            .error-section ul {{ font-size: 11px; padding-left: 20px; line-height: 1.5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📰 주요 언론사별 대표 속보 TOP 10</h1>
            <div class="subtitle">기준 시각: {today_formatted} (중복 배제 완료)</div>
            <div class="news-list">
    """
    
    for idx, item in enumerate(news_list, 1):
        html_content += f"""
                <div class="news-item">
                    <div class="news-content">
                        <span class="rank">{idx}</span>
                        <span class="press">{item['press']}</span>
                        <span class="title"><a href="{item['link']}" target="_blank">{item['title']}</a></span>
                    </div>
                    <div class="time">속보</div>
                </div>
        """
        
    html_content += f"""
            </div>
            {error_html}
        </div>
    </body>
    </html>
    """
    
    filename = "breaking_news_with_log.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    abs_path = os.path.abspath(filename)
    webbrowser.open(f"file://{abs_path}")
    print(f"[*] 브라우저에 속보 및 에러 로그 페이지가 열렸습니다!")

if __name__ == "__main__":
    news, errors = get_diverse_breaking_news()
    if news:
        create_html_and_open(news, errors)
    else:
        print("[-] 수집된 뉴스가 없습니다.")