import streamlit as st
from ultralytics import YOLO
from PIL import Image, ImageDraw
import numpy as np
import requests

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="Object Detection 체험하기",
    page_icon="🎯",
    layout="wide"
)

API_URL = "http://127.0.0.1:8080"

# -----------------------------
# 모델 로드
# -----------------------------
@st.cache_resource
def load_model():
    return YOLO("./models/yolo26n.pt")

model = load_model()

# -----------------------------
# CSS 스타일
# -----------------------------
st.markdown("""
<style>
/* 전체 배경 */
.stApp {
    background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
}

/* 전체 컨테이너 여백 */
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* 상단 히어로 */
.hero-box {
    background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #60a5fa 100%);
    border-radius: 28px;
    padding: 40px 36px;
    color: white;
    box-shadow: 0 20px 45px rgba(37, 99, 235, 0.18);
    margin-bottom: 24px;
}

.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 999px;
    padding: 7px 14px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 16px;
}

.hero-title {
    font-size: 40px;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 12px;
}

.hero-desc {
    font-size: 16px;
    line-height: 1.7;
    color: rgba(255,255,255,0.92);
    max-width: 760px;
}

/* 일반 카드 */
.glass-card {
    background: rgba(255,255,255,0.82);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(203, 213, 225, 0.7);
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
    margin-bottom: 18px;
}

/* 섹션 제목 */
.section-title {
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 8px;
}

.section-desc {
    font-size: 15px;
    color: #475569;
    margin-bottom: 8px;
    line-height: 1.7;
}

/* 업로드 박스 강조 */
.upload-guide {
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    border: 1px dashed #60a5fa;
    border-radius: 18px;
    padding: 16px 18px;
    margin-bottom: 12px;
    color: #1e3a8a;
    font-size: 14px;
    line-height: 1.7;
}

/* expander */
div[data-testid="stExpander"] {
    border: none !important;
    background: transparent !important;
}

div[data-testid="stExpander"] details {
    background: rgba(255,255,255,0.82) !important;
    border: 1px solid rgba(203, 213, 225, 0.7) !important;
    border-radius: 24px !important;
    padding: 8px 14px !important;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
}

/* file uploader */
div[data-testid="stFileUploader"] {
    background: white;
    border: 1.5px dashed #93c5fd;
    border-radius: 20px;
    padding: 10px;
}

/* 버튼 */
div.stButton > button {
    width: 100%;
    height: 52px;
    border: none;
    border-radius: 16px;
    background: linear-gradient(135deg, #2563eb 0%, #3b82f6 55%, #60a5fa 100%);
    color: white;
    font-size: 17px;
    font-weight: 700;
    box-shadow: 0 12px 22px rgba(37, 99, 235, 0.22);
    transition: all 0.2s ease-in-out;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 16px 28px rgba(37, 99, 235, 0.28);
}

/* 결과 메트릭 카드 */
.metric-card {
    background: white;
    border-radius: 20px;
    padding: 18px 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    text-align: center;
}

.metric-label {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 8px;
    font-weight: 600;
}

.metric-value {
    font-size: 26px;
    color: #0f172a;
    font-weight: 800;
}

/* 결과 카드 */
.detect-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.detect-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}

.detect-label {
    font-size: 18px;
    font-weight: 800;
    color: #0f172a;
}

.detect-badge {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    color: #1d4ed8;
    border-radius: 999px;
    padding: 6px 12px;
    font-size: 13px;
    font-weight: 700;
}

.detect-coord {
    color: #475569;
    font-size: 14px;
    line-height: 1.7;
}

/* 안내 문구 */
.info-soft {
    padding: 14px 16px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 16px;
    color: #1e3a8a;
    font-size: 14px;
    line-height: 1.7;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 상단 히어로 영역
# -----------------------------
st.markdown("""
<div class="hero-box">
    <div class="hero-badge">YOLO Object Detection Demo</div>
    <div class="hero-title">Object Detection 체험하기</div>
    <div class="hero-desc">
        이미지를 업로드하고 YOLO 모델이 어떤 객체를 찾는지 확인해보세요.
        객체의 종류, 신뢰도, 위치 좌표까지 한 번에 볼 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 설명
# -----------------------------
with st.expander(label="모델 카드", expanded=True):
    st.markdown("""
    <div class="section-title">Object Detection YOLO 모델</div>
    <div class="section-desc">
        - object detection은 이미지를 입력 받아 객체 탐지를 하는 모델입니다.<br>
        - 이미지를 입력하면 학습된 데이터를 바탕으로 추론값을 내뱉습니다.<br>
        - object detection으로 사람, 차량, 이상행동 등을 탐지할 수 있습니다.<br>
        - object detection을 학습할 때에는 라벨링 품질, 다양한 데이터, 데이터 분리 등을 주의해야 합니다.
    </div>
    <div class="info-soft">
        이 데모에서는 업로드한 이미지에 대해 YOLO 추론을 수행하고,
        탐지된 객체를 시각화해서 보여줍니다.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# 파일 업로드 섹션
# -----------------------------
st.markdown("""
<div class="glass-card">
    <div class="section-title">이미지 업로드</div>
    <div class="section-desc">
        JPG, JPEG, PNG 형식의 이미지를 업로드한 뒤 예측 버튼을 눌러보세요.
    </div>
    <div class="upload-guide">
        권장: 객체가 비교적 선명하게 보이는 이미지를 사용하면 탐지 결과가 더 안정적으로 나옵니다.
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    label="이미지를 업로드 하세요",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

# -----------------------------
# 업로드 이미지 표시
# -----------------------------
image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">업로드한 이미지</div>', unsafe_allow_html=True)

    _, col, _ = st.columns([0.8, 1.6, 0.8])
    with col:
        st.image(
            image,
            caption="원본 이미지",
            use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 버튼
# -----------------------------
predict_button = st.button(
    "예측하기",
    type="primary",
    use_container_width=True
)

# -----------------------------
# 예측 실행
# -----------------------------
if predict_button:
    if uploaded_file is None:
        st.warning("먼저 이미지를 업로드해주세요.")
    else:
        with st.spinner("백엔드 서버에 요청 중입니다..."):
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
            }

            try:
                response = requests.post(
                    f"{API_URL}/detect_image",
                    files=files,
                    timeout=60
                )
                response.raise_for_status()
                result_json = response.json()

            except requests.exceptions.RequestException as e:
                st.error(f"요청 중 오류가 발생했습니다: {e}")
                st.stop()

        detections = result_json.get("object_detection", [])

        # 결과 이미지에 박스 그리기
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)

        for det in detections:
            x1, y1, x2, y2 = det["box"]
            label = det["label"]
            conf = det["confidence"]

            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
            draw.text((x1, max(y1 - 20, 0)), f"{label} {conf:.2f}", fill="red")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 원본 이미지")
            st.image(image, use_container_width=True)

        with col2:
            st.markdown("### 예측 결과")
            st.image(draw_image, use_container_width=True)

        st.markdown("### 탐지 결과")

        if detections:
            for i, det in enumerate(detections, start=1):
                x1, y1, x2, y2 = det["box"]
                label = det["label"]
                conf = det["confidence"]

                st.markdown(f"""
                <div class="result-card">
                    <b>{i}. {label}</b><br>
                    신뢰도: {conf:.2f}<br>
                    좌표: ({x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f})
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("탐지된 객체가 없습니다.")