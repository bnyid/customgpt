import tkinter as tk
from tkinter import messagebox, ttk
import json
from openai import OpenAI
from main import my_api_key


# 메타데이터 로드
def load_model_metadata():
    try:
        with open('model_metadata.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_model_metadata(metadata):
    with open('model_metadata.json', 'w') as f:
        json.dump(metadata, f)

def select_model(client):
    selected_model = None  # 선택된 모델 저장
    model_metadata = load_model_metadata()  # 메타데이터 로드

    def center_window(window, width, height):
        # 화면의 너비와 높이를 가져옴
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # 중앙에 창을 배치하기 위한 x, y 좌표 계산
        x = (screen_width // 2) - ((width // 2) + 50)
        y = (screen_height // 2) - ((height // 2) + 100)

        # 창의 크기와 위치 설정
        window.geometry(f'{width}x{height}+{x}+{y}')

    def on_model_select(event):
        nonlocal selected_model  # selected_model을 업데이트할 수 있도록 nonlocal 선언
        selected_item = tree.focus()  # 선택된 항목의 ID를 가져옴
        if selected_item:
            selected_values = tree.item(selected_item, 'values')
            selected_model = selected_values[0]  # 선택된 모델 ID 저장
            description = model_metadata.get(selected_model, {}).get('description', '')
            memo = model_metadata.get(selected_model, {}).get('memo', '')

            # 설명과 메모를 텍스트 상자에 표시
            description_entry.delete(0, tk.END)
            description_entry.insert(0, description)
            memo_textbox.delete('1.0', tk.END)
            memo_textbox.insert(tk.END, memo)

    def save_metadata():
        if selected_model:
            description = description_entry.get()
            memo = memo_textbox.get('1.0', tk.END).strip()

            # 모델 메타데이터 저장
            model_metadata[selected_model] = {'description': description, 'memo': memo}
            save_model_metadata(model_metadata)

            # Treeview에 반영
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

    # 모델 선택 시 반환
    def select_model_confirm():
        if selected_model:
            messagebox.showinfo("Model Selected", f"'{selected_model}'가 선택되었습니다.")
            root.destroy()  # 창을 닫음
        else:
            messagebox.showwarning("No Selection", "모델을 선택하지 않았습니다.")

    # Tkinter 설정
    root = tk.Tk()
    root.title("Select GPT Model")
    center_window(root,800,700)

    # 창이 닫힐 때의 동작 설정
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 모델 목록 라벨
    label = tk.Label(root, text="Select a GPT model")
    label.pack(pady=10)

    # Treeview 설정
    tree = ttk.Treeview(root, columns=("Model ID", "Description", "Memo"), show="headings")
    tree.heading("Model ID", text="Model ID")
    tree.heading("Description", text="Description")
    tree.heading("Memo", text="Memo")
    tree.pack(fill="both", expand=True)

    # 모델 메타데이터 입력/수정 영역
    tk.Label(root, text="Description:").pack(pady=5)
    description_entry = tk.Entry(root, width=100)
    description_entry.pack(pady=5)

    tk.Label(root, text="Memo:").pack(pady=5)
    memo_textbox = tk.Text(root, height=5, width=100)
    memo_textbox.pack(pady=5)

    # Save 버튼
    save_button = tk.Button(root, text="Save Metadata", command=save_metadata)
    save_button.pack(pady=10)

    # 모델 선택 버튼
    select_button = tk.Button(root, text="모델 선택", command=select_model_confirm)
    select_button.pack(pady=10)

    # OpenAI에서 모델 목록 가져오기
    models = client.models.list().data  # OpenAI에서 모델 목록 가져오기
    fine_tune_models = ['babbage-002',
                        'davinci-002',
                        'gpt-3.5-turbo-0125',
                        'gpt-3.5-turbo-0613',
                        'gpt-3.5-turbo-1106',
                        'gpt-4o-2024-08-06',
                        'gpt-4o-mini-2024-07-18',
                        ]  # Fine-tuning이 가능한 모델 목록

    # Fine-tuning이 가능한 모델 필터링
    matched_models = [model.id for model in models if model.id in fine_tune_models]
    fine_tuned_models = [model.id for model in models if model.id.startswith('ft:')]

    final_models_list = matched_models + fine_tuned_models

    # Treeview에 모델 정보 추가
    for model_id in final_models_list:
        description = model_metadata.get(model_id, {}).get('description', 'No description')
        memo = model_metadata.get(model_id, {}).get('memo', 'No memo')
        tree.insert("", tk.END, values=(model_id, description, memo))

    # Treeview에서 선택한 모델의 정보를 보여줌
    tree.bind('<<TreeviewSelect>>', on_model_select)

    # GUI 실행
    root.mainloop()

    return selected_model  # 선택된 모델 반환

client = OpenAI(api_key=my_api_key)
select_model(client)