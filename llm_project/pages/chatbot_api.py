import streamlit as st
import requests
import uuid

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="로켓단 나옹 챗봇",
    page_icon="😼",
    layout="centered"
)

API_URL = "http://localhost:8080/chat"

# --------------------------------------------------
# CSS 스타일 (index.html 디자인 그대로)
# --------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">

<style>
/* ===== 전체 배경 ===== */
.stApp {
    background:
        radial-gradient(ellipse 70% 50% at 10% 5%, rgba(214,31,58,0.12), transparent),
        radial-gradient(ellipse 60% 40% at 90% 10%, rgba(255,215,0,0.08), transparent),
        radial-gradient(ellipse 80% 60% at 50% 100%, rgba(214,31,58,0.06), transparent),
        #0d0d0d;
    color: #e8e0d0;
    font-family: 'Noto Sans KR', sans-serif;
}

/* dot overlay */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background-image: radial-gradient(circle, rgba(255,255,255,0.018) 1px, transparent 1px);
    background-size: 36px 36px;
    pointer-events: none;
}

.block-container {
    max-width: 860px;
    padding-top: 1.5rem;
    padding-bottom: 1rem;
}

/* ===== 히어로 카드 ===== */
.hero-card {
    background: linear-gradient(135deg, #1a0a0e 0%, #200c12 40%, #161616 100%);
    border: 1px solid rgba(214,31,58,0.25);
    border-left: 5px solid #d61f3a;
    border-radius: 20px;
    padding: 20px 22px 18px;
    box-shadow: 0 0 40px rgba(214,31,58,0.12), 0 8px 32px rgba(0,0,0,0.5);
    position: relative;
    overflow: hidden;
    margin-bottom: 16px;
    animation: heroIn 0.7s cubic-bezier(.22,1,.36,1) both;
}
@keyframes heroIn {
    from { opacity: 0; transform: translateY(-18px); }
    to   { opacity: 1; transform: translateY(0); }
}
.hero-card::after {
    content: '🪙';
    position: absolute;
    top: -8px; right: 20px;
    font-size: 3rem;
    opacity: 0.18;
    transform: rotate(-15deg);
    pointer-events: none;
}
.hero-top {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 12px;
}
.avatar-wrap { position: relative; flex-shrink: 0; }
.avatar {
    width: 64px; height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2a0a10, #3a1020);
    border: 2px solid #d61f3a;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem;
    box-shadow: 0 0 18px rgba(214,31,58,0.45);
    animation: coinGlow 3s ease-in-out infinite;
}
@keyframes coinGlow {
    0%, 100% { box-shadow: 0 0 18px rgba(214,31,58,0.45); }
    50%       { box-shadow: 0 0 32px rgba(214,31,58,0.45), 0 0 8px rgba(255,215,0,0.55); }
}
.avatar-badge {
    position: absolute;
    bottom: -3px; right: -3px;
    background: #ffd700;
    color: #111;
    font-size: 0.58rem;
    font-weight: 900;
    padding: 2px 5px;
    border-radius: 6px;
    font-family: 'Black Han Sans', sans-serif;
}
.hero-title-block h1 {
    font-family: 'Black Han Sans', sans-serif;
    font-size: 1.5rem;
    color: #fff;
    line-height: 1.2;
    margin-bottom: 3px;
}
.hero-title-block h1 span { color: #d61f3a; }
.hero-title-block p { font-size: 0.8rem; color: #a09888; letter-spacing: 0.08em; }
.hero-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.tag {
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
}
.tag-red  { background: rgba(214,31,58,0.2); color: #ffb0bb; border: 1px solid rgba(214,31,58,0.3); }
.tag-gold { background: rgba(255,215,0,0.12); color: #ffd700; border: 1px solid rgba(255,215,0,0.25); }
.tag-gray { background: rgba(255,255,255,0.06); color: #b0b0b0; border: 1px solid rgba(255,255,255,0.1); }
.hero-info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
}
.info-chip {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 10px 12px;
}
.info-chip .label {
    font-size: 0.68rem;
    color: #ffd700;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 3px;
}
.info-chip .value { font-size: 0.82rem; color: #e8e0d0; line-height: 1.4; }

/* ===== 채팅 메시지 ===== */
[data-testid="stChatMessage"] {
    border-radius: 18px !important;
    padding: 4px 8px !important;
    margin-bottom: 4px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    animation: msgIn 0.4s cubic-bezier(.22,1,.36,1) both;
}
@keyframes msgIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
/* 사용자 메시지 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, rgba(214,31,58,0.18), rgba(180,20,40,0.08)) !important;
    border-color: rgba(214,31,58,0.22) !important;
}
/* 어시스턴트 메시지 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(200,160,0,0.04)) !important;
    border-color: rgba(255,215,0,0.18) !important;
}
/* 메시지 텍스트 색상 */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] .stMarkdown {
    color: #363430 !important;
}

/* ===== 입력창 ===== */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 18px !important;
    color: #e8e0d0 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(214,31,58,0.5) !important;
    box-shadow: 0 0 0 3px rgba(214,31,58,0.1) !important;
}
[data-testid="stChatInput"] textarea {
    color: #e8e0d0 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ===== 퀵 리플라이 버튼 ===== */
.quick-btn-wrap {
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}
.quick-btn {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,215,0,0.22);
    color: #ffd700;
    border-radius: 99px;
    padding: 6px 14px;
    font-size: 0.78rem;
    font-family: 'Noto Sans KR', sans-serif;
    cursor: pointer;
    transition: all 0.18s ease;
    white-space: nowrap;
}
.quick-btn:hover {
    background: rgba(255,215,0,0.1);
    border-color: #ffd700;
    box-shadow: 0 0 12px rgba(255,215,0,0.2);
}

/* Streamlit 버튼 -> 퀵리플라이 스타일 */
[data-testid="stHorizontalBlock"] .stButton button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,215,0,0.3) !important;
    color: #ffd700 !important;
    border-radius: 99px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 0.78rem !important;
    padding: 4px 14px !important;
    transition: all 0.18s ease !important;
}
[data-testid="stHorizontalBlock"] .stButton button:hover {
    background: rgba(255,215,0,0.1) !important;
    border-color: #ffd700 !important;
    box-shadow: 0 0 12px rgba(255,215,0,0.2) !important;
    color: #fff !important;
}

/* ===== 구분선 ===== */
.rocket-divider {
    display: flex; align-items: center; gap: 10px;
    margin: 8px 0;
}
.rocket-divider::before,
.rocket-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(214,31,58,0.25), transparent);
}
.rocket-divider span {
    font-size: 0.7rem;
    color: rgba(214,31,58,0.5);
    letter-spacing: 0.12em;
    font-weight: 700;
    font-family: 'Black Han Sans', sans-serif;
}

