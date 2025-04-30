from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import subprocess
import json
from app.config import CSV_FILE_PATH, CLASSIFIER_FILE_PATH
from app.utils.helpers import send_to_queue

router = APIRouter()

@router.post("/classify")
async def classify_categories(request: Request):
		try:
			data = await request.json()
			csv_file_path = CSV_FILE_PATH
			classifier_file_path = CLASSIFIER_FILE_PATH

			# props가 데이터에 포함되어 있는지 확인
			props = data.get('props')

			# 만약 props에 reply_to나 correlation_id가 없으면 오류 반환
			if not props or not props.get('reply_to') or not props.get('correlation_id'):
					response_content = {"stateCode": "MTCH-001", "message": "Field Missing"}
					await send_to_queue(None, props, response_content)
					return JSONResponse(content={"error": "Missing properties (reply_to or correlation_id)"}, status_code=400)

			# 필수 필드 확인
			required_fields = ["uuid", "smallCategory"]
			for field in required_fields:
					if field not in data:
							response_content = {"stateCode": "MTCH-001", "message": "Field Missing"}
							await send_to_queue(None, props, response_content)
							return JSONResponse(content=response_content, status_code=400)

			result = subprocess.run(['python', classifier_file_path], capture_output=True, text=True)
			if result.returncode != 0:
					response_content = {"stateCode": "MTCH-005", "message": "Error running classifier script"}
					await send_to_queue(None, props, response_content)
					response_content.update({"details": str(e)})
					return JSONResponse(content=response_content, status_code=500)

		except json.JSONDecodeError as e:
			response_content = {"stateCode": "MTCH-003", "message": "Invalid JSON format"}
			await send_to_queue(None, data.get("props", {}), response_content)
			response_content.update({"details": str(e)})
			return JSONResponse(content=response_content, status_code=400)

		except Exception as e:
			response_content = {"stateCode": "MTCH-004", "message": "An unexpected error occurred"}
			await send_to_queue(None, data.get("props", {}), response_content)
			response_content.update({"details": str(e)})
			return JSONResponse(content=response_content, status_code=500)
