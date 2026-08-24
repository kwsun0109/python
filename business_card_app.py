import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

# 데이터가 저장될 파일명
DATA_FILE = "business_cards.json"

class BusinessCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("나만의 명함 관리 프로그램")
        self.root.geometry("600x500")
        self.root.minsize(550, 450)

        # 상단 입력 폼 프레임 (padding 옵션 제거 및 내부 여백 조정)
        form_frame = tk.LabelFrame(root, text=" 명함 정보 입력 ")
        form_frame.pack(fill="x", padx=15, pady=15, ipady=10)

        fields = [
            ("이름", "name_entry"),
            ("회사명", "company_entry"),
            ("직책", "title_entry"),
            ("연락처", "phone_entry"),
            ("이메일", "email_entry"),
        ]

        self.entries = {}
        for i, (label_text, attr_name) in enumerate(fields):
            lbl = tk.Label(form_frame, text=label_text, width=8, anchor="w")
            lbl.grid(row=i, column=0, sticky="w", padx=10, pady=4)
            
            ent = tk.Entry(form_frame, width=30)
            ent.grid(row=i, column=1, sticky="ew", padx=10, pady=4)
            self.entries[attr_name] = ent

        form_frame.columnconfigure(1, weight=1)

        # 저장 및 초기화 버튼 프레임
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        save_btn = tk.Button(btn_frame, text="💾 명함 저장", bg="#007aff", fg="white", font=("", 10, "bold"), width=12, command=self.save_card)
        save_btn.pack(side="left", padx=5)

        clear_btn = tk.Button(btn_frame, text="🧹 입력 지우기", width=12, command=self.clear_entries)
        clear_btn.pack(side="left", padx=5)

        # 하단 리스트 (저장된 명함 목록) 프레임
        list_frame = tk.LabelFrame(root, text=" 등록된 명함 목록 ")
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # 트리뷰(표 형태) 생성
        columns = ("name", "company", "title", "phone", "email")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("name", text="이름")
        self.tree.heading("company", text="회사명")
        self.tree.heading("title", text="직책")
        self.tree.heading("phone", text="연락처")
        self.tree.heading("email", text="이메일")

        self.tree.column("name", width=80, anchor="center")
        self.tree.column("company", width=110, anchor="w")
        self.tree.column("title", width=80, anchor="center")
        self.tree.column("phone", width=120, anchor="center")
        self.tree.column("email", width=140, anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # 프로그램 실행 시 기존 데이터 불러오기
        self.load_data()

    def save_card(self):
        name = self.entries["name_entry"].get().strip()
        company = self.entries["company_entry"].get().strip()
        title = self.entries["title_entry"].get().strip()
        phone = self.entries["phone_entry"].get().strip()
        email = self.entries["email_entry"].get().strip()

        if not name or not phone:
            messagebox.showwarning("입력 오류", "이름과 연락처는 필수 입력 항목입니다!")
            return

        new_card = {
            "name": name,
            "company": company,
            "title": title,
            "phone": phone,
            "email": email
        }

        # 기존 데이터 읽기
        cards = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    cards = json.load(f)
            except:
                cards = []

        cards.append(new_card)

        # JSON 파일에 저장
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(cards, f, ensure_ascii=False, indent=4)

        messagebox.showinfo("성공", "명함이 안전하게 저장되었습니다!")
        self.clear_entries()
        self.load_data()

    def clear_entries(self):
        for ent in self.entries.values():
            ent.delete(0, tk.END)

    def load_data(self):
        # 기존 트리뷰 목록 초기화
        for item in self.tree.get_children():
            self.tree.delete(item)

        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    cards = json.load(f)
                    for card in cards:
                        self.tree.insert("", "end", values=(
                            card.get("name"),
                            card.get("company"),
                            card.get("title"),
                            card.get("phone"),
                            card.get("email")
                        ))
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = BusinessCardApp(root)
    root.mainloop()