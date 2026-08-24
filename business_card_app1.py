from flask import Flask, render_template_string, request, redirect, url_for
import json
import os
import re

app = Flask(__name__)
DATA_FILE = "business_cards.json"
ITEMS_PER_PAGE = 10  # 한 페이지에 보여줄 명함 개수

def load_cards():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_cards(cards):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=4)

# 전화번호 자동 하이픈(-) 포맷팅 함수
def format_phone_number(phone):
    if not phone:
        return ""
    # 숫자만 추출
    nums = re.sub(r'[^0-9]', '', phone)
    
    # 서울 지역번호(02)인 경우
    if nums.startswith('02'):
        if len(nums) == 9: # 02-XXX-XXXX
            return f"{nums[:2]}-{nums[2:5]}-{nums[5:]}"
        elif len(nums) == 10: # 02-XXXX-XXXX
            return f"{nums[:2]}-{nums[2:6]}-{nums[6:]}"
    # 일반 휴대폰 및 기타 지역번호 (010, 031 등)
    elif len(nums) == 8: # 1588-XXXX 등
        return f"{nums[:4]}-{nums[4:]}"
    elif len(nums) == 10: # 031-XXX-XXXX 등
        return f"{nums[:3]}-{nums[3:6]}-{nums[6:]}"
    elif len(nums) == 11: # 010-XXXX-XXXX 등
        return f"{nums[:3]}-{nums[3:7]}-{nums[7:]}"
    
    # 규칙에 맞지 않으면 원본 반환
    return phone

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>스마트 명함 지갑</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        function filterCards() {
            let input = document.getElementById('searchInput').value.toLowerCase();
            let cards = document.getElementsByClassName('business-card');
            
            for (let i = 0; i < cards.length; i++) {
                let text = cards[i].innerText.toLowerCase();
                if (text.includes(input)) {
                    cards[i].style.display = "";
                } else {
                    cards[i].style.display = "none";
                }
            }
        }

        function toggleEdit(index) {
            let viewMode = document.getElementById('view-mode-' + index);
            let editMode = document.getElementById('edit-mode-' + index);
            if (editMode.classList.contains('hidden')) {
                editMode.classList.remove('hidden');
                viewMode.classList.add('hidden');
            } else {
                editMode.classList.add('hidden');
                viewMode.classList.remove('hidden');
            }
        }
    </script>
