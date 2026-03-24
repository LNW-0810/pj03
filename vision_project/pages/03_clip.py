import streamlit as st
from transformers import CLIPModel, CLIPProcessor
import torch
from PIL import Image

# -----------------------------
# 페이지 기본 설정
# -----------------------------
st.set_page_config(
    page_title="CLIP 동물 유사도 테스트",
    page_icon="🐾",
    layout="wide"
)

# -----------------------------
# 모델 캐싱
# -----------------------------
@st.cache_resource
def load_clip():
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()
    return model, processor, device

model, processor, device = load_clip()

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
/* 전체 배경 */
.stApp {
    background: linear-gradient(180deg, #fffafc 0%, #fff1f7 45%, #fef6ff 100%);
}

/* 전체 여백 */
.block-container {
    max-width: 1150px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

/* 상단 배너 */
.hero-wrap {
    background: linear-gradient(135deg, #ffb7d5 0%, #ffc8dd 45%, #cdb4db 100%);
    border-radius: 32px;
    padding: 36px 34px;
    box-shadow: 0 18px 40px rgba(214, 107, 154, 0.18);
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
}

.hero-wrap::after {
    content: "🐶 🐱 🐷";
    position: absolute;
    right: 24px;
    top: 20px;
    font-size: 34px;
    opacity: 0.28;
}

.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.38);
    border: 1px solid rgba(255,255,255,0.45);
    border-radius: 999px;
    padding: 7px 14px;
    font-size: 13px;
    font-weight: 700;
    color: #7a3057;
    margin-bottom: 14px;
}

.hero-title {
    font-size: 38px;
    font-weight: 900;
    color: #5b2242;
    margin-bottom: 10px;
    line-height: 1.2;
}

.hero-desc {
    font-size: 16px;
    line-height: 1.8;
    color: #6f3654;
    max-width: 760px;
}

/* 카드 */
.soft-card {
    background: rgba(255,255,255,0.85);
    border: 1px solid #f6d3e0;
    border-radius: 26px;
    padding: 24px;
    box-shadow: 0 10px 28px rgba(160, 98, 128, 0.08);
    margin-bottom: 18px;
}

/* 제목 */
.section-title {
    font-size: 24px;
    font-weight: 900;
    color: #6e2d50;
    margin-bottom: 8px;
}

.section-desc {
    font-size: 15px;
    line-height: 1.8;
    color: #7a4a61;
}

/* 안내 박스 */
.tip-box {
    background: linear-gradient(135deg, #fff2f8 0%, #ffeaf3 100%);
    border: 1px dashed #f0a9c4;
    border-radius: 18px;
    padding: 14px 16px;
    color: #934d6d;
    font-size: 14px;
    line-height: 1.8;
    margin-top: 12px;
}

/* 업로더 */
div[data-testid="stFileUploader"] {
    background: #fffdfd;
    border: 2px dashed #f3b1cb;
    border-radius: 22px;
    padding: 10px;
}

/* 버튼 */
div.stButton > button {
    width: 100%;
    height: 54px;
    border-radius: 18px;
    border: none;
    background: linear-gradient(135deg, #ff8fab 0%, #ffb3c6 55%, #ffc2d1 100%);
    color: #6b2143;
    font-size: 18px;
    font-weight: 900;
    box-shadow: 0 12px 24px rgba(255, 143, 171, 0.28);
    transition: all 0.2s ease-in-out;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 16px 28px rgba(255, 143, 171, 0.34);
}

/* 결과 요약 카드 */
.result-highlight {
    background: linear-gradient(135deg, #fff4f8 0%, #fff9fc 100%);
    border: 1px solid #f7cfde;
    border-radius: 22px;
    padding: 18px;
    text-align: center;
    margin-bottom: 16px;
}

.result-highlight .top {
    font-size: 14px;
    color: #a25377;
    font-weight: 700;
    margin-bottom: 6px;
}

.result-highlight .main {
    font-size: 30px;
    color: #7e2951;
    font-weight: 900;
}

.result-highlight .sub {
    font-size: 14px;
    color: #8c5970;
    margin-top: 6px;
}

/* 확률 카드 */
.prob-card {
    background: white;
    border: 1px solid #f2d7e2;
    border-radius: 20px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: 0 8px 20px rgba(174, 112, 137, 0.07);
}

.prob-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.prob-label {
    font-size: 18px;
    font-weight: 900;
    color: #6f2d50;
}

.prob-score {
    font-size: 15px;
    font-weight: 800;
    color: #96506f;
    background: #fff1f6;
    border-radius: 999px;
    padding: 6px 12px;
}

.bar-bg {
    width: 100%;
    height: 14px;
    background: #fde6ef;
    border-radius: 999px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #ff8fab 0%, #ffb3c6 100%);
}

/* 순위 뱃지 */
.rank-badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: #ffe7f0;
    color: #9b456a;
    font-size: 12px;
    font-weight: 800;
    margin-left: 8px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 상단 영역
# -----------------------------
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">CLIP Similarity Demo</div>
    <div class="hero-title">📎 CLIP 동물 유사도 테스트</div>
    <div class="hero-desc">
        이미지를 업로드하면 CLIP 모델이 사진을 보고
        <b>강아지 / 고양이 / 돼지</b> 중 어떤 단어와 가장 비슷한지 확률 형태로 보여줍니다.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 모델 설명
# -----------------------------
with st.expander("모델 카드", expanded=True):
    st.markdown("""
    <div class="section-title">CLIP 모델</div>
    <div class="section-desc">
        <ul>
            <li>CLIP은 이미지와 텍스트를 같은 공간에서 비교할 수 있게 학습된 모델입니다.</li>
            <li>즉, 사진과 단어가 얼마나 비슷한지를 점수로 계산할 수 있습니다.</li>
            <li>이 페이지에서는 업로드한 이미지가 강아지, 고양이, 돼지 중 어떤 텍스트와 가장 가까운지 비교합니다.</li>
            <li>결과는 확률처럼 보이도록 softmax를 적용해서 출력합니다.</li>
        </ul>
    </div>
    <div class="tip-box">
        참고: CLIP은 영어 프롬프트에서 비교적 안정적으로 동작하는 경우가 많아서,
        내부 비교는 영어 문장으로 하고 화면에는 한국어 이름으로 보여줍니다.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# 업로드 영역
# -----------------------------
st.markdown("""
<div class="soft-card">
    <div class="section-title">이미지 업로드</div>
    <div class="section-desc">
        동물 사진을 업로드한 뒤 예측 버튼을 눌러보세요.
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    label="파일을 업로드하세요.",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">업로드한 이미지</div>', unsafe_allow_html=True)

    _, col, _ = st.columns([0.7, 1.6, 0.7])
    with col:
        st.image(image, caption="미리보기", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 버튼
# -----------------------------
predict_button = st.button(
    label="예측하기",
    type="primary",
    use_container_width=True
)

# -----------------------------
# 예측
# -----------------------------
if predict_button:
    if uploaded_file is None:
        st.warning("먼저 이미지를 업로드해주세요.")
    else:
        with st.spinner("CLIP이 이미지를 분석 중입니다..."):
            # 화면 표시용 한국어 / 모델 입력용 영어 프롬프트
            labels_kr = ["강아지", "고양이", "돼지"]
            labels_en = [
                "a photo of a dog",
                "a photo of a cat",
                "a photo of a pig"
            ]

            inputs = processor(
                text=labels_en,
                images=image,
                return_tensors="pt",
                padding=True
            )

            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)[0].detach().cpu().tolist()

            result_pairs = list(zip(labels_kr, probs))
            result_pairs.sort(key=lambda x: x[1], reverse=True)

            top_label, top_prob = result_pairs[0]

        st.markdown("""
        <div class="soft-card">
            <div class="section-title">예측 결과</div>
            <div class="section-desc">
                업로드한 이미지와 각 동물 단어의 유사도를 확률 형태로 정리했습니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 상단 대표 결과
        st.markdown(f"""
        <div class="result-highlight">
            <div class="top">가장 유사한 결과</div>
            <div class="main">{top_label}</div>
            <div class="sub">예측 확률 {top_prob * 100:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

        # 이미지 + 결과
        left, right = st.columns([1.1, 1.2])

        with left:
            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">입력 이미지</div>', unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">확률 분포</div>', unsafe_allow_html=True)

            for rank, (label, prob) in enumerate(result_pairs, start=1):
                percent = prob * 100

                st.markdown(f"""
                <div class="prob-card">
                    <div class="prob-top">
                        <div class="prob-label">
                            {label}
                            <span class="rank-badge">{rank}위</span>
                        </div>
                        <div class="prob-score">{percent:.2f}%</div>
                    </div>
                    <div class="bar-bg">
                        <div class="bar-fill" style="width: {percent:.2f}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # 표 형태 결과도 같이 표시
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">숫자 결과</div>', unsafe_allow_html=True)

        for label, prob in result_pairs:
            st.write(f"- {label}: {prob * 100:.2f}%")

        st.markdown('</div>', unsafe_allow_html=True)