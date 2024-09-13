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
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("Fine-tuning Complete", "Fine-tuning 작업이 완료되었습니다!")
                root.destroy()
                break  # 작업 완료 시 루프 탈출
            elif status == 'failed':
                root = tk.Tk()
                root.withdraw()
                messagebox.showwarning("Fine-tuning Failed", "Fine-tuning 작업이 실패했습니다.")
                root.destroy()
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







