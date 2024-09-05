import os,json,time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
from datetime import datetime


def prompt_manager():
    # CSV 파일 읽기
    df = pd.read_csv('system_prompt_db.csv')

    # 'type' 및 'updated_at' 열 값 추출
    type_options = df[['updated_at', 'type']].dropna().values.tolist()

    # 전역 변수로 선택된 'system_prompt' 저장
    global selected_index, selected_prompt,selected_type

    selected_index = None
    selected_prompt = None  # 선택된 system_prompt 값을 저장할 변수
    selected_type = None

    def center_window(window, width, height):
        # 화면의 너비와 높이를 가져옴
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # 중앙에 창을 배치하기 위한 x, y 좌표 계산
        x = (screen_width // 2) - ((width // 2) + 50)
        y = (screen_height // 2) - ((height // 2) + 100)

        # 창의 크기와 위치 설정
        window.geometry(f'{width}x{height}+{x}+{y}')

    def on_select_tree(event):
        global selected_index
        selected_item = tree.focus()  # 선택된 항목의 ID를 가져옴
        if selected_item:
            print(f"Selected item: {selected_item}")
            selected_values = tree.item(selected_item, 'values')
            selected_index = int(tree.index(selected_item))  # 선택된 항목의 인덱스를 저장
            print(f"Selected index: {selected_index}")
            
            # 해당 인덱스에 맞는 'system_prompt'를 가져오기
            prompt = df.iloc[selected_index]['system_prompt']
            
            # 텍스트 박스 수정 가능으로 변경 후 업데이트
            text_box.config(state="normal")  # 텍스트 박스를 수정 가능하게
            text_box.delete("1.0", tk.END)  # 기존 텍스트 박스 내용을 지움
            text_box.insert(tk.END, prompt)  # 선택한 시스템 프롬프트를 넣어줌
            text_box.config(state="disabled")  # 다시 읽기 전용으로 설정

    def enable_edit():
        """편집 모드 활성화"""
        text_box.config(state="normal")

    def save_to_csv():
        """수정한 내용을 CSV 파일에 저장"""
        global selected_index
        if selected_index is not None:
            # 텍스트 박스에서 수정된 내용을 가져옴
            updated_prompt = text_box.get("1.0", tk.END).strip()  # strip()은 앞뒤 공백 제거
            
            # 현재 시간을 yymmddhhmm 형식으로 변환
            current_date = datetime.now().strftime("%y%m%d%H%M")
            
            # 데이터프레임에서 해당 인덱스의 system_prompt와 updated_at 업데이트
            df.at[selected_index, 'system_prompt'] = updated_prompt
            df.at[selected_index, 'updated_at'] = current_date
            
            # CSV 파일로 다시 저장 (utf-8-sig 인코딩 사용)
            df.to_csv('system_prompt_db.csv', index=False, encoding='utf-8-sig')
            
            # Treeview 업데이트 (해당 행의 updated_at도 갱신)
            selected_item = tree.focus()  # 선택된 항목의 ID 가져오기
            tree.item(selected_item, values=(current_date, df.at[selected_index, 'type']))  # Treeview 갱신

            # 저장 후 다시 읽기 전용으로 변경
            text_box.config(state="disabled")

    def select_prompt_and_exit():

        print("select_prompt_and_exit 함수가 호출되었습니다.")
        global selected_prompt, selected_type, selected_index
        if selected_index is not None:
            print("selected_index가 None이 아님")
            # 선택된 인덱스의 system_prompt 값을 selected_prompt에 저장
            selected_prompt = df.iloc[selected_index]['system_prompt']
            selected_type = df.iloc[selected_index]['type']
            messagebox.showinfo("선택 완료", f"{selected_type} 프롬프트가 선택되었습니다.")
        else:
            print("selected_index가 None임. 선택된 항목이 없습니다.")


    # Tkinter GUI 설정
    root = tk.Tk()
    center_window(root, 1000, 500)  # 1000x500

    # 제목 라벨
    label_list = tk.Label(root, text="System Prompt List")
    label_list.grid(row=0, column=0, padx=20, pady=10, sticky="nw")

    # 추가 버튼
    add_button = tk.Button(root, text="Type 추가", command=None)  # 미리 정의된 함수를 할당해야 합니다.
    add_button.grid(row=0, column=0, padx=20, sticky="e")

    # 프롬프트 라벨
    label_prompt = tk.Label(root, text="[시스템 프롬프트]")
    label_prompt.grid(row=0, column=1, padx=20, pady=10, sticky="w")

    # 편집 버튼
    button_edit = tk.Button(root, text="편집모드로 전환", command=enable_edit)
    button_edit.grid(row=0, column=1, sticky="e")

    # 저장 버튼
    save_button = tk.Button(root, text="저장", command=save_to_csv)
    save_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

    # "프롬프트 선택" 버튼
    select_button = tk.Button(root, text="프롬프트 선택", command=select_prompt_and_exit)
    select_button.grid(row=2, column=2, padx=20, pady=10, sticky="e")

    # Treeview 위젯을 사용한 표 형식
    tree = ttk.Treeview(root, columns=("updated_at", "type"), show="headings", height=20)
    tree.grid(row=1, column=0, padx=20, pady=10, sticky="n")

    # Treeview 열 제목 설정
    tree.heading("updated_at", text="Updated At")
    tree.heading("type", text="Type")

    # Treeview 열 너비 설정
    tree.column("updated_at", width=150)
    tree.column("type", width=150)

    # Treeview에 데이터 삽입
    for item in type_options:
        tree.insert("", "end", values=item)

    # Treeview에 선택 이벤트 바인딩
    tree.bind('<<TreeviewSelect>>', on_select_tree)

    # 프롬프트 표시용 텍스트 박스 (기본적으로 읽기 전용)
    text_box = tk.Text(root, height=30, width=80)
    text_box.grid(row=1, column=1, padx=20, sticky="n", columnspan=2)
    text_box.config(state="disabled")

    # Tkinter 메인 루프 실행
    root.mainloop()
    return selected_type, selected_prompt


if __name__ == "__main__":
    prompt_manager()
