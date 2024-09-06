import os, json, gspread
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from datetime import datetime

load_dotenv()
my_spread_sheet_id = os.getenv("SPREADSHEET_MY_ID")
SHEET_NAME = 'system_prompt'

# Google Sheets API 자격 증명 설정
def get_google_sheets_client():
    creds_path = 'my-google-sheet-api-key.json'  # 서비스 계정 키 파일 경로
    creds = Credentials.from_service_account_file(creds_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    return client

# 시스템 프롬프트 데이터 로드 (Google Sheets에서 로드)
def load_system_prompts():
    client = get_google_sheets_client()
    sheet = client.open_by_key(my_spread_sheet_id).worksheet(SHEET_NAME)
    rows = sheet.get_all_values()

    # 첫 번째 행은 헤더이므로 제외하고 데이터 딕셔너리로 변환 (열 순서 명확히 설정)
    prompts = [{"updated_at": row[0], "type": row[1], "system_prompt": row[2], "memo": row[3]} for row in rows[1:]]
    return prompts

# 시스템 프롬프트 데이터 저장 (Google Sheets에 저장)
def save_system_prompts(prompts):
    client = get_google_sheets_client()
    sheet = client.open_by_key(my_spread_sheet_id).worksheet(SHEET_NAME)

    # 저장할 데이터를 리스트 형식으로 변환
    rows = [["updated_at", "type", "system_prompt", "memo"]]  # 헤더 추가
    for prompt in prompts:
        rows.append([prompt['updated_at'], prompt['type'], prompt['system_prompt'], prompt['memo']])
    
    # 기존 내용을 삭제하고 새 데이터를 추가
    sheet.clear()
    sheet.append_rows(rows)

def prompt_manager():
    # Google Sheets에서 데이터 로드
    system_prompts = load_system_prompts()

    # 전역 변수로 선택된 'system_prompt' 저장
    global selected_index, selected_prompt, selected_type, selected_memo
    selected_index = None
    selected_prompt = None  # 선택된 system_prompt 값을 저장할 변수
    selected_type = None
    selected_memo = None
    is_edit_mode = False  # 편집 모드 상태 변수

    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - ((width // 2) + 50)
        y = (screen_height // 2) - ((height // 2) + 100)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def on_select_tree(event):
        global selected_index
        selected_item = tree.focus()  # 선택된 항목의 ID를 가져옴
        if selected_item:
            selected_index = int(tree.index(selected_item))  # 선택된 항목의 인덱스를 저장

            # 해당 인덱스에 맞는 'system_prompt'와 'memo'를 가져오기
            prompt = system_prompts[selected_index]['system_prompt']

            # 텍스트 박스 수정 가능으로 변경 후 업데이트
            text_box.config(state="normal")
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, prompt)

            # 트리 항목을 선택했을 때 기본으로 읽기 모드로 전환
            set_read_only_mode()

    def toggle_edit_mode():
        """편집 모드와 읽기 전용 모드를 전환하는 함수"""
        nonlocal is_edit_mode
        if is_edit_mode:
            set_read_only_mode()
        else:
            set_edit_mode()

    def set_edit_mode():
        """편집 모드로 설정"""
        nonlocal is_edit_mode
        text_box.config(state="normal")
        edit_mode_label.config(text="편집 모드")
        edit_button.config(text="읽기 전용으로 전환")
        is_edit_mode = True

    def set_read_only_mode():
        """읽기 전용 모드로 설정"""
        nonlocal is_edit_mode
        text_box.config(state="disabled")
        edit_mode_label.config(text="읽기 전용")
        edit_button.config(text="편집모드로 전환")
        is_edit_mode = False

    def save_to_sheet():
        """수정한 내용을 Google Sheets에 저장"""
        global selected_index
        if selected_index is not None:
            # 텍스트 박스에서 수정된 내용을 가져옴
            updated_prompt = text_box.get("1.0", tk.END).strip()

            # 현재 시간을 yymmddhhmm 형식으로 변환
            current_date = datetime.now().strftime("%y%m%d%H%M")

            # system_prompts 리스트에서 해당 인덱스의 데이터 업데이트
            system_prompts[selected_index]['system_prompt'] = updated_prompt
            system_prompts[selected_index]['updated_at'] = current_date

            # Google Sheets에 저장
            save_system_prompts(system_prompts)

            # Treeview 업데이트 (해당 행의 updated_at도 갱신)
            selected_item = tree.focus()  # 선택된 항목의 ID 가져오기
            tree.item(selected_item, values=(current_date, system_prompts[selected_index]['type'], system_prompts[selected_index]['memo']))  # Treeview 갱신

            # 저장 후 기본 읽기 모드로 전환
            set_read_only_mode()
            messagebox.showinfo("저장 완료", f"저장되었습니다.")

    def select_prompt_and_exit():
        global selected_prompt, selected_type, selected_index, selected_memo
        if selected_index is not None:
            # 선택된 인덱스의 system_prompt 값을 selected_prompt에 저장
            selected_prompt = system_prompts[selected_index]['system_prompt']
            selected_type = system_prompts[selected_index]['type']
            selected_memo = system_prompts[selected_index]['memo']
            messagebox.showinfo("선택 완료", f"{selected_type} 프롬프트가 선택되었습니다.")
            root.destroy()
        else:
            messagebox.showwarning("선택 오류", "선택된 항목이 없습니다.")

    def edit_memo(event):
        """트리플 클릭 시 메모를 편집할 수 있는 창을 띄움"""
        global selected_index
        selected_item = tree.focus()
        if selected_item:
            selected_index = int(tree.index(selected_item))
            memo = system_prompts[selected_index]['memo']

            # 팝업 창 생성
            edit_window = tk.Toplevel(root)
            edit_window.title("Edit Memo")
            center_window(edit_window, 300, 200)

            tk.Label(edit_window, text="Memo를 수정하세요:").pack(pady=10)
            memo_entry = tk.Text(edit_window, height=5, width=40)
            memo_entry.pack(pady=10)
            memo_entry.insert(tk.END, memo)

            def save_edited_memo():
                new_memo = memo_entry.get("1.0", tk.END).strip()
                system_prompts[selected_index]['memo'] = new_memo
                save_system_prompts(system_prompts)
                tree.item(selected_item, values=(system_prompts[selected_index]['updated_at'], system_prompts[selected_index]['type'], new_memo))
                edit_window.destroy()

            save_button = tk.Button(edit_window, text="저장", command=save_edited_memo)
            save_button.pack(pady=10)

    def add_new_type():
        """새로운 Type을 추가하는 함수"""
        def save_new_type():
            new_type = type_entry.get().strip()  # 입력한 새로운 type 가져오기
            if new_type:
                # 현재 시간으로 updated_at 생성
                current_date = datetime.now().strftime("%y%m%d%H%M")
                # 새로운 프롬프트 데이터 추가
                system_prompts.append({
                    'updated_at': current_date,
                    'type': new_type,
                    'system_prompt': "",  # 빈 시스템 프롬프트로 시작
                    'memo': ""  # 빈 메모로 시작
                })
                # Google Sheets에 저장
                save_system_prompts(system_prompts)
                # Treeview에 새로 추가
                tree.insert("", "end", values=(current_date, new_type, ""))
                new_type_window.destroy()  # 창 닫기
            else:
                messagebox.showwarning("입력 오류", "Type을 입력해 주세요.")

        # 새 창을 생성하여 Type 추가 입력 받기
        new_type_window = tk.Toplevel(root)
        new_type_window.title("새로운 Type 추가")
        center_window(new_type_window, 300, 150)

        tk.Label(new_type_window, text="새로운 Type을 입력하세요:").pack(pady=10)
        type_entry = tk.Entry(new_type_window, width=30)
        type_entry.pack(pady=10)

        save_button = tk.Button(new_type_window, text="저장", command=save_new_type)
        save_button.pack(pady=10)

    def delete_type():
        """선택된 Type을 삭제하는 함수"""
        global selected_index
        if selected_index is not None:
            confirm = messagebox.askyesno("삭제 확인", "선택된 Type을 정말로 삭제하시겠습니까?")
            if confirm:
                # system_prompts 리스트에서 해당 인덱스 삭제
                deleted_type = system_prompts.pop(selected_index)

                # Google Sheets에 저장 (삭제된 상태로 덮어쓰기)
                save_system_prompts(system_prompts)

                # Treeview에서 해당 항목 삭제
                tree.delete(tree.selection())

                # 텍스트 박스 초기화
                text_box.config(state="normal")
                text_box.delete("1.0", tk.END)
                text_box.config(state="disabled")

                messagebox.showinfo("삭제 완료", f"{deleted_type['type']}가 삭제되었습니다.")
        else:
            messagebox.showwarning("선택 오류", "삭제할 항목을 선택하지 않았습니다.")

    # Tkinter GUI 설정
    root = tk.Tk()
    center_window(root, 1120, 550)

    label_list = tk.Label(root, text="System Prompt List")
    label_list.grid(row=0, column=0, padx=20, pady=10, sticky="nw")

    memo_edit_label = tk.Label(root, text="메모 수정 = 3번 연속 클릭")
    memo_edit_label.grid(row=0, column=1, padx=20, pady=10, sticky="e")

    add_button = tk.Button(root, text="Type 추가", command=add_new_type)
    add_button.grid(row=0, column=2, sticky="e")

    label_prompt = tk.Label(root, text="[시스템 프롬프트]")
    label_prompt.grid(row=0, column=5, padx=20, pady=10, sticky="w")
    

    # 편집 모드 버튼
    edit_button = tk.Button(root, text="편집모드로 전환", command=toggle_edit_mode)
    edit_button.grid(row=0, column=6, sticky="e")

    # 편집 모드 상태 라벨 추가
    edit_mode_label = tk.Label(root, text="읽기 전용")
    edit_mode_label.grid(row=0, column=7, sticky="w")

    save_button = tk.Button(root, text="저장", command=save_to_sheet)
    save_button.grid(row=0, column=7, padx=10, pady=10, sticky="e")

    select_button = tk.Button(root, text="프롬프트 선택", command=select_prompt_and_exit)
    select_button.grid(row=2, column=6, padx=20, pady=10, sticky="e")

    delete_button = tk.Button(root, text="삭제", command=delete_type)
    delete_button.grid(row=2, column=0, padx=20, pady=10, sticky="w")

    tree = ttk.Treeview(root, columns=("updated_at", "type", "memo"), show="headings", height=20)
    tree.grid(row=1, column=0, columnspan=4,padx=20, pady=10, sticky="n")

    tree.heading("updated_at", text="Updated At")
    tree.heading("type", text="Type")
    tree.heading("memo", text="Memo")
    tree.column("updated_at", width=150)
    tree.column("type", width=150)
    tree.column("memo", width=150)

    # Treeview에 데이터 삽입
    for prompt in system_prompts:
        tree.insert("", "end", values=(prompt['updated_at'], prompt['type'], prompt['memo']))

    tree.bind('<<TreeviewSelect>>', on_select_tree)
    
    # 트리플 클릭 이벤트 바인딩
    tree.bind('<Triple-1>', edit_memo)

    # 시스템 프롬프트 입력 박스
    text_box = tk.Text(root, height=30, width=80)
    text_box.grid(row=1, column=5, padx=20, pady=10, sticky="n", columnspan=3)
    text_box.config(state="disabled")

    root.mainloop()
    return selected_type, selected_prompt

if __name__ == "__main__":
    prompt_manager()