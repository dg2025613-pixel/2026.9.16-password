# ================================================
# 🔐 암호 방탈출 게임 (Streamlit 버전)
# 시저 암호 → 아핀 암호 → 힐 암호 순서로 탈출!
# ================================================

import streamlit as st
import numpy as np
import time

from utils import (
    caesar_encrypt, caesar_decrypt,
    affine_encrypt, affine_decrypt, VALID_A_VALUES,
    hill_encrypt, hill_decrypt, det_mod26, mod_inverse
)

# ================================================
# 페이지 기본 설정
# ================================================

st.set_page_config(
    page_title="암호 방탈출 게임",
    page_icon="🔐",
    layout="centered"
)

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


# ================================================
# 사이드바 (게임 정보 표시)
# ================================================

with st.sidebar:
    st.title("🎮 게임 정보")
    st.metric("현재 점수", f"{st.session_state.score}점")
    st.metric("현재 단계", f"{st.session_state.stage} / 3")

    elapsed = time.time() - st.session_state.start_time
    st.metric("경과 시간", f"{int(elapsed)}초")

    st.divider()

    st.subheader("📖 게임 방법")
    st.markdown("""
    1️⃣ 시저 암호 해독  
    2️⃣ 아핀 암호 해독  
    3️⃣ 힐 암호 해독  

    각 단계의 암호문을 보고  
    원래 평문을 맞춰보세요!
    """)

    st.divider()

    if st.button("🔄 게임 초기화"):
        reset_game()
        st.rerun()


# ================================================
# 메인 화면 - 제목
# ================================================

st.title("🔐 수학 실험실 탈출 게임")
st.markdown("### 암호를 풀어서 실험실을 탈출하세요!")
st.divider()


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
    st.header("🚪 1단계: 시저 암호의 문")
    st.markdown(f"**이동 값(shift):** `{STAGE1_SHIFT}`")
    st.code(STAGE1_CIPHER, language=None)

    st.markdown("💡 각 알파벳을 이동 값만큼 **앞으로** 밀어서 원래 글자를 찾아보세요!")

    col1, col2 = st.columns([3, 1])
    with col1:
        answer = st.text_input("정답 입력 (영어 대문자)", key="stage1_input").upper().strip()
    with col2:
        st.write("")
        st.write("")
        submit = st.button("제출", key="stage1_submit")

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
    st.header("🚪 2단계: 아핀 암호의 문")

    st.markdown("**암호화 공식:** `C = (a × M + b) mod 26`")
    st.markdown(f"**a = {STAGE2_A}, b = {STAGE2_B}**")
    st.code(STAGE2_CIPHER, language=None)

    st.info("""
    💡 **계산 도우미 사용법**
    1. 역원(a⁻¹)을 구해야 해요
    2. 복호화 공식: M = a⁻¹ × (C - b) mod 26
    3. 아래 계산기를 사용해보세요!
    """)

    # 계산 도우미 (아핀 복호화 계산기)
    with st.expander("🧮 아핀 복호화 계산기 (도구)"):
        st.markdown("암호 글자를 숫자로 바꿔서(A=0, B=1, ... Z=25) 입력하세요")
        c_num = st.number_input("암호 숫자 입력 (0~25)", min_value=0, max_value=25, step=1, key="affine_calc_num")
        if st.button("계산하기", key="affine_calc_btn"):
            a_inv = mod_inverse(STAGE2_A, 26)
            m_num = (a_inv * (c_num - STAGE2_B)) % 26
            result_letter = chr(int(m_num) + ord('A'))
            st.success(f"숫자 {c_num} → 원래 글자: '{result_letter}'")
    col1, col2 = st.columns([3, 1])
    with col1:
        answer = st.text_input("정답 입력 (영어 대문자)", key="stage2_input").upper().strip()
    with col2:
        st.write("")
        st.write("")
        submit = st.button("제출", key="stage2_submit")

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
    st.header("🚪 3단계: 힐 암호의 문 (최종 관문)")

    st.markdown("**키 행렬:**")
    st.latex(r"""
    K = \begin{pmatrix} 3 & 3 \\ 2 & 5 \end{pmatrix}
    """)
    st.code(STAGE3_CIPHER, language=None)

    st.info("""
    💡 **힐 암호는 어려우니 도구를 사용하세요!**
    아래 계산기에 암호문 2글자씩 넣으면 
    자동으로 원래 글자를 계산해줘요!
    """)

    # 계산 도우미 (힐 복호화 계산기)
    with st.expander("🧮 힐 복호화 계산기 (도구) - 꼭 사용하세요!"):
    st.markdown("암호문 2글자를 각각 숫자로 바꿔서(A=0, B=1, ... Z=25) 입력하세요")

    col_a, col_b = st.columns(2)
    with col_a:
        c1 = st.number_input("숫자 1 (0~25)", min_value=0, max_value=25, step=1, key="hill_calc_n1")
    with col_b:
        c2 = st.number_input("숫자 2 (0~25)", min_value=0, max_value=25, step=1, key="hill_calc_n2")

    if st.button("계산하기", key="hill_calc_btn"):
        from utils import matrix_mod_inverse
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
        submit = st.button("제출", key="stage3_submit")

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
    st.title("🎉 축하합니다! 탈출 성공! 🎉")

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

    if st.button("🔄 다시 도전하기"):
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
