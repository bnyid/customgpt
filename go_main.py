# 클라이언트 콜
import tkinter as tk
import os, sys
from openai import OpenAI
from file_formatter import df_splitter, format_to_jsonl
from data_manager_ import load_sheet_to_df
from upload_manager import upload_file_and_wait, check_fine_tuning_status
from prompt_manager import prompt_manager
from model_manager import select_model
from cost_manager import calculate_cost
from tkinter import messagebox
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    my_api_key = os.getenv("OPENAI_MY_API_KEY")


    client = OpenAI(api_key=my_api_key)
    # 훈련시킬 모델 선택
    selected_model = select_model(client)

    if not selected_model:
        messagebox.showerror("Error", "모델이 선택되지 않았습니다. 작업을 종료합니다.")
        sys.exit()
            
    # system_prompt 선택
    type, system_prompt = prompt_manager()

    if not system_prompt:
        messagebox.showerror("Error", "프롬프트를 선택하지 않았습니다. 작업을 종료합니다.")
        sys.exit()

    # 학습시킬 sheet를 선택하고 df로 반환
    selected_sheet_df = load_sheet_to_df()

    # 학습시킬 sheet의 df를 검증,테스트,훈련용으로 3개의 df로 반환함
    val_df,test_df,train_df = df_splitter(selected_sheet_df)


    # df에다가 system_prompt를 입혀서 json파일로 변환하고 그 jsonl 파일의 경로를 얻어옴
    train_jsonl_path = format_to_jsonl(type, train_df, system_prompt,"train")
    val_jsonl_path = format_to_jsonl(type, val_df, system_prompt,"val")



    # json 파일을 open ai 웹에 업로드 (업로드 완료될 때 까지 대기)
    file_upload_response_train = upload_file_and_wait(train_jsonl_path, client)
    file_upload_response_val = upload_file_and_wait(val_jsonl_path, client)


    total_cost, total_tokens = calculate_cost(train_df,selected_model)

    root = tk.Tk()
    root.withdraw()  # 기본 창을 숨김 (필요하지 않으므로 표시되지 않게)
    result = messagebox.askyesno("Training Cost", f"훈련에는 총 {total_tokens} 토큰이 사용되며, 총 {int(total_cost)}원의 비용이 부과됩니다.\n트레이닝을 시작하겠습니까?")
    

    
    if result:
        # 트레이닝 시작
        try:
            # Fine-tuning 작업 시작
            fine_tuning_response = client.fine_tuning.jobs.create(training_file=file_upload_response_train.id,
                                                                    model=selected_model,
                                                                    hyperparameters={'n_epochs':1},
                                                                    validation_file=file_upload_response_val.id
                                                                    )
            fine_tuning_job_id = fine_tuning_response.id
            print("Fine-tuning Started", f"Fine-tuning 작업이 시작되었습니다. ID: {fine_tuning_job_id}")
            
            # 작업 상태 확인 시작
            
            check_fine_tuning_status(client, fine_tuning_job_id)
        
        except Exception as e:
            messagebox.showerror("Error", f"Fine-tuning 작업을 시작하는 동안 오류가 발생했습니다: {e}")
            root.destroy()

