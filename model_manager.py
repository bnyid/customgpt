import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
from openai import OpenAI
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()
my_api_key = os.getenv("OPENAI_MY_API_KEY")
my_spread_sheet_id = os.getenv("SPREADSHEET_MY_ID")
SHEET_NAME = 'model_meta'
client = OpenAI(api_key=my_api_key)

# Google Sheets API 자격 증명 설정
def get_google_sheets_client():
    # 서비스 계정 키 파일 경로 (json 파일 경로 설정)
    creds_path = 'my-google-sheet-api-key.json'  # 여기서 json 파일 경로를 설정해주세요 
    creds = Credentials.from_service_account_file(creds_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    return client

# 메타데이터 로드 (Google Sheets에서 로드)
def load_model_metadata():
    client = get_google_sheets_client()
    sheet = client.open_by_key(my_spread_sheet_id).worksheet(SHEET_NAME)
    
    # Google Sheets 데이터를 불러와서 dictionary로 변환
    rows = sheet.get_all_values()
    metadata = {}
    for row in rows[1:]:  # 첫 번째 행은 헤더
        model_id, description, memo = row
        metadata[model_id] = {'description': description, 'memo': memo}
    return metadata

# 메타데이터 저장 (Google Sheets에 저장)
def save_model_metadata(metadata):
    client = get_google_sheets_client()
    sheet = client.open_by_key(my_spread_sheet_id).worksheet(SHEET_NAME)
    
    # 스프레드시트에 저장할 데이터 포맷으로 변환
    rows = [["Model ID", "Description", "Memo"]]  # 첫 번째 행에 헤더 추가
    for model_id, data in metadata.items():
        rows.append([model_id, data['description'], data['memo']])
    
    # 기존 내용을 삭제하고 새 데이터를 추가
    sheet.clear()
    sheet.append_rows(rows)

def select_model(client):
    selected_model = None  # 선택된 모델 저장
    model_metadata = load_model_metadata()  # 메타데이터 로드

    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - ((width // 2) + 50)
        y = (screen_height // 2) - ((height // 2) + 100)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def on_model_select(event):
        nonlocal selected_model
        selected_item = tree.focus()
        if selected_item:
            selected_values = tree.item(selected_item, 'values')
            selected_model = selected_values[0]
            description = model_metadata.get(selected_model, {}).get('description', '')
            memo = model_metadata.get(selected_model, {}).get('memo', '')
            description_entry.delete(0, tk.END)
            description_entry.insert(0, description)
            memo_textbox.delete('1.0', tk.END)
            memo_textbox.insert(tk.END, memo)

    def save_metadata():
        if selected_model:
            description = description_entry.get()
            memo = memo_textbox.get('1.0', tk.END).strip()
            model_metadata[selected_model] = {'description': description, 'memo': memo}
            save_model_metadata(model_metadata)
            tree.item(tree.focus(), values=(selected_model, description, memo))
            messagebox.showinfo("Success", "Model metadata saved successfully.")
        else:
            messagebox.showwarning("No Selection", "모델을 선택하지 않았습니다.")

    def on_closing():
        if selected_model:
            root.destroy()
        else:
            if messagebox.askokcancel("Quit", "모델을 선택하지 않았습니다. 그래도 닫으시겠습니까?"):
                root.destroy()

    def select_model_confirm():
        if selected_model:
            messagebox.showinfo("Model Selected", f"'{selected_model}'가 선택되었습니다.")
            root.quit()
            root.destroy()

        else:
            messagebox.showwarning("No Selection", "모델을 선택하지 않았습니다.")

    root = tk.Tk()
    root.title("Select GPT Model")
    center_window(root, 800, 700)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    label = tk.Label(root, text="폐기할 모델은 Memo에 '미사용' 이라고 적어주세요")
    label.pack(pady=10)

    tree = ttk.Treeview(root, columns=("Model ID", "Description", "Memo"), show="headings")
    tree.heading("Model ID", text="Model ID")
    tree.heading("Description", text="Description")
    tree.heading("Memo", text="Memo")
    
    tree.column("Model ID", width=260)  # Model ID 열의 너비를 200으로 설정
    tree.column("Description", width=100)
    tree.pack(fill="both", expand=True)

    tk.Label(root, text="Description:").pack(pady=5)
    description_entry = tk.Entry(root, width=100)
    description_entry.pack(pady=5)

    tk.Label(root, text="Memo:").pack(pady=5)
    memo_textbox = tk.Text(root, height=5, width=100)
    memo_textbox.pack(pady=5)

    save_button = tk.Button(root, text="Save Metadata", command=save_metadata)
    save_button.pack(pady=10)

    select_button = tk.Button(root, text="모델 선택", command=select_model_confirm)
    select_button.pack(pady=10)

    models = client.models.list().data
    fine_tune_models = ['babbage-002', 'davinci-002', 'gpt-3.5-turbo-0125',
                        'gpt-3.5-turbo-0613', 'gpt-3.5-turbo-1106',
                        'gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18']

    matched_models = [model.id for model in models if model.id in fine_tune_models]
    fine_tuned_models = [model.id for model in models if model.id.startswith('ft:')]
    final_models_list = matched_models + fine_tuned_models

    for model_id in final_models_list:
        description = model_metadata.get(model_id, {}).get('description', '')
        memo = model_metadata.get(model_id, {}).get('memo', '')
        # tree.insert("", tk.END, values=(model_id, description, memo))
        if description != "미사용":
            tree.insert("", tk.END, values=(model_id, description, memo))

    tree.bind('<<TreeviewSelect>>', on_model_select)
    root.mainloop()
    return selected_model

if __name__ == "__main__":
    select_model(client)