/* ===== 푸터 ===== */
.footer-note {
    text-align: center;
    font-size: 0.72rem;
    color: #a09888;
    margin-top: 6px;
    opacity: 0.7;
}
.footer-note span { color: #d61f3a; }

/* ===== 일반 텍스트 ===== */
html, body, [class*="css"] { color: #e8e0d0; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 세션 초기화
# --------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "session_id" not in st.session_state:
    st.session_state["session_id"] = "session-" + str(uuid.uuid4())[:8]

if "quick_input" not in st.session_state:
    st.session_state["quick_input"] = None

# --------------------------------------------------
# 히어로 카드 (상단 소개)
# --------------------------------------------------
st.markdown("""
<div class="hero-card">
  <div class="hero-top">
    <div class="avatar-wrap">
      <div class="avatar">😼</div>
      <div class="avatar-badge">ROCKET</div>
    </div>
    <div class="hero-title-block">
      <h1>로켓단 <span>나옹</span> 챗봇</h1>
      <p>TEAM ROCKET × MEOWTH AI ASSISTANT</p>
    </div>
  </div>
  <div class="hero-tags">
    <span class="tag tag-red">🚀 로켓단 소속</span>
    <span class="tag tag-gold">🪙 금구슬 보유</span>
    <span class="tag tag-gray">비주기 두목님 충성</span>
  </div>
  <div class="hero-info-grid">
    <div class="info-chip">
      <div class="label">🎯 목표</div>
      <div class="value">피카츄 포획</div>
    </div>
    <div class="info-chip">
      <div class="label">🐾 동료</div>
      <div class="value">로사 &amp; 로이</div>
    </div>
    <div class="info-chip">
      <div class="label">⚡ 특기</div>
      <div class="value">마구할퀴기 위협</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 기존 채팅 출력
# --------------------------------------------------
for chat in st.session_state["chat_history"]:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# --------------------------------------------------
# 퀵 리플라이 버튼 (대화 없을 때만 표시)
# --------------------------------------------------
if not st.session_state["chat_history"]:
    st.markdown('<div class="rocket-divider"><span>— 빠른 시작 —</span></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    quick_map = {
        col1: ("👋 안녕, 나옹!", "안녕, 나옹!"),
        col2: ("🚀 로켓단 소개", "로켓단에 대해 알려줘"),
        col3: ("⚡ 피카츄 어디?", "피카츄는 어디 있어?"),
        col4: ("🪙 금구슬 자랑", "금구슬에 대해 얘기해줘"),
    }
    for col, (label, msg) in quick_map.items():
        with col:
            if st.button(label, key=f"quick_{label}"):
                st.session_state["quick_input"] = msg
                st.rerun()

# --------------------------------------------------
# 퀵 리플라이 처리
# --------------------------------------------------
if st.session_state["quick_input"]:
    user_text = st.session_state["quick_input"]
    st.session_state["quick_input"] = None

    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("나옹이 생각하는 중이다옹..."):
            try:
                resp = requests.post(
                    API_URL,
                    json={"message": user_text, "session_id": st.session_state["session_id"]},
                    timeout=30
                )
                resp.raise_for_status()
                answer = resp.json()["text"]
            except requests.exceptions.RequestException as e:
                answer = f"서버 요청 중 오류가 발생했다옹: {e}"
            except (KeyError, ValueError):
                answer = "서버 응답이 이상하다옹. 나중에 다시 시도하다옹."
        st.markdown(answer)

    st.session_state["chat_history"].extend([
        {"role": "user",      "content": user_text},
        {"role": "assistant", "content": answer},
    ])
    st.rerun()

# --------------------------------------------------
# 구분선
# --------------------------------------------------
st.markdown('<div class="rocket-divider"><span>— ROCKET DAN —</span></div>', unsafe_allow_html=True)

# --------------------------------------------------
# 사용자 입력
# --------------------------------------------------
user_input = st.chat_input("나옹에게 할 말을 입력하다옹...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("나옹이 생각하는 중이다옹..."):
            try:
                resp = requests.post(
                    API_URL,
                    json={"message": user_input, "session_id": st.session_state["session_id"]},
                    timeout=30
                )
                resp.raise_for_status()
                answer = resp.json()["text"]
            except requests.exceptions.RequestException as e:
                answer = f"서버 요청 중 오류가 발생했다옹: {e}"
            except (KeyError, ValueError):
                answer = "서버 응답이 이상하다옹. 나중에 다시 시도하다옹."
        st.markdown(answer)

    st.session_state["chat_history"].extend([
        {"role": "user",      "content": user_input},
        {"role": "assistant", "content": answer},
    ])

# --------------------------------------------------
# 푸터
# --------------------------------------------------
st.markdown("""
<div class="footer-note">
  <span>로켓단</span> 비주기 두목님을 위해 작동 중 · 이 몸 나옹이 직접 답변하는 챗봇이다옹
</div>
""", unsafe_allow_html=True)
