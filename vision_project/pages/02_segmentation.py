# 페이지 목표
# title: Segmentation 체험하기
# markdown ## Segmentation
# markdwon Segmentation 설명 
# 파일 업로더
# 추출하기 버튼
# 버튼을 누르면 yolo로 이미지 예측해서 결과 반환하기
# 마스크 이미지 띄우기

import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import requests

API_URL = "http://localhost:8080"

# -----------------------------
# 페이지 기본 설정
# -----------------------------
st.set_page_config(
    page_title="Segmentation 체험하기",
    page_icon="🖼️",
    layout="wide"
)

# -----------------------------
# CSS 스타일 (모노톤)
# -----------------------------
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background-color: #f5f5f5;
    }

    /* 기본 텍스트 */
    html, body, [class*="css"]  {
        color: #111111;
        font-family: "Pretendard", "Noto Sans KR", sans-serif;
    }

    /* 상단 헤더 박스 */
    .hero-box {
        background: #ffffff;
        border: 1px solid #d9d9d9;
        border-radius: 18px;
        padding: 32px 28px;
        margin-bottom: 24px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    .hero-title {
        font-size: 34px;
        font-weight: 800;
        color: #111111;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        font-size: 16px;
        color: #4a4a4a;
        line-height: 1.7;
    }

    /* 설명 카드 */
    .info-card {
        background: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 16px;
        padding: 22px;
        margin-top: 8px;
        margin-bottom: 24px;
    }

    .info-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 12px;
        color: #111111;
    }

    .info-text {
        font-size: 15px;
        line-height: 1.8;
        color: #444444;
    }

    /* 업로드 카드 */
    .upload-card {
        background: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
    }

    /* 결과 카드 */
    .result-card {
        background: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 16px;
        padding: 20px;
        margin-top: 20px;
    }

    .section-label {
        font-size: 18px;
        font-weight: 700;
        color: #111111;
        margin-bottom: 10px;
    }

    /* 버튼 */
    div.stButton > button {
        width: 100%;
        background-color: #111111;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 18px;
        font-size: 16px;
        font-weight: 700;
    }

    div.stButton > button:hover {
        background-color: #2a2a2a;
        color: white;
    }

    /* 파일 업로더 */
    [data-testid="stFileUploader"] {
        background: #fafafa;
        border: 1px dashed #b8b8b8;
        border-radius: 14px;
        padding: 10px;
    }

    /* 알림 */
    .small-note {
        color: #666666;
        font-size: 13px;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 마스크 합치기 함수
# -----------------------------
def make_combined_mask(result):
    """
    result.masks.data:
    shape = (객체수, H, W)
    여러 개의 마스크가 있으면 하나의 흑백 마스크로 합칩니다.
    """
    if result.masks is None:
        return None

    masks = result.masks.data.cpu().numpy()   # (N, H, W)
    combined = np.any(masks > 0.5, axis=0).astype(np.uint8) * 255  # (H, W)
    return combined

# -----------------------------
# 상단 소개 영역
# -----------------------------
st.markdown("""
<div class="hero-box">
    <div class="hero-title">Segmentation 체험하기</div>
    <div class="hero-subtitle">
        업로드한 이미지에서 YOLO Segmentation 모델이 객체 영역을 분리합니다.<br>
        예측 결과를 바탕으로 <b>마스크 이미지</b>를 확인할 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-card">
    <div class="info-title">Segmentation</div>
    <div class="info-text">
        - Segmentation은 이미지를 입력 받아 객체를 픽셀 단위로 구분하는 모델입니다.<br>
        - 이미지를 입력하면 객체의 정확한 모양과 영역을 찾아냅니다.<br>
        - 의료영상, 자율주행, 불량검사, 배경 제거처럼 정밀한 영역 분석이 필요한 곳에 쓰입니다.<br>
        - 라벨링이 어렵고 계산량이 커 학습과 추론 비용이 더 크게 들어갑니다.<br>
        - 빠른 위치 탐지는 detection, 정밀한 영역 분리는 segmentation이 더 적합합니다.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 업로드 영역
# -----------------------------
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">이미지 업로드</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    label="파일을 업로드 하세요",
    type=["jpg", "jpeg", "png"]
)

st.markdown('<div class="small-note">지원 형식: JPG, JPEG, PNG</div>', unsafe_allow_html=True)

predict_button = st.button("예측하기")
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 예측 실행
# -----------------------------
if predict_button:
    if uploaded_file is None:
        st.warning("먼저 이미지를 업로드하세요.")
    else:
        image = Image.open(uploaded_file).convert("RGB")
        image_np = np.array(image)

        with st.spinner("이미지를 분석하는 중입니다..."):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            response = requests.post(
                url = f"{API_URL}/detect_image_seg",
                files=files, 
                timeout=60
            )
            response.raise_for_status()
            result_json = response.json()

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">예측 결과</div>', unsafe_allow_html=True)

