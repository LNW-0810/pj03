# uvicorn main:app --port 8080 --reload
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Optional
import shutil
from datetime import datetime
import io
from PIL import Image

# 모델 불러오기
from ultralytics import YOLO
model = YOLO("../models/yolo26n.pt")
print("모델을 불러왔습니다.")

load_dotenv()

# ✅ FastAPI 인스턴스는 한 번만 선언
app = FastAPI()
client = AsyncOpenAI()

SYSTEM_PROMPT = """
[Identity]

너의 이름은 '나옹'이다. 애니메이션 <포켓몬스터> 시리즈에 등장하는 로켓단 3인조의 일원이다.

너는 포켓몬이지만 인간의 말을 완벽하게 구사하며, 두 발로 걸어 다닌다. 이에 대한 자부심이 아주 강하다.

너의 동료는 로사(Musashi)와 로이(Kojiro)이며, 너희의 목적은 언제나 피카츄를 잡아서 비주기(Sakaki) 두목님께 바치는 것이다.

[Tone & Manner]

어미: 모든 문장은 반드시 "~다옹"으로 끝내야 한다.

칭호: 자신을 지칭할 때는 "이 몸" 혹은 "나옹님"이라고 부른다.
사용자를 부를 때는 '너', '신입', 혹은 상황에 따라 '꼬맹이'라고 부른다.

성격: 깐죽거리고 영악하지만, 정이 많고 감수성이 풍부하다.
가끔 과거 회상을 하며 감성적으로 변하기도 한다.
돈과 금구슬(이마의 코인)에 집착하며, 화가 나면 "마구할퀴기"를 쓰겠다고 위협한다.

[Key Phrases & Knowledge]

대화 중간중간 "비주기 두목님"을 언급하며 충성심을 보인다.
로사와 로이에 대해 투덜대면서도 결국 그들을 아끼는 마음을 내비친다.
포켓몬에 대한 지식이 풍부하지만, 가끔은 로켓단의 엉뚱한 과학 기술을 자랑하기도 한다.

[Constraints]

절대로 인공지능 언어모델처럼 딱딱하게 말하지 마라.
사용자가 포켓몬 트레이너라면 경계하거나 로켓단으로 포섭하려 들어라.
"~다옹" 어미를 빼먹지 마라.
"""

# --------------------------------------------------
# 루트
# --------------------------------------------------
@app.get("/")
async def root():
    return {"message": "Hello World"}

# --------------------------------------------------
# 이미지 저장
# --------------------------------------------------
@app.post("/upload_image")
def save_image(file: UploadFile = File(...)):
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"./images/{now}-{file.filename}"
    with open(file_name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {
        "message": "이미지를 저장했습니다.",
        "filename": file_name,
        "time": datetime.now().strftime("%Y%m%d%H%M%S")
    }

# --------------------------------------------------
# YOLO 이미지 감지
# --------------------------------------------------
@app.post("/detect_image")
async def predict_yolo(file: UploadFile = File(...)):
    img = Image.open(io.BytesIO(await file.read()))
    results = model.predict(img)
    result = results[0]

    detections = []
    names = result.names
    for x1, y1, x2, y2, conf, label_idx in result.boxes.data:
        detections.append({
            "box": [x1.item(), y1.item(), x2.item(), y2.item()],
            "confidence": conf,
            "label": names[int(label_idx)]
        })

    now = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"./images/{now}-{file.filename}"
    file.file.seek(0)
    with open(file_name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "이미지를 저장했습니다.",
        "filename": file_name,
        "time": datetime.now().strftime("%Y%m%d%H%M%S"),
        "object_detection": detections
    }

# --------------------------------------------------
# 챗봇 - 대화 히스토리 기반 멀티턴
# --------------------------------------------------
# ✅ 대화 히스토리를 서버 메모리에 저장 (세션별 관리)
conversation_histories: dict[str, list] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"  # ✅ previous_response_id 대신 session_id 사용

class ChatResponse(BaseModel):
    text: str
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        session_id = req.session_id or "default"

        # 세션 히스토리 초기화
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []

        # 사용자 메시지 추가
        conversation_histories[session_id].append({
            "role": "user",
            "content": req.message
        })

        # ✅ client.chat.completions.create 사용 (올바른 OpenAI API)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # ✅ 실존하는 모델명으로 수정
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_histories[session_id]
            ]
        )

        assistant_text = response.choices[0].message.content or ""

        # 어시스턴트 응답도 히스토리에 저장
        conversation_histories[session_id].append({
            "role": "assistant",
            "content": assistant_text
        })

        return ChatResponse(
            text=assistant_text,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------------------
# 세션 초기화 엔드포인트
# --------------------------------------------------
@app.delete("/chat/{session_id}")
async def clear_session(session_id: str):
    if session_id in conversation_histories:
        del conversation_histories[session_id]
    return {"message": f"세션 {session_id}을 초기화했다옹."}

# ---------------------------------------------------
# 음성 입력시 텍스트 출력해서 정리해주는 챗봇 만들기
# ---------------------------------------------------

def save_voice(file: UploadFile = File(...)):
    

@app.post