</head>
<body class="bg-slate-100 text-slate-900 min-h-screen py-12 px-4 sm:px-6">
    <div class="max-w-5xl mx-auto">
        
        <!-- 상단 타이틀 -->
        <header class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-10 pb-6 border-b border-slate-200/60 gap-4">
            <div>
                <h1 class="text-2xl sm:text-3xl font-black tracking-tight text-slate-900">📇 인맥 명함 지갑</h1>
                <p class="text-sm text-slate-500 mt-1">직장 연락처 및 번호 자동 하이픈 기능이 적용된 스마트 명함 시스템</p>
            </div>
            <!-- 실시간 검색창 -->
            <div class="w-full sm:w-72">
                <input type="text" id="searchInput" onkeyup="filterCards()" placeholder="🔍 현재 페이지에서 검색..." 
                    class="w-full px-4 py-2.5 bg-white border border-slate-200/80 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 shadow-sm transition">
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <!-- 왼쪽: 새 명함 등록 폼 -->
            <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-200/60 h-fit">
                <h2 class="text-base font-bold text-slate-900 mb-5 pb-3 border-b border-slate-100 flex items-center gap-2">
                    <span>✨ 새 명함 추가하기</span>
                </h2>
                <form action="/add" method="POST" class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1.5">이름 *</label>
                        <input type="text" name="name" required placeholder="예: 홍길동" class="w-full px-4 py-2.5 text-sm bg-slate-50/50 border border-slate-200/80 rounded-xl focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-600 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1.5">회사명</label>
                        <input type="text" name="company" placeholder="예: (주)테크솔루션" class="w-full px-4 py-2.5 text-sm bg-slate-50/50 border border-slate-200/80 rounded-xl focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-600 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1.5">직책</label>
                        <input type="text" name="title" placeholder="예: 대표이사 / 매니저" class="w-full px-4 py-2.5 text-sm bg-slate-50/50 border border-slate-200/80 rounded-xl focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-600 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1.5">개인 연락처 * <span class="text-[10px] text-blue-600 font-normal">(자동 하이픈)</span></label>
                        <input type="text" name="phone" required placeholder="예: 01012345678" class="w-full px-4 py-2.5 text-sm bg-slate-50/50 border border-slate-200/80 rounded-xl focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-600 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1.5">직장 연락처 <span class="text-[10px] text-blue-600 font-normal">(자동 하이픈)</span></label>
                        <input type="text" name="office_phone" placeholder="예: 025558888" class="w-full px-4 py-2.5 text-sm bg-slate-50/50 border border-slate-200/80 rounded-xl focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-600 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1.5">이메일</label>
                        <input type="email" name="email" placeholder="예: example@email.com" class="w-full px-4 py-2.5 text-sm bg-slate-50/50 border border-slate-200/80 rounded-xl focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-600 transition">
                    </div>
                    <button type="submit" class="w-full mt-2 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl transition shadow-lg shadow-blue-600/20">
                        명함 안전하게 저장하기
                    </button>
                </form>
            </div>

            <!-- 오른쪽: 명함 카드 리스트 -->
            <div class="lg:col-span-2 space-y-4">
                <div class="flex justify-between items-center px-1">
                    <h2 class="text-sm font-bold text-slate-600 uppercase tracking-wider">등록된 명함 카드 <span class="text-blue-600 font-extrabold">({{ total_cards }}명)</span></h2>
                </div>

                {% if page_cards %}
                    <div id="cardContainer" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {% for card in page_cards %}
                        {% set actual_index = (current_page - 1) * 10 + loop.index0 %}
                        <div class="business-card bg-white p-6 rounded-3xl shadow-sm border border-slate-200/60 flex flex-col justify-between hover:shadow-xl transition duration-200">
                            
                            <!-- [1] 보기 모드 -->
                            <div id="view-mode-{{ actual_index }}">
                                <div class="flex justify-between items-start mb-2">
                                    <h3 class="font-black text-slate-900 text-lg">{{ card.name }}</h3>
                                    <span class="text-xs bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full font-bold">{{ card.title if card.title else '멤버' }}</span>
                                </div>
                                <p class="text-xs font-extrabold text-slate-400 uppercase tracking-wider mb-4">{{ card.company if card.company else '소속 없음' }}</p>
                                
                                <div class="space-y-2 text-xs text-slate-600 border-t border-slate-100 pt-4 mb-4">
                                    <p class="flex items-center gap-2 font-medium">📞 개인: <span class="text-slate-800">{{ card.phone }}</span></p>
                                    <p class="flex items-center gap-2 font-medium">🏢 직장: <span class="text-slate-800">{{ card.office_phone if card.office_phone else '등록된 직장 번호 없음' }}</span></p>
                                    <p class="flex items-center gap-2 font-medium truncate">✉️ 이메일: <span class="text-slate-800">{{ card.email if card.email else '등록된 이메일 없음' }}</span></p>
                                </div>

                                <div class="flex justify-end gap-2 pt-3 border-t border-slate-100">
                                    <button onclick="toggleEdit('{{ actual_index }}')" class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-bold transition">✏️ 수정</button>
                                    <a href="/delete/{{ actual_index }}" onclick="return confirm('정말 이 명함을 삭제하시겠습니까?');" class="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-lg text-xs font-bold transition">🗑️ 삭제</a>
                                </div>
                            </div>

                            <!-- [2] 수정 모드 -->
                            <div id="edit-mode-{{ actual_index }}" class="hidden">
                                <h3 class="font-bold text-slate-900 text-sm mb-3 pb-2 border-b border-slate-100">✏️ 명함 정보 수정</h3>
                                <form action="/update/{{ actual_index }}" method="POST" class="space-y-2.5">
                                    <input type="text" name="name" value="{{ card.name }}" required class="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200/80 rounded-lg">
                                    <input type="text" name="company" value="{{ card.company }}" placeholder="회사명" class="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200/80 rounded-lg">
                                    <input type="text" name="title" value="{{ card.title }}" placeholder="직책" class="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200/80 rounded-lg">
                                    <input type="text" name="phone" value="{{ card.phone }}" required placeholder="개인 연락처" class="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200/80 rounded-lg">
                                    <input type="text" name="office_phone" value="{{ card.office_phone if card.office_phone else '' }}" placeholder="직장 연락처" class="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200/80 rounded-lg">
                                    <input type="email" name="email" value="{{ card.email }}" placeholder="이메일" class="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200/80 rounded-lg">
                                    
                                    <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
                                        <button type="submit" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold">저장</button>
                                        <button type="button" onclick="toggleEdit('{{ actual_index }}')" class="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg text-xs font-bold">취소</button>
                                    </div>
                                </form>
                            </div>

                        </div>
                        {% endfor %}
                    </div>

                    <!-- 페이지네이션 번호 버튼 영역 -->
                    {% if total_pages > 1 %}
                    <div class="flex justify-center items-center gap-2 mt-8 pt-4 border-t border-slate-200/60">
                        {% for p in range(1, total_pages + 1) %}
                            <a href="/?page={{ p }}" class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition {% if p == current_page %} bg-blue-600 text-white shadow-md shadow-blue-600/20 {% else %} bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 {% endif %}">
                                {{ p }}
                            </a>
                        {% endfor %}
                    </div>
                    {% endif %}

                {% else %}
                    <div class="bg-white p-16 text-center rounded-3xl border border-slate-200/60 text-slate-400 text-sm">
                        아직 저장된 명함이 없습니다. 왼쪽 폼에서 첫 명함을 추가해 보세요! 🚀
                    </div>
                {% endif %}
            </div>

        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    cards = load_cards()
    total_cards = len(cards)
    
    try:
        current_page = int(request.args.get('page', 1))
    except ValueError:
        current_page = 1

    total_pages = (total_cards + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    if total_pages < 1:
        total_pages = 1

    if current_page > total_pages:
        current_page = total_pages
    if current_page < 1:
        current_page = 1

    reversed_cards = list(reversed(cards))
    start_idx = (current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_cards = reversed_cards[start_idx:end_idx]

    return render_template_string(
        HTML_TEMPLATE, 
        page_cards=page_cards, 
        total_cards=total_cards, 
        current_page=current_page, 
        total_pages=total_pages
    )

@app.route('/add', methods=['POST'])
def add_card():
    name = request.form.get('name', '').strip()
    company = request.form.get('company', '').strip()
    title = request.form.get('title', '').strip()
    
    # 입력받은 번호에 자동 하이픈 적용
    phone = format_phone_number(request.form.get('phone', '').strip())
    office_phone = format_phone_number(request.form.get('office_phone', '').strip())
    
    email = request.form.get('email', '').strip()

    if not name or not phone:
        return redirect(url_for('index'))

    new_card = {
        "name": name,
        "company": company,
        "title": title,
        "phone": phone,
        "office_phone": office_phone,
        "email": email
    }

    cards = load_cards()
    cards.append(new_card)
    save_cards(cards)

    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_card(index):
    cards = load_cards()
    reversed_index = len(cards) - 1 - index
    if 0 <= reversed_index < len(cards):
        cards.pop(reversed_index)
        save_cards(cards)
    return redirect(url_for('index'))

@app.route('/update/<int:index>', methods=['POST'])
def update_card(index):
    cards = load_cards()
    reversed_index = len(cards) - 1 - index
    if 0 <= reversed_index < len(cards):
        cards[reversed_index] = {
            "name": request.form.get('name', '').strip(),
            "company": request.form.get('company', '').strip(),
            "title": request.form.get('title', '').strip(),
            "phone": format_phone_number(request.form.get('phone', '').strip()),
            "office_phone": format_phone_number(request.form.get('office_phone', '').strip()),
            "email": request.form.get('email', '').strip()
        }
        save_cards(cards)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)