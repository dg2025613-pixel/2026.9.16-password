# ================================================
# 🔐 암호 방탈출 게임 (Streamlit 버전) - VAULT 테마
# 시저 암호 → 아핀 암호 → 힐 암호 순서로 탈출!
# ================================================

import streamlit as st
import numpy as np
import time

from utils import (
    caesar_encrypt, caesar_decrypt,
    affine_encrypt, affine_decrypt, VALID_A_VALUES,
    hill_encrypt, hill_decrypt, det_mod26, mod_inverse,
    matrix_mod_inverse
)

# ================================================
# 페이지 기본 설정
# ================================================

st.set_page_config(
    page_title="CIPHER VAULT · 암호 방탈출",
    page_icon="🔐",
    layout="centered"
)

# ================================================
# 커스텀 디자인 (VAULT / 해킹 터미널 컨셉)
# ================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
}

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 0.02em;
}

/* 배경: 은은한 네온 그라디언트 + 격자 무늬 */
.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(0, 245, 212, 0.07), transparent 42%),
        radial-gradient(circle at 85% 0%, rgba(124, 58, 237, 0.10), transparent 45%),
        #0B0F1A;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0, 245, 212, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 245, 212, 0.035) 1px, transparent 1px);
    background-size: 42px 42px;
    pointer-events: none;
    z-index: 0;
}
.main .block-container {
    position: relative;
    z-index: 1;
}

/* 메인 타이틀 */
.vault-title {
    font-family: 'Orbitron', sans-serif;
    font-weight: 800;
    font-size: 2.15rem;
    line-height: 1.25;
    background: linear-gradient(90deg, #00F5D4, #7C3AED);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.15rem;
}
.vault-subtitle {
    color: #8FA3BF;
    font-size: 0.98rem;
    margin-bottom: 0.4rem;
}

/* 단계 진행 dots */
.stage-dots {
    display: flex;
    gap: 0.55rem;
    margin: 0.9rem 0 1.3rem 0;
}
.stage-dot {
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.05rem;
    border: 2px solid rgba(255,255,255,0.14);
    color: rgba(255,255,255,0.35);
    background: rgba(255,255,255,0.02);
}
.stage-dot.done {
    border-color: #00F5D4;
    color: #00F5D4;
    box-shadow: 0 0 12px rgba(0,245,212,0.45);
}
.stage-dot.active {
    border-color: #7C3AED;
    color: #fff;
    background: rgba(124,58,237,0.22);
    box-shadow: 0 0 14px rgba(124,58,237,0.55);
}

/* 암호문 터미널 박스 */
.cipher-box {
    background: #05070D;
    border: 1px solid rgba(0, 245, 212, 0.4);
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin: 0.7rem 0 1.2rem 0;
    box-shadow: 0 0 20px rgba(0, 245, 212, 0.13), inset 0 0 24px rgba(0, 245, 212, 0.04);
}
.cipher-box .cb-label {
    color: #6E86A6;
    font-size: 0.75rem;
    letter-spacing: 0.14em;
    margin-bottom: 0.45rem;
}
.cipher-box .cb-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.65rem;
    font-weight: 600;
    letter-spacing: 0.32em;
    color: #00F5D4;
    text-shadow: 0 0 12px rgba(0, 245, 212, 0.55);
    word-break: break-all;
}

/* 버튼 */
div[data-testid="stButton"] button {
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    border: 1px solid rgba(0, 245, 212, 0.5);
    transition: all 0.15s ease;
}
div[data-testid="stButton"] button:hover {
    box-shadow: 0 0 14px rgba(0, 245, 212, 0.45);
    transform: translateY(-1px);
}

