import openai
from openai import OpenAI
from main import my_api_key
from model_manager import select_model
from prompt_manager import prompt_manager
import tkinter as tk

client = OpenAI(api_key=my_api_key)
model_to_use_id = select_model(client)
system_prompt = prompt_manager()

def send_query():
    user_input = text_entry.get("1.0", tk.END).strip()  # 텍스트 입력창의 내용을 가져옴
    if user_input:
        response = client.chat.completions.create(
            model=model_to_use_id,
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

def paste_clipboard(event=None):
    text_entry.insert(tk.INSERT, root.clipboard_get())

root = tk.Tk()
root.title("GPT Fine_Tuned Model Interaction")

text_entry = tk.Text(root, height=10, width=50)
text_entry.pack()
text_entry.bind("<Command-v>", paste_clipboard)  # Mac의 경우

send_button = tk.Button(root, text="Send", command=send_query)
send_button.pack()

# 결과 출력 텍스트 위젯 (복사 가능하도록)
result_text = tk.Text(root, height=10, width=50, wrap=tk.WORD)
result_text.pack()
result_text.config(state=tk.DISABLED)  # 처음에는 비활성화하여 편집 불가 상태로 설정


root.mainloop()
