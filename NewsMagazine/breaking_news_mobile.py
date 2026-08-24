from datetime import datetime
import os
import webbrowser
import feedparser

# 주요 언론사 RSS 피드 주소 리스트
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
    error_logs = {}
    
    for press_name, rss_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(rss_url)
            if not feed.entries:
                error_logs[press_name] = "데이터 없음 또는 접근 거부"
                continue
                
            success_count = 0
            for entry in feed.entries:
                title = getattr(entry, 'title', '').strip()
                link = getattr(entry, 'link', '').strip()
                
                if not title or not link or title in seen_titles:
                    continue
                
                if len(collected_news) < 10:
                    collected_news.append({
                        "press": press_name,
                        "title": title,
                        "link": link
                    })
                    seen_titles.add(title)
                
                success_count += 1
                break
                
            if success_count == 0:
                error_logs[press_name] = "유효한 기사 없음"
                
        except Exception as e:
            error_logs[press_name] = str(e)

    # 10개가 안 채워졌을 때 추가 수집
    if len(collected_news) < 10:
        for press_name, rss_url in RSS_FEEDS.items():
            if len(collected_news) >= 10:
                break
            if press_name in error_logs:
                continue
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries:
                    if len(collected_news) >= 10:
                        break
                    title = getattr(entry, 'title', '').strip()
                    link = getattr(entry, 'link', '').strip()
                    
                    if not title or not link or title in seen_titles:
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
    
    error_html = ""
    if error_logs:
        error_items = "".join([f"<li><b>{press}</b>: {reason}</li>" for press, reason in error_logs.items()])
        error_html = f"""
        <div class="error-section">
            <h3>⚠️ 수집 실패 또는 점검 중인 언론사</h3>
            <ul>
                {error_items}
            </ul>
        </div>
        """

    # 모바일 최적화 CSS 적용 (viewport 및 반응형 레이아웃)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>모바일 실시간 속보 TOP 10</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
                background-color: #f0f2f5; 
                margin: 0; 
                padding: 10px; 
            }}
            .container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                background: white; 
                padding: 15px; 
                border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.05); 
            }}
            h1 {{ 
                color: #1a1a1a; 
                text-align: center; 
                font-size: 20px; 
                margin-bottom: 5px; 
            }}
            .subtitle {{ 
                text-align: center; 
                color: #666; 
                font-size: 12px; 
                margin-bottom: 20px; 
            }}
            .news-item {{ 
                padding: 12px 5px; 
                border-bottom: 1px solid #eee; 
                display: flex; 
                flex-direction: column;
                gap: 6px;
            }}
            .news-item:last-child {{ border-bottom: none; }}
            .news-header {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .rank {{ 
                font-weight: bold; 
                color: #e74c3c; 
                font-size: 16px; 
                min-width: 20px; 
            }}
            .press {{ 
                background: #007aff; 
                color: white; 
                padding: 2px 6px; 
                border-radius: 4px; 
                font-size: 11px; 
                font-weight: bold; 
            }}
            .title a {{ 
                text-decoration: none; 
                color: #222; 
                font-size: 14px; 
                font-weight: 500; 
                line-height: 1.4;
                display: block;
                word-break: keep-all;
            }}
            .title a:active {{ color: #007aff; }}
            
            /* 하단 에러 로그 스타일 */
            .error-section {{ 
                margin-top: 25px; 
                padding-top: 15px; 
                border-top: 1px dashed #ddd; 
                color: #888; 
            }}
            .error-section h3 {{ font-size: 11px; color: #e67e22; margin-bottom: 5px; }}
            .error-section ul {{ font-size: 10px; padding-left: 15px; line-height: 1.4; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚨 모바일 실시간 속보 TOP 10</h1>
            <div class="subtitle">{today_formatted} 기준 (중복 배제 완료)</div>
            <div class="news-list">
    """
    
    for idx, item in enumerate(news_list, 1):
        html_content += f"""
                <div class="news-item">
                    <div class="news-header">
                        <span class="rank">{idx}</span>
                        <span class="press">{item['press']}</span>
                    </div>
                    <div class="title"><a href="{item['link']}" target="_blank">{item['title']}</a></div>
                </div>
        """
        
    html_content += f"""
            </div>
            {error_html}
        </div>
    </body>
    </html>
    """
    
    filename = "mobile_breaking_news.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    abs_path = os.path.abspath(filename)
    webbrowser.open(f"file://{abs_path}")
    print(f"[*] 모바일 최적화 속보 페이지가 생성되었습니다!")

if __name__ == "__main__":
    news, errors = get_diverse_breaking_news()
    if news:
        create_html_and_open(news, errors)
    else:
        print("[-] 수집된 뉴스가 없습니다.")