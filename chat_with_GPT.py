import os,sys
import tkinter as tk
from tkinter import messagebox 
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
print("model_id : ",selected_model,"type : ", type)
# sys.exit()

def send_query():
    user_input = text_entry.get("1.0", tk.END).strip()  # 텍스트 입력창의 내용을 가져옴
    if user_input:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        output_text = response.choices[0].message.content
        result_text.config(state=tk.NORMAL)  # 텍스트 위젯을 편집 가능 상태로 전환
        result_text.delete("1.0", tk.END)  # 기존 텍스트 삭제
        result_text.insert(tk.END, output_text)  # 결과 텍스트 삽입
        result_text.config(state=tk.DISABLED)  # 다시 텍스트 위젯을 비활성화
        
def paste(event=None):
    try:
        # 클립보드에서 텍스트를 가져와서 현재 커서 위치에 붙여넣기
        print("붙여넣기 바인드 동작 실행됨")
        text_entry.insert(tk.INSERT, root.clipboard_get())
        
    except tk.TclError:
        pass  # 클립보드에 텍스트가 없을 때 오류를 무시

def enable_copy(event):
    # 복사 기능을 허용하기 위해 비활성화 상태를 잠시 해제
    result_text.config(state=tk.NORMAL)
    result_text.event_generate("<<Copy>>")  # 복사 이벤트 트리거
    result_text.config(state=tk.DISABLED)  # 다시 비활성화


root = tk.Tk()
root.title("GPT Fine_Tuned Model Interaction")
root.geometry("848x800")


input_label = tk.Label(root, font=("Helvetica",16), text="[Input] prompt를 입력하세요>")
input_label.grid(row=0,column=2,columnspan=2, pady=10)
# input_label.destroy()

text_entry = tk.Text(root, height=20, width=120)
text_entry.grid(row=1,column=0, columnspan=6)
text_entry.bind('<Control-v>', paste)  # Windows/Linux에서 Ctrl+V로 붙여넣기
text_entry.bind('<Command-v>', paste)  # Mac에서 Command+V로 붙여넣기

send_button = tk.Button(root, text="Send",font=("Helvetica",15), width=5, height=1,command=send_query)
send_button.grid(row=2, column=2, columnspan=2, pady=10)

# 결과 출력 텍스트 위젯 
output_label = tk.Label(root,text="[Output] GPT의 답변이 하단에 표시됩니다.", font=("Hevetica",14))
output_label.grid(row=3,column=2, columnspan=2)

# output_label.destroy()
result_text = tk.Text(root, height=20, width=120, wrap=tk.WORD)
result_text.grid(row=4,column=0, columnspan=6,pady=10)
# result_text.destroy()
result_text.config(state=tk.DISABLED)  # 처음에는 비활성화하여 편집 불가 상태로 설정
result_text.bind('<Control-c>', enable_copy)  # Windows/Linux용 Ctrl+C
result_text.bind('<Command-c>', enable_copy)  # Mac용 Command+C


root.mainloop()
