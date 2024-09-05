import tiktoken
from forex_python.converter import CurrencyRates



# 토큰 수 계산
def calculate_cost(df,model):

    def tokens_from_string(string):
        encoding = tiktoken.get_encoding('cl100k_base')
        num_tokens = len(encoding.encode(string))
        return num_tokens
    
    def get_base_model(model):
    # ft:로 시작하면 ':' 이후의 값을 사용하고, 그렇지 않으면 model 그대로 사용
        base_model = model.split(":")[1] if model.startswith('ft:') else model
        
        # 1. 먼저 정확히 일치하는 모델이 있는지 확인
        if base_model in MODEL_PRICES:
            return base_model

        # 2. 정확히 일치하는 모델이 없으면, 접두사 매칭 방식 사용
        for key in MODEL_PRICES.keys():
            if base_model.startswith(key):
                return key  # 접두사에 매칭된 키값을 반환
        
        # 3. 매칭되는 모델이 없을 경우 None 반환
        return None
    
    MODEL_PRICES = {
        'gpt-4o': 25 / 1000000,  # 예시 가격 (per 1k tokens)
        'gpt-4o-mini': 3 / 1000000,  # 예시 가격 (per 1k tokens)
        'gpt-3.5-turbo': 8 / 1000000,  # 예시 가격 (per 1k tokens)
        'davinci-002': 6 / 1000000,  # 예시 가격 (per 1k tokens)
        'babbage-002': 0.4 / 1000000,  # 예시 가격 (per 1k tokens)
        }
    
    base_model = get_base_model(model)
    

    total_tokens = df['input'].apply(tokens_from_string).sum() + df['output'].apply(tokens_from_string).sum()
    model_price_per_token = MODEL_PRICES.get(base_model, 0.0004)  # 0.0004는 해당 모델이 없을경우 기본값을 0.0004로 잡겠다는 것임

    #c = CurrencyRates() # 환율정보 가져오기
    #ex_rate = c.get_rate('USD','KRW') # 원달러 환율
    ex_rate = 1330
    total_cost = total_tokens * model_price_per_token * ex_rate

    return total_cost, total_tokens


