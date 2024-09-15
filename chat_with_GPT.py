import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from openai import OpenAI
from model_manager import select_model
from prompt_manager import prompt_manager
from dotenv import load_dotenv

load_dotenv()
my_api_key = os.getenv("OPENAI_MY_API_KEY")
client = OpenAI(api_key=my_api_key)

selected_model = select_model(client)

if not selected_model:
    messagebox.showerror("Error", "모델이 선택되지 않았습니다. 작업을 종료합니다.")
    sys.exit()

# system_prompt 선택
type, system_prompt = prompt_manager()
print("model_id : ", selected_model, "type : ", type)

def send_query():
    user_input = text_entry.get("1.0", tk.END).strip()
    if user_input:
        try:
            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            output_text = response.choices[0].message.content
            result_text.config(state=tk.NORMAL)
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, output_text)
            result_text.config(state=tk.DISABLED)
            status_var.set("응답을 성공적으로 받았습니다.")
            add_to_history(user_input, output_text)
        except Exception as e:
            messagebox.showerror("Error", f"요청 중 오류가 발생했습니다: {e}")
    else:
        messagebox.showwarning("Warning", "프롬프트를 입력하세요.")

def paste(event=None):
    try:
        text_entry.insert(tk.INSERT, root.clipboard_get())
    except tk.TclError:
        pass

def paste_from_clipboard():
    try:
        text_entry.insert(tk.END, root.clipboard_get())
    except tk.TclError:
        pass

def enable_copy(event):
    result_text.config(state=tk.NORMAL)
    result_text.event_generate("<<Copy>>")
    result_text.config(state=tk.DISABLED)

def copy_to_clipboard():
    try:
        output_content = result_text.get("1.0", tk.END).strip()
        root.clipboard_clear()
        root.clipboard_append(output_content)
        messagebox.showinfo("복사 완료", "출력 내용이 클립보드로 복사되었습니다.")
    except tk.TclError:
        pass

def clear_input():
    text_entry.delete("1.0", tk.END)

def clear_output():
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    result_text.config(state=tk.DISABLED)

def save_output():
    output_content = result_text.get("1.0", tk.END).strip()
    if output_content:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            messagebox.showinfo("저장 완료", "출력이 성공적으로 저장되었습니다.")
    else:
        messagebox.showwarning("Warning", "저장할 출력 내용이 없습니다.")

def add_to_history(user_input, output_text):
    history_listbox.insert(tk.END, user_input)
    history_data.append((user_input, output_text))

def show_history(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        user_input, output_text = history_data[index]
        text_entry.delete("1.0", tk.END)
        text_entry.insert(tk.END, user_input)
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, output_text)
        result_text.config(state=tk.DISABLED)

root = tk.Tk()
root.title("GPT Fine-Tuned Model Interaction")
root.resizable(False, False)

# 창 크기 설정
window_width = 1150
window_height = 800

# 화면 크기 가져오기
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 창의 x, y 좌표 계산 (가로 및 세로 중앙 정렬)
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2)) - 80

# 창의 위치 및 크기 설정
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 스타일 설정
style = ttk.Style()
style.theme_use('clam')

# Apple 스타일에 맞는 색상 팔레트
BACKGROUND_COLOR = '#F2F2F2'
BUTTON_COLOR = '#007AFF'
TEXT_COLOR = '#000000'
ENTRY_BG_COLOR = '#FFFFFF'

root.configure(bg=BACKGROUND_COLOR)

# 메뉴 바 추가
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="저장", command=save_output)
file_menu.add_separator()
file_menu.add_command(label="종료", command=root.quit)
menu_bar.add_cascade(label="파일", menu=file_menu)
root.config(menu=menu_bar)

# 상태 표시줄 추가
status_var = tk.StringVar()
status_var.set("준비됨")
status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor='w')
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# 메인 프레임 설정
main_frame = ttk.Frame(root, padding=(20, 10, 20, 10))
main_frame.pack(expand=True, fill=tk.BOTH)

# 입력 프레임
input_frame = ttk.LabelFrame(main_frame, text="프롬프트 입력", padding=(10, 10))
input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

input_frame.columnconfigure(0, weight=1)
input_frame.rowconfigure(1, weight=1)

# Paste Button above Text Entry
paste_button = ttk.Button(input_frame, text="clipboard에서 붙여넣기", command=paste_from_clipboard)
paste_button.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="ew")

text_entry = tk.Text(input_frame, height=15, wrap=tk.WORD, font=("Helvetica", 12), bg=ENTRY_BG_COLOR, fg=TEXT_COLOR)
text_entry.grid(row=1, column=0, sticky="nsew")
text_entry.bind('<Control-v>', paste)
text_entry.bind('<Command-v>', paste)

# 버튼 프레임
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=1, column=0, pady=5, sticky="ew")

send_button = ttk.Button(button_frame, text="Send", command=send_query)
send_button.grid(row=0, column=0, padx=5)

clear_input_button = ttk.Button(button_frame, text="입력 지우기", command=clear_input)
clear_input_button.grid(row=0, column=1, padx=5)

clear_output_button = ttk.Button(button_frame, text="출력 지우기", command=clear_output)
clear_output_button.grid(row=0, column=2, padx=5)

# 출력 프레임
output_frame = ttk.LabelFrame(main_frame, text="GPT의 답변", padding=(10, 10))
output_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

output_frame.columnconfigure(0, weight=1)
output_frame.rowconfigure(1, weight=1)

# Copy Button above Result Text
copy_button = ttk.Button(output_frame, text="clipboard로 복사하기", command=copy_to_clipboard)
copy_button.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="ew")

result_text = tk.Text(output_frame, height=15, wrap=tk.WORD, font=("Helvetica", 12), bg=ENTRY_BG_COLOR, fg=TEXT_COLOR)
result_text.grid(row=1, column=0, sticky="nsew")
result_text.config(state=tk.DISABLED)
result_text.bind('<Control-c>', enable_copy)
result_text.bind('<Command-c>', enable_copy)

# 히스토리 프레임
history_frame = ttk.LabelFrame(main_frame, text="히스토리", padding=(10, 10))
history_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=5, sticky="ns")

history_listbox = tk.Listbox(history_frame, height=35, font=("Helvetica", 12), bg=ENTRY_BG_COLOR, fg=TEXT_COLOR)
history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
history_listbox.bind('<<ListboxSelect>>', show_history)

history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=history_listbox.yview)
history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

history_listbox.config(yscrollcommand=history_scrollbar.set)

history_data = []

# 그리드 열 및 행 설정
main_frame.columnconfigure(0, weight=3)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)
main_frame.rowconfigure(2, weight=1)

root.mainloop()
