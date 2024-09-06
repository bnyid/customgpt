import os, shutil, time, json
import tkinter as tk
from tkinter import messagebox,filedialog

import pandas as pd

def upload_file_and_wait(file_path, client):
    # 파일 업로드
    if os.path.exists(file_path):
        file_upload_response = client.files.create(file=open(file_path, 'rb'), purpose='fine-tune')
    else:
        raise FileNotFoundError(f"File {file_path} does not exist for upload.")

    # 업로드 상태 확인
    file_id = file_upload_response.id
    while True:
        file_status = client.files.retrieve(file_id)  # 파일 상태 객체를 받아옴
        if file_status.status == 'processed':  # 객체 속성으로 접근
            print(f"File {file_id} processed successfully.")
            break
        elif file_status.status == 'failed':  # 객체 속성으로 접근
            raise Exception(f"File {file_id} processing failed.")
        else:
            print(f"File {file_id} is still processing... waiting.")
            time.sleep(5)  # 5초 간격으로 상태를 확인
    
    uploaded_dir = 'uploaded_data'
    if not os.path.exists(uploaded_dir):
        os.makedirs(uploaded_dir)

    # 파일 이동
    new_path = os.path.join(uploaded_dir, os.path.basename(file_path))
    shutil.move(file_path, new_path)

    return file_upload_response


def df_to_jsonl(type, df, sys_prompt, string):
    formatted_data = []
    
    for index, row in df.iterrows():  # 각 행에 대해 index, series 튜플 반환
        entry = {"messages": [{'role': 'system', 'content': sys_prompt},
                              {'role': 'user', 'content': row['input']},
                              {'role': 'assistant', 'content': row['output']}
                             ]}
        formatted_data.append(entry)

    file_name = f'{type}_{string}.jsonl'
    file_path = os.path.abspath(file_name)
    with open(file_path, 'w') as f:
        for entry in formatted_data:
            f.write(json.dumps(entry))
            f.write("\n")
    
    return file_path


def check_fine_tuning_status(client, fine_tuning_job_id):
    """
    Fine-tuning 작업 상태를 확인하고 완료되면 메시지를 띄웁니다.
    """
    while True:
        try:
            # Fine-tuning 작업 상태 확인
            fine_tune_status = client.fine_tuning.jobs.retrieve(fine_tuning_job_id)
            status = fine_tune_status.status
            
            if status == 'succeeded':
                messagebox.showinfo("Fine-tuning Complete", "Fine-tuning 작업이 완료되었습니다!")
                break  # 작업 완료 시 루프 탈출
            elif status == 'failed':
                messagebox.showwarning("Fine-tuning Failed", "Fine-tuning 작업이 실패했습니다.")
                break  # 작업 실패 시 루프 탈출
            else:
                print(f"Fine-tuning in progress... Status: {status}")
                
            # 30초 동안 대기 후 상태를 다시 확인
            time.sleep(5)
        
        except Exception as e:
            print(f"Error while checking fine-tuning status: {e}")
            break  # 오류 발생 시 루프 탈출

def start_fine_tuning(client, file_upload_response_train, file_upload_response_val, selected_model):
    """
    Fine-tuning 작업을 시작하고, 상태를 30초마다 확인하는 함수.
    """
    try:
        # Fine-tuning 작업 시작
        fine_tuning_response = client.fine_tuning.jobs.create(
            training_file=file_upload_response_train.id,
            model=selected_model,
            hyperparameters={'n_epochs': 1},
            validation_file=file_upload_response_val.id
        )
        
        fine_tuning_job_id = fine_tuning_response['id']
        messagebox.showinfo("Fine-tuning Started", f"Fine-tuning 작업이 시작되었습니다. ID: {fine_tuning_job_id}")
        
        # 작업 상태 확인 시작
        
        check_fine_tuning_status(client, fine_tuning_job_id)
    
    except Exception as e:
        messagebox.showerror("Error", f"Fine-tuning 작업을 시작하는 동안 오류가 발생했습니다: {e}")



def db_to_df():
    def select_db_file():
        # Tkinter 윈도우를 숨깁니다
        root = tk.Tk()
        root.withdraw()

        # 파일 선택 대화상자 열기
        file_path = filedialog.askopenfilename(
            title="학습시킬 DB를 선택하세요.",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )

        # 사용자가 선택한 파일 경로 반환
        return file_path


    raw_db_path = select_db_file()
    raw_df = pd.read_csv(raw_db_path, encoding='utf-8')
    df = raw_df[['input', 'output']]
    df = df.dropna(subset=['output'])
    val_test_data = df.sample(10,random_state=42)
    val_df = val_test_data.head(5)
    test_df = val_test_data.tail(5)
    train_df = df[~df.index.isin(val_test_data.index)]
    file_name = os.path.splitext(os.path.basename(raw_db_path))[0]

    return val_df,test_df,train_df,file_name


    # 학습할 csv 읽어서 변수에 할당하기




