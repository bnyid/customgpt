import os,json
from data_manager_ import load_sheet_to_df


def df_splitter(df_from_sheet):
    """
    이 함수는 df에서 랜덤으로 데이터를 추출하여 검증, 테스트, 훈련용 데이터를 반환합니다.
    Parameters:
    pandas DataFrame
        'input'과 'output' column이 존재해야함
    
    Returns:
    val_df: pandas DataFrame
        검증용 데이터 (5개의 샘플)
    test_df: pandas DataFrame
        테스트용 데이터 (5개의 샘플)
    train_df: pandas DataFrame
        훈련용 데이터 (나머지 데이터)
    """
    # sheet_df 에서 랜덤추출하여 검증,테스트,훈련용 df를 return함
    df = df_from_sheet[['input', 'output']]
    df = df.dropna(subset=['output'])
    total_rows = len(df)
    
    if total_rows < 20:
        raise ValueError(f"데이터가 충분하지 않습니다. 최소 20개 이상의 유효한 데이터가 필요합니다. 현재 행 개수: {total_rows}")
    
    val_test_data = df.sample(10,random_state=42)
    val_df = val_test_data.head(5)
    test_df = val_test_data.tail(5)
    train_df = df[~df.index.isin(val_test_data.index)]
    
    return val_df,test_df,train_df



def format_to_jsonl(type, df, sys_prompt, string):
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