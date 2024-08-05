from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tritonclient.http as httpclient
import numpy as np

app = FastAPI()

# Triton 서버의 REST API 주소를 설정합니다.
TRITON_SERVER_URL = "your_triton_server_ip:8000"

class RecommendationRequest(BaseModel):
    user_index: int
    user_age_preference: str
    avoid_same_major: bool

@app.post("/recommend")
def recommend(request: RecommendationRequest):
    try:
        # Triton 클라이언트 생성
        triton_client = httpclient.InferenceServerClient(url=TRITON_SERVER_URL)

        # 입력 데이터 설정
        inputs = [
            httpclient.InferInput("user_index", [1], "INT32"),
            httpclient.InferInput("user_age_preference", [1], "BYTES"),
            httpclient.InferInput("avoid_same_major", [1], "BOOL")
        ]

        inputs[0].set_data_from_numpy(np.array([request.user_index], dtype=np.int32))
        inputs[1].set_data_from_numpy(np.array([request.user_age_preference.encode()], dtype=bytes))
        inputs[2].set_data_from_numpy(np.array([request.avoid_same_major], dtype=bool))

        # 출력 데이터 설정
        outputs = [
            httpclient.InferRequestedOutput("RECOMMENDATION")
        ]

        # Triton 서버에 추론 요청
        response = triton_client.infer(
            model_name="user_recommendation",
            inputs=inputs,
            outputs=outputs
        )

        # 추론 결과 받아오기
        recommendation = response.as_numpy("RECOMMENDATION")[0].decode("utf-8")

        # 결과 반환
        return {"recommendation": recommendation}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