/* 진행률 바 그라디언트 */
div[data-testid="stProgress"] div[role="progressbar"] > div {
    background-image: linear-gradient(90deg, #00F5D4, #7C3AED) !important;
}

/* expander (계산기 / 힌트) */
div[data-testid="stExpander"] {
    border: 1px solid rgba(124, 58, 237, 0.4);
    border-radius: 10px;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(0, 245, 212, 0.15);
}

/* 코드 블록 (힐 암호 행렬 등) */
code {
    color: #00F5D4 !important;
}
</style>
""", unsafe_allow_html=True)


# ================================================
# 게임 데이터 설정 (문제, 정답, 힌트)
# ================================================

# 1단계: 시저 암호
STAGE1_ANSWER = "LIBRARY"
STAGE1_SHIFT = 3
STAGE1_CIPHER = caesar_encrypt(STAGE1_ANSWER, STAGE1_SHIFT)

# 2단계: 아핀 암호
STAGE2_ANSWER = "TREASURE"
STAGE2_A = 5
STAGE2_B = 8
STAGE2_CIPHER = affine_encrypt(STAGE2_ANSWER, STAGE2_A, STAGE2_B)

# 3단계: 힐 암호
STAGE3_ANSWER = "ESCAPE"
STAGE3_KEY = np.array([[3, 3], [2, 5]])
STAGE3_CIPHER = hill_encrypt(STAGE3_ANSWER, STAGE3_KEY)


# ================================================
# 세션 상태 초기화 (게임 진행 상황 저장)
# ================================================

def init_session_state():
    """게임 상태 초기화"""
    if "stage" not in st.session_state:
        st.session_state.stage = 1          # 현재 단계
    if "score" not in st.session_state:
        st.session_state.score = 100        # 점수
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()  # 시작 시간
    if "hint_count" not in st.session_state:
        st.session_state.hint_count = {1: 0, 2: 0, 3: 0}  # 단계별 힌트 사용 수
    if "cleared" not in st.session_state:
        st.session_state.cleared = False    # 최종 클리어 여부
    if "wrong_count" not in st.session_state:
        st.session_state.wrong_count = {1: 0, 2: 0, 3: 0}  # 단계별 오답 횟수


init_session_state()


# ================================================
# 공통 함수
# ================================================

def use_hint(stage):
    """힌트 사용 처리"""
    st.session_state.hint_count[stage] += 1
    st.session_state.score = max(0, st.session_state.score - 10)


def wrong_answer(stage):
    """오답 처리"""
    st.session_state.wrong_count[stage] += 1
    st.session_state.score = max(0, st.session_state.score - 15)


def next_stage():
    """다음 단계로 이동"""
    st.session_state.stage += 1


def calculate_final_score():
    """최종 점수 계산 (시간 보너스 포함)"""
    elapsed = time.time() - st.session_state.start_time

    if elapsed < 180:
        time_bonus = 50
    elif elapsed < 300:
        time_bonus = 30
    elif elapsed < 480:
        time_bonus = 10
    else:
        time_bonus = 0

    final_score = st.session_state.score + time_bonus
    return final_score, elapsed, time_bonus


def get_grade(score):
    """점수에 따른 등급 반환"""
    if score >= 130:
        return "🥇 S등급 - 천재 탐정!"
    elif score >= 100:
        return "🥈 A등급 - 암호 전문가!"
    elif score >= 70:
        return "🥉 B등급 - 암호 분석가!"
    elif score >= 40:
        return "📝 C등급 - 암호 입문자!"
    else:
        return "📚 D등급 - 더 연습해봐요!"


def reset_game():
    """게임 초기화"""
    st.session_state.stage = 1
    st.session_state.score = 100
    st.session_state.start_time = time.time()
    st.session_state.hint_count = {1: 0, 2: 0, 3: 0}
    st.session_state.cleared = False
    st.session_state.wrong_count = {1: 0, 2: 0, 3: 0}


def render_cipher(label, text):
    """암호문을 터미널 스타일 박스로 표시"""
    st.markdown(f"""
    <div class="cipher-box">
        <div class="cb-label">{label}</div>
        <div class="cb-text">{text}</div>
    </div>
    """, unsafe_allow_html=True)


def render_stage_dots():
    """상단 단계 진행 표시 (🔒/🔓 아이콘 dots)"""
    if st.session_state.cleared:
        icons = ["✅", "✅", "✅"]
        classes = ["done", "done", "done"]
    else:
        icons, classes = [], []
        for s in [1, 2, 3]:
            if s < st.session_state.stage:
                icons.append("✅")
                classes.append("done")
            elif s == st.session_state.stage:
                icons.append("🔓")
                classes.append("active")
            else:
                icons.append("🔒")
                classes.append("")

    dots_html = '<div class="stage-dots">'
    for icon, cls in zip(icons, classes):
        dots_html += f'<div class="stage-dot {cls}">{icon}</div>'
    dots_html += '</div>'
    st.markdown(dots_html, unsafe_allow_html=True)


# ================================================
# 사이드바 (게임 정보 표시)
# ================================================

with st.sidebar:
    st.markdown("### 🕹️ 게임 정보")
    st.metric("현재 점수", f"{st.session_state.score}점")
    st.metric("현재 단계", f"{st.session_state.stage} / 3")

    elapsed = time.time() - st.session_state.start_time
    st.metric("경과 시간", f"{int(elapsed)}초")

    st.divider()

    st.markdown("#### 📖 게임 방법")
    st.markdown("""
    1️⃣ 시저 암호 해독  
    2️⃣ 아핀 암호 해독  
    3️⃣ 힐 암호 해독  

    각 단계의 암호문을 보고  
    원래 평문을 맞춰보세요!
    """)

    st.divider()

    if st.button("🔄 게임 초기화", use_container_width=True):
        reset_game()
        st.rerun()


# ================================================
# 메인 화면 - 제목
# ================================================

st.markdown('<div class="vault-title">🔐 CIPHER VAULT</div>', unsafe_allow_html=True)
st.markdown('<div class="vault-subtitle">암호를 풀어서 수학 실험실을 탈출하세요</div>', unsafe_allow_html=True)

render_stage_dots()


# ================================================
# 스토리 인트로
# ================================================

if st.session_state.stage == 1 and st.session_state.wrong_count[1] == 0:
    st.info("""
    📜 **스토리**
    
    당신은 수학 실험실에 갇혔습니다.  
    탈출하려면 3개의 암호화된 문을 통과해야 합니다.  
    
    첫 번째 문에는 오래된 **시저 암호**가 적혀있습니다...
    """)


# ================================================
# 1단계: 시저 암호
# ================================================

def stage1():
    st.header("🚪 1단계 · 시저 암호의 문")
    st.markdown(f"**이동 값(shift):** `{STAGE1_SHIFT}`")
    render_cipher("ENCRYPTED MESSAGE", STAGE1_CIPHER)

    st.markdown("💡 각 알파벳을 이동 값만큼 **앞으로** 밀어서 원래 글자를 찾아보세요!")

    col1, col2 = st.columns([3, 1])
    with col1:
        answer = st.text_input("정답 입력 (영어 대문자)", key="stage1_input").upper().strip()
    with col2:
        st.write("")
        st.write("")
        submit = st.button("제출", key="stage1_submit", use_container_width=True)

    # 힌트 영역
    with st.expander("💡 힌트 보기 (점수 -10점)"):
        if st.button("힌트 확인하기", key="stage1_hint_btn"):
            use_hint(1)
        if st.session_state.hint_count[1] > 0:
            st.success(f"힌트: 정답은 {len(STAGE1_ANSWER)}글자이며, 책 읽는 장소와 관련이 있어요!")

    if submit:
        if answer == STAGE1_ANSWER:
            st.success("🎉 정답입니다! 첫 번째 문이 열렸어요!")
            st.balloons()
            time.sleep(1)
            next_stage()
            st.rerun()
        elif answer == "":
            st.warning("답을 입력해주세요!")
        else:
            wrong_answer(1)
            st.error(f"❌ 틀렸어요! (-15점) 다시 시도해보세요")


# ================================================
# 2단계: 아핀 암호
# ================================================

def stage2():
    st.header("🚪 2단계 · 아핀 암호의 문")

    st.markdown("**암호화 공식:** `C = (a × M + b) mod 26`")
    st.markdown(f"**a = {STAGE2_A}, b = {STAGE2_B}**")
    render_cipher("ENCRYPTED MESSAGE", STAGE2_CIPHER)

    st.info("""
    💡 **계산 도우미 사용법**
    1. 역원(a⁻¹)을 구해야 해요
    2. 복호화 공식: M = a⁻¹ × (C - b) mod 26
    3. 알파벳을 숫자로 바꿔서(A=0, B=1, ... Z=25) 아래 계산기에 넣어보세요!
    """)

    # 계산 도우미 (아핀 복호화 검산기)
    with st.expander("🧮 아핀 복호화 계산기 (직접 계산 후 확인해보세요)"):
        st.markdown(f"**1단계: a의 역원(a⁻¹) 구하기**  (a × a⁻¹ ≡ 1 (mod 26), a = {STAGE2_A})")
        user_a_inv = st.number_input(
            "직접 계산한 a⁻¹ 값을 입력하세요 (0~25)",
            min_value=0, max_value=25, step=1,
            key="affine_user_ainv"
        )
        if st.button("역원 확인하기", key="affine_check_ainv_btn"):
            correct_a_inv = mod_inverse(STAGE2_A, 26)
            if user_a_inv == correct_a_inv:
                st.success(f"정답이에요! a⁻¹ = {user_a_inv}")
            else:
                st.error("아직 틀렸어요. (a × a⁻¹) mod 26 = 1이 되는 값을 다시 찾아보세요.")

        st.markdown("---")
        st.markdown("**2단계: 복호화 공식 계산하기**  M = a⁻¹ × (C − b) mod 26")
        col_c, col_b = st.columns(2)
        with col_c:
            c_num = st.number_input(
                "암호 글자를 숫자로 바꿔서 입력 (A=0, B=1, ... Z=25)",
                min_value=0, max_value=25, step=1,
                key="affine_calc_c"
            )
        with col_b:
            b_num = st.number_input(
                "b 값 입력",
                min_value=0, max_value=25, step=1,
                key="affine_calc_b"
            )
        if st.button("계산하기", key="affine_calc_btn"):
            m_num = (int(user_a_inv) * (c_num - b_num)) % 26
            result_letter = chr(int(m_num) + ord('A'))
            st.success(f"→ 원래 글자: '{result_letter}'")

    col1, col2 = st.columns([3, 1])
    with col1:
        answer = st.text_input("정답 입력 (영어 대문자)", key="stage2_input").upper().strip()
    with col2:
        st.write("")
        st.write("")
        submit = st.button("제출", key="stage2_submit", use_container_width=True)

    with st.expander("💡 힌트 보기 (점수 -10점)"):
        if st.button("힌트 확인하기", key="stage2_hint_btn"):
            use_hint(2)
        if st.session_state.hint_count[2] > 0:
            st.success(f"힌트: 정답은 {len(STAGE2_ANSWER)}글자이며, 보물과 관련된 단어예요!")

    if submit:
        if answer == STAGE2_ANSWER:
            st.success("🎉 정답입니다! 두 번째 문이 열렸어요!")
            st.balloons()
            time.sleep(1)
            next_stage()
            st.rerun()
        elif answer == "":
            st.warning("답을 입력해주세요!")
        else:
            wrong_answer(2)
            st.error(f"❌ 틀렸어요! (-15점) 다시 시도해보세요")


# ================================================
# 3단계: 힐 암호
# ================================================

def stage3():
    st.header("🚪 3단계 · 힐 암호의 문 (최종 관문)")

    st.markdown("**키 행렬:**")
    st.latex(r"""
    K = \begin{pmatrix} 3 & 3 \\ 2 & 5 \end{pmatrix}
    """)
    render_cipher("ENCRYPTED MESSAGE", STAGE3_CIPHER)

    st.info("""
    💡 **힐 암호는 어려우니 도구를 사용하세요!**
    암호문 글자를 숫자로 바꿔서(A=0, B=1, ... Z=25)  
    2개씩 짝지어 아래 계산기에 넣으면  
    자동으로 원래 글자를 계산해줘요!
    """)

    # 계산 도우미 (힐 복호화 계산기) - 숫자 직접 입력 방식
    with st.expander("🧮 힐 복호화 계산기 (도구) - 꼭 사용하세요!"):
        st.markdown("암호문 2글자를 각각 숫자로 바꿔서(A=0, B=1, ... Z=25) 입력하세요")

        col_a, col_b = st.columns(2)
        with col_a:
            c1 = st.number_input("숫자 1 (0~25)", min_value=0, max_value=25, step=1, key="hill_calc_n1")
        with col_b:
            c2 = st.number_input("숫자 2 (0~25)", min_value=0, max_value=25, step=1, key="hill_calc_n2")

        if st.button("계산하기", key="hill_calc_btn"):
            inv_matrix = matrix_mod_inverse(STAGE3_KEY)
            pair = np.array([[c1], [c2]])
            result = np.dot(inv_matrix, pair) % 26
            r1 = chr(int(result[0][0]) + ord('A'))
            r2 = chr(int(result[1][0]) + ord('A'))
            st.success(f"({c1}, {c2}) → 원래 글자: '{r1}{r2}'")

    col1, col2 = st.columns([3, 1])
    with col1:
        answer = st.text_input("정답 입력 (영어 대문자)", key="stage3_input").upper().strip()
    with col2:
        st.write("")
        st.write("")
        submit = st.button("제출", key="stage3_submit", use_container_width=True)

    with st.expander("💡 힌트 보기 (점수 -10점)"):
        if st.button("힌트 확인하기", key="stage3_hint_btn"):
            use_hint(3)
        if st.session_state.hint_count[3] > 0:
            st.success(f"힌트: 정답은 {len(STAGE3_ANSWER)}글자이며, 이 게임의 목표와 같은 단어예요!")

    if submit:
        # 패딩 X 제거하고 비교
        clean_answer = answer.rstrip('X')
        if answer == STAGE3_ANSWER or clean_answer == STAGE3_ANSWER:
            st.success("🎉 정답입니다! 최종 문이 열렸어요!")
            st.balloons()
            time.sleep(1)
            st.session_state.cleared = True
            st.rerun()
        elif answer == "":
            st.warning("답을 입력해주세요!")
        else:
            wrong_answer(3)
            st.error(f"❌ 틀렸어요! (-15점) 다시 시도해보세요")


# ================================================
# 최종 클리어 화면
# ================================================

def show_clear_screen():
    st.balloons()
    st.markdown('<div class="vault-title">🎉 VAULT UNLOCKED</div>', unsafe_allow_html=True)
    st.markdown('<div class="vault-subtitle">축하합니다! 탈출에 성공했습니다.</div>', unsafe_allow_html=True)

    final_score, elapsed, time_bonus = calculate_final_score()

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏱️ 걸린 시간", f"{int(elapsed)}초")
    with col2:
        st.metric("💯 기본 점수", f"{st.session_state.score}점")
    with col3:
        st.metric("⚡ 시간 보너스", f"+{time_bonus}점")

    st.markdown("---")

    st.header(f"🏆 최종 점수: {final_score}점")
    st.subheader(get_grade(final_score))

    st.markdown("---")

    # 단계별 통계
    st.subheader("📊 단계별 기록")
    for stage in [1, 2, 3]:
        st.write(f"**{stage}단계** - 오답: {st.session_state.wrong_count[stage]}회, "
                 f"힌트 사용: {st.session_state.hint_count[stage]}회")

    st.markdown("---")

    if st.button("🔄 다시 도전하기", use_container_width=True):
        reset_game()
        st.rerun()


# ================================================
# 진행 상태 표시 (프로그레스 바)
# ================================================

if not st.session_state.cleared:
    progress = (st.session_state.stage - 1) / 3
    st.progress(progress, text=f"진행률: {st.session_state.stage - 1}/3 단계 완료")


# ================================================
# 메인 로직 - 단계별 화면 전환
# ================================================

if st.session_state.cleared:
    show_clear_screen()
elif st.session_state.stage == 1:
    stage1()
elif st.session_state.stage == 2:
    stage2()
elif st.session_state.stage == 3:
    stage3()
