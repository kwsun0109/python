from datetime import datetime
import os
import webbrowser
import feedparser

# 요청하신 15개 주요 언론사 RSS 피드 주소 리스트
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
    print(f"[*] 오늘 날짜 ({today_str}) 기준 15개 언론사 속보 수집 중...")
    
    collected_news = []
    seen_titles = set()
    
    # 언론사별로 순회하며 딱 1개씩만 추출 (최대 10개 채우기)
    for press_name, rss_url in RSS_FEEDS.items():
        if len(collected_news) >= 10:
            break
            
        try:
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries:
                title = entry.title.strip()
                link = entry.link.strip()
                
                # 중복 제목 검사
                if title in seen_titles:
                    continue
                
                collected_news.append({
                    "press": press_name,
                    "title": title,
                    "link": link
                })
                
                seen_titles.add(title)
                break  # 해당 언론사에서 1개를 가져왔으므로 다음 언론사로 이동
                
        except Exception as e:
            print(f"[-] {press_name} RSS 수집 중 오류 발생: {e}")

    return collected_news

def create_html_and_open(news_list):
    today_formatted = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
    
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📰 주요 언론사별 대표 속보 TOP 10</h1>
            <div class="subtitle">기준 시각: {today_formatted} (언론사별 1개씩 골고루 추출 & 중복 배제)</div>
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
        
    html_content += """
            </div>
        </div>
    </body>
    </html>
    """
    
    filename = "all_press_breaking_news.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    abs_path = os.path.abspath(filename)
    webbrowser.open(f"file://{abs_path}")
    print(f"[*] 브라우저에 속보 페이지가 성공적으로 열렸습니다!")

if __name__ == "__main__":
    news = get_diverse_breaking_news()
    if news:
        create_html_and_open(news)
    else:
        print("[-] 수집된 뉴스가 없습니다.")