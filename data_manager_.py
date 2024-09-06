import gspread
from google.oauth2.service_account import Credentials  # 최신 인증 라이브러리 사용
import pandas as pd
import tkinter as tk
from tkinter import Listbox, END
from tkinter import ttk  # Treeview를 위해 사용

# Google Sheets API 인증 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file('my-google-sheet-api-key.json', scopes=scope)
client = gspread.authorize(creds)

# 스프레드시트 ID 및 불러오기
spreadsheet_id = '1fdKRx2FbV90WhqJQHoNpy0YdVdL7_pLGZZO4EM8ooyw'
spreadsheet = client.open_by_key(spreadsheet_id)

# 모든 시트의 데이터를 저장할 딕셔너리
sheets_data = {}

def load_sheet_to_df():
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - ((width // 2) + 50)
        y = (screen_height // 2) - ((height // 2) + 100)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def update_all_sheets():
        """스프레드시트의 모든 시트 데이터를 불러와 메모리에 저장하고 Treeview를 최신화"""
        global sheets_data
        sheets_data.clear()  # 기존 데이터를 지움
        for sheet in sheet_list:
            data = sheet.get_all_records()
            if data:
                df = pd.DataFrame(data)
                sheets_data[sheet.title] = df  # 각 시트 데이터를 딕셔너리에 저장
        print("모든 시트 데이터 업데이트 완료")

        # 업데이트 후 현재 선택된 시트의 데이터를 Treeview에 표시
        selected_sheet = listbox.get(listbox.curselection()) if listbox.curselection() else None
        if selected_sheet:
            display_sheet_data(selected_sheet)

    def display_sheet_data(sheet_title):
        """선택한 시트의 데이터를 Treeview에 표시"""
        if sheet_title in sheets_data:
            df = sheets_data[sheet_title]

            # Treeview 업데이트 (이전에 표시된 내용을 모두 삭제)
            for item in tree.get_children():
                tree.delete(item)

            # Treeview에 새로운 데이터 추가
            tree["column"] = list(df.columns)
            tree["show"] = "headings"
            
            # 각 열에 대해 헤더 설정
            for col in tree["column"]:
                tree.heading(col, text=col)
                tree.column(col, width=100)  # 각 열의 너비를 설정

            # 데이터 입력
            for row in df.itertuples(index=False):
                tree.insert("", "end", values=row)

            # 스크롤 위치 초기화
            tree.yview_moveto(0)
            tree.xview_moveto(0)

    def on_select(event):
        """Listbox에서 시트를 선택했을 때 해당 데이터를 보여줌"""
        selected_sheet = listbox.get(listbox.curselection())
        display_sheet_data(selected_sheet)

    def return_selected_sheet_data():
        """선택한 시트의 데이터를 DataFrame으로 반환"""
        selected_sheet = listbox.get(listbox.curselection())
        if selected_sheet in sheets_data:
            print("sheet 선택 완료")
            root.destroy()
            return sheets_data[selected_sheet]
        else:
            print("No sheet selected or data unavailable")
            return None

    # Tkinter 윈도우 생성
    root = tk.Tk()
    root.title("Google Sheets 선택 및 데이터 보기")
    center_window(root, 1000, 600)

    # 좌측 Listbox (시트 선택)
    sheet_list_label = tk.Label(root, text="학습할 시트 리스트")
    sheet_list_label.grid(row=0, column=0, padx=10)

    sheet_list_label = tk.Label(root, text="Data 구조")
    sheet_list_label.grid(row=0, column=1, padx=10)

    # 데이터 최신화 버튼
    update_button = tk.Button(root, text="데이터 최신화", command=update_all_sheets)
    update_button.grid(row=0, column=1, padx=15, pady=10, sticky="E")

    listbox_frame = tk.Frame(root)
    listbox_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    listbox = tk.Listbox(listbox_frame)
    listbox.grid(row=0, column=0, sticky="nsew")
    listbox.bind('<<ListboxSelect>>', on_select)

    # 데이터 시트 선택 버튼 추가
    select_button = tk.Button(root, text="데이터 시트 선택!", command=lambda: set_selected_df(return_selected_sheet_data()))
    select_button.grid(row=2, column=1,pady=10)

    # 스프레드시트의 모든 시트 이름을 Listbox에 추가
    sheet_list = spreadsheet.worksheets()
    for sheet in sheet_list:
        listbox.insert(tk.END, sheet.title)

    # 우측 Treeview (데이터 표시)
    tree_frame = tk.Frame(root, width=200, height=100)
    tree_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    tree_frame.grid_propagate(False)  # 프레임의 크기가 내부 위젯에 따라 변하지 않도록 고정

    # Treeview에 세로 Scrollbar 추가
    tree_scroll_y = tk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.grid(row=0, column=1, sticky="ns")

    # Treeview에 가로 Scrollbar 추가
    tree_scroll_x = tk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.grid(row=1, column=0, sticky="ew")

    # 고정 크기의 Treeview 생성 (높이 300px, 너비 400px)
    tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set, height=10)
    tree.grid(row=0, column=0, sticky="nsew")

    # Scrollbar와 Treeview 연결
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    # 처음 프로그램 실행 시 자동으로 업데이트
    update_all_sheets()

    # grid 크기 설정
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(1, weight=1)

    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    # 선택된 DataFrame 저장 변수
    selected_df = None

    def set_selected_df(df):
        nonlocal selected_df
        selected_df = df

    # Tkinter 루프 실행
    root.mainloop()

    return selected_df


if __name__ == "__main__":
    selected_sheet_df = load_sheet_to_df()
    if selected_sheet_df is not None:
        print(selected_sheet_df)
        print("선택된 시트의 데이터프레임을 성공적으로 가져왔습니다.")
    else:
        print("시트가 선택되지 않았거나 오류가 발생했습니다.")