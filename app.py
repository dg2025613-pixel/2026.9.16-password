
import streamlit as st
import random
import math

# =====================================================
# 기본 설정
# =====================================================

st.set_page_config(
    page_title="암호 탈출 프로젝트",
    page_icon="🔐",
    layout="wide"
)

WORD_BANK = [
    "APPLE", "GRAPE", "BRAIN", "PLANT", "DREAM",
    "LIGHT", "MUSIC", "WATER", "HOUSE", "SMILE",
    "CLOUD", "TRAIN", "EARTH", "HEART", "STONE",
    "RIVER", "SPACE", "NIGHT", "SUGAR", "BEACH",
    "TIGER", "ZEBRA", "CHAIR", "PAPER", "PHONE",
    "MOUSE", "GREEN", "BLACK", "WHITE", "BREAD"
]

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# =====================================================
# 디자인
# =====================================================

st.markdown("""
<style>
.stApp {
    background-color: #101827;
    color: #F1F5F9;
}

section[data-testid="stSidebar"] {
    background-color: #172338;
}

h1, h2, h3, h4, p, label, span, li {
    color: #F1F5F9;
}

.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 5px;
}

.sub-title {
    color: #AFC1D8;
    font-size: 16px;
    margin-bottom: 25px;
}

.info-card {
    background-color: #1B2A41;
    border: 1px solid #334967;
    border-radius: 12px;
    padding: 20px;
    margin: 12px 0;
}

.cipher-text {
    background-color: #263B59;
    color: #FFFFFF;
    padding: 18px;
    border-radius: 10px;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: 7px;
    text-align: center;
}

.small-text {
    color: #B8C9DF;
    font-size: 14px;
}

div.stButton > button {
    background-color: #3478F6;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    min-height: 42px;
}

div.stButton > button:hover {
    background-color: #5590FF;
    color: white;
}

div[data-testid="stForm"] {
    background-color: #172338;
    border: 1px solid #334967;
    border-radius: 12px;
    padding: 18px;
}

input, textarea {
    color: #FFFFFF !important;
}

[data-testid="stMetricValue"] {
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# 암호 관련 함수
# =====================================================

def caesar_encrypt(word, shift):
    result = ""

    for char in word:
        number = ord(char) - ord("A")
        encrypted = (number + shift) % 26
        result += chr(encrypted + ord("A"))

    return result


def caesar_decrypt(word, shift):
    result = ""

    for char in word:
        number = ord(char) - ord("A")
        decrypted = (number - shift) % 26
        result += chr(decrypted + ord("A"))

    return result


def affine_encrypt(word, a, b):
    result = ""

    for char in word:
        p = ord(char) - ord("A")
        c = (a * p + b) % 26
        result += chr(c + ord("A"))

    return result


def affine_decrypt(word, a, b):
    inverse = pow(a, -1, 26)
    result = ""

    for char in word:
        c = ord(char) - ord("A")
        p = (inverse * (c - b)) % 26
        result += chr(p + ord("A"))

    return result


# =====================================================
# 힐암호 함수
# 열벡터 방식으로 계산
# =====================================================

def hill_encrypt_pair(pair, key):
    x = ord(pair[0]) - ord("A")
    y = ord(pair[1]) - ord("A")

    c1 = (key[0][0] * x + key[0][1] * y) % 26
    c2 = (key[1][0] * x + key[1][1] * y) % 26

    return chr(c1 + 65) + chr(c2 + 65)


def hill_encrypt(word, key):
    padded = word

    if len(padded) % 2 == 1:
        padded += "X"

    result = ""

    for i in range(0, len(padded), 2):
        pair = padded[i:i+2]
        result += hill_encrypt_pair(pair, key)

    return result


def hill_matrix_inverse(key):
    a, b = key[0]
    c, d = key[1]

    determinant = (a * d - b * c) % 26

    if math.gcd(determinant, 26) != 1:
        return None

    det_inverse = pow(determinant, -1, 26)

    inverse = [
        [(d * det_inverse) % 26,
         (-b * det_inverse) % 26],

        [(-c * det_inverse) % 26,
         (a * det_inverse) % 26]
    ]

    return inverse


def hill_decrypt(ciphertext, key):
    inverse = hill_matrix_inverse(key)

    if inverse is None:
        return None

    result = ""

    for i in range(0, len(ciphertext), 2):
        x = ord(ciphertext[i]) - 65
        y = ord(ciphertext[i + 1]) - 65

        p1 = (inverse[0][0] * x + inverse[0][1] * y) % 26
        p2 = (inverse[1][0] * x + inverse[1][1] * y) % 26

        result += chr(p1 + 65) + chr(p2 + 65)

    return result


def make_hill_key():
    while True:
        key = [
            [random.randint(0, 25), random.randint(0, 25)],
            [random.randint(0, 25), random.randint(0, 25)]
        ]

        determinant = (
            key[0][0] * key[1][1]
            - key[0][1] * key[1][0]
        ) % 26

        if math.gcd(determinant, 26) == 1:
            return key


# =====================================================
# 문제 생성
# =====================================================

def make_question(stage):

    word = random.choice(WORD_BANK)

    if stage == 1:
        shift = random.randint(1, 25)

        return {
            "word": word,
            "shift": shift,
            "cipher": caesar_encrypt(word, shift)
        }

    elif stage == 2:
        possible_a = [
            x for x in range(1, 26)
            if math.gcd(x, 26) == 1
        ]

        a = random.choice(possible_a)
        b = random.randint(0, 25)

        return {
            "word": word,
            "a": a,
            "b": b,
            "cipher": affine_encrypt(word, a, b)
        }

    elif stage == 3:
        key = make_hill_key()

        # 알려진 평문과 암호문 쌍
        known1 = "BA"
        known2 = "BD"

        known_cipher1 = hill_encrypt_pair(known1, key)
        known_cipher2 = hill_encrypt_pair(known2, key)

        cipher = hill_encrypt(word, key)

        return {
            "word": word,
            "key": key,
            "cipher": cipher,
            "known1": known1,
            "known2": known2,
            "known_cipher1": known_cipher1,
            "known_cipher2": known_cipher2
        }


# =====================================================
# 게임 상태 관리
# =====================================================

if "stage" not in st.session_state:
    st.session_state.stage = 1

if "questions" not in st.session_state:
    st.session_state.questions = {}

if "solved" not in st.session_state:
    st.session_state.solved = {
        1: False,
        2: False,
        3: False
    }


def reset_game():
    st.session_state.stage = 1
    st.session_state.questions = {}
    st.session_state.solved = {
        1: False,
        2: False,
        3: False
    }


def next_stage():
    current = st.session_state.stage

    if current < 3:
        st.session_state.stage += 1

        # 다음 단계에 새 문제 생성
        new_stage = st.session_state.stage
        st.session_state.questions[new_stage] = make_question(new_stage)


def get_question(stage):
    if stage not in st.session_state.questions:
        st.session_state.questions[stage] = make_question(stage)

    return st.session_state.questions[stage]


# =====================================================
# 상단 제목
# =====================================================

st.markdown(
    '<div class="main-title">🔐 암호 탈출 프로젝트</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '세 가지 암호를 해독하고 마지막 단계까지 탈출하라!'
    '</div>',
    unsafe_allow_html=True
)


# =====================================================
# 게임 / 계산기 탭
# =====================================================

game_tab, calculator_tab = st.tabs([
    "🗝️ 암호 탈출 게임",
    "🧮 아핀암호 계산기"
])


# =====================================================
# 암호 탈출 게임
# =====================================================

with game_tab:

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("### 진행 상황")

    with col2:
        if st.button("🔄 게임 다시 시작", key="restart"):
            reset_game()
            st.rerun()

    stage = st.session_state.stage

    progress = stage / 3
    st.progress(progress)

    st.caption(f"현재 {stage}단계 / 총 3단계")

    q = get_question(stage)

    st.divider()

    # -------------------------------------------------
    # 1단계: 시저암호
    # -------------------------------------------------

    if stage == 1:

        st.markdown("## 1단계. 시저암호")

        st.markdown("""
        <div class="info-card">
        <b>시저암호란?</b><br><br>
        알파벳을 정해진 칸 수만큼 뒤로 이동시켜 암호문을 만드는 방법이다.<br><br>
        <b>복호화 방법</b><br>
        암호문을 반대 방향으로 정해진 칸 수만큼 이동시키면 된다.<br><br>
        예를 들어 3칸 이동했다면 KHOOR는 HELLO가 된다.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 암호 해독")

        st.markdown(
            f'<div class="cipher-text">{q["cipher"]}</div>',
            unsafe_allow_html=True
        )

        st.write("")
        st.info(
            f"알파벳이 뒤로 이동한 칸 수: **{q['shift']}칸**"
        )

        with st.form("caesar_form"):
            answer = st.text_input(
                "해독한 단어를 입력하세요.",
                max_chars=5
            )

            submitted = st.form_submit_button("정답 확인")

        if submitted:
            if answer.strip().upper() == q["word"]:
                st.session_state.solved[1] = True
                st.success("정답입니다! 1단계를 통과했습니다.")
            else:
                st.error("정답이 아닙니다. 이동 방향과 칸 수를 다시 확인하세요.")

        if st.session_state.solved[1]:
            st.success("다음 단계로 이동할 수 있습니다.")

            if st.button("2단계로 이동 ➜"):
                next_stage()
                st.rerun()


    # -------------------------------------------------
    # 2단계: 아핀암호
    # -------------------------------------------------

    elif stage == 2:

        st.markdown("## 2단계. 아핀암호")

        st.markdown("""
        <div class="info-card">
        <b>아핀암호란?</b><br><br>
        알파벳을 숫자로 바꾼 뒤 두 개의 숫자 a, b를 이용해 암호화하는 방법이다.<br><br>
        <b>암호화 공식</b><br>
        C = (a × P + b)를 26으로 나눈 나머지<br><br>
        <b>복호화 공식</b><br>
        P = a의 역원 × (C - b)를 26으로 나눈 나머지<br><br>
        A=0, B=1, ..., Z=25로 계산한다.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 암호 해독")

        st.markdown(
            f'<div class="cipher-text">{q["cipher"]}</div>',
            unsafe_allow_html=True
        )

        st.write("")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("a 값", q["a"])

        with col2:
            st.metric("b 값", q["b"])

        st.caption(
            "a와 26은 서로소여야 하며, a의 역원을 이용해 복호화한다."
        )

        with st.form("affine_form"):
            answer = st.text_input(
                "해독한 단어를 입력하세요.",
                max_chars=5
            )

            submitted = st.form_submit_button("정답 확인")

        if submitted:
            if answer.strip().upper() == q["word"]:
                st.session_state.solved[2] = True
                st.success("정답입니다! 2단계를 통과했습니다.")
            else:
                st.error("정답이 아닙니다. 복호화 공식과 역원을 확인하세요.")

        if st.session_state.solved[2]:
            st.success("다음 단계로 이동할 수 있습니다.")

            if st.button("3단계로 이동 ➜"):
                next_stage()
                st.rerun()


    # -------------------------------------------------
    # 3단계: 힐암호
    # -------------------------------------------------

    elif stage == 3:

        st.markdown("## 3단계. 힐암호")

        st.markdown("""
        <div class="info-card">
        <b>힐암호란?</b><br><br>
        알파벳을 숫자로 바꾸고, 2×2 행렬을 이용해 두 글자씩 암호화하는 방법이다.<br><br>
        이번 단계에서는 암호화에 사용된 행렬이 공개되지 않는다.<br>
        주어진 평문과 암호문 쌍을 이용해 행렬을 직접 찾아야 한다.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### ① 행렬 추론에 필요한 정보")

        st.write(
            "다음 두 평문이 각각 어떤 암호문으로 바뀌었는지 확인하자."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**첫 번째 평문·암호문 쌍**")
            st.markdown(
                f'<div class="cipher-text">'
                f'{q["known1"]} → {q["known_cipher1"]}'
                f'</div>',
                unsafe_allow_html=True
            )

        with col2:
            st.markdown("**두 번째 평문·암호문 쌍**")
            st.markdown(
                f'<div class="cipher-text">'
                f'{q["known2"]} → {q["known_cipher2"]}'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("### ② 암호문 해독")

        st.markdown(
            f'<div class="cipher-text">{q["cipher"]}</div>',
            unsafe_allow_html=True
        )

        st.write("")

        st.markdown("### ③ 직접 추론한 행렬 입력")

        st.caption(
            "A=0, B=1, ..., Z=25로 바꾼 뒤 행렬의 네 값을 구해 입력하자."
        )

        with st.form("hill_form"):

            st.write("추론한 2×2 행렬")

            row1 = st.columns(2)
            with row1[0]:
                m00 = st.number_input(
                    "첫째 행 첫째 값",
                    min_value=0,
                    max_value=25,
                    value=0,
                    step=1,
                    key="hill_m00"
                )

            with row1[1]:
                m01 = st.number_input(
                    "첫째 행 둘째 값",
                    min_value=0,
                    max_value=25,
                    value=0,
                    step=1,
                    key="hill_m01"
                )

            row2 = st.columns(2)
            with row2[0]:
                m10 = st.number_input(
                    "둘째 행 첫째 값",
                    min_value=0,
                    max_value=25,
                    value=0,
                    step=1,
                    key="hill_m10"
                )

            with row2[1]:
                m11 = st.number_input(
                    "둘째 행 둘째 값",
                    min_value=0,
                    max_value=25,
                    value=0,
                    step=1,
                    key="hill_m11"
                )

            answer = st.text_input(
                "행렬로 복호화한 단어를 입력하세요.",
                max_chars=5
            )

            submitted = st.form_submit_button("행렬과 정답 확인")

        if submitted:

            user_key = [
                [int(m00), int(m01)],
                [int(m10), int(m11)]
            ]

            correct_key = q["key"]

            matrix_correct = (
                user_key == correct_key
            )

            answer_correct = (
                answer.strip().upper() == q["word"]
            )

            if matrix_correct and answer_correct:
                st.session_state.solved[3] = True
                st.success("정답입니다! 모든 암호를 해독했습니다.")

            elif not matrix_correct:
                st.error(
                    "행렬이 정확하지 않습니다. "
                    "주어진 두 평문·암호문 쌍을 다시 확인하세요."
                )

            else:
                st.error(
                    "행렬은 맞았습니다! "
                    "복호화 과정과 마지막 단어를 다시 확인하세요."
                )

        if st.session_state.solved[3]:

            st.balloons()

            st.markdown("""
            <div class="info-card">
            <h2>🎉 탈출 성공!</h2>
            모든 암호를 해독하고 마지막 단계까지 통과했습니다.
            </div>
            """, unsafe_allow_html=True)

            if st.button("새로운 암호 문제 시작"):
                reset_game()
                st.rerun()


# =====================================================
# 아핀암호 계산기
# =====================================================

with calculator_tab:

    st.markdown("## 🧮 아핀암호 계산기")

    st.markdown("""
    <div class="info-card">
    암호문 또는 평문을 입력하고 a, b 값을 설정하면
    아핀암호를 암호화하거나 복호화할 수 있다.
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio(
        "계산 방식",
        ["복호화", "암호화"],
        horizontal=True,
        key="affine_calculator_mode"
    )

    text = st.text_input(
        "문자열 입력",
        placeholder="예: MXZHL",
        key="affine_calculator_text"
    )

    col1, col2 = st.columns(2)

    with col1:
        calc_a = st.number_input(
            "a 값",
            min_value=0,
            max_value=25,
            value=9,
            step=1,
            key="calculator_a"
        )

    with col2:
        calc_b = st.number_input(
            "b 값",
            min_value=0,
            max_value=25,
            value=1,
            step=1,
            key="calculator_b"
        )

    if st.button("계산하기", key="affine_calculate"):

        clean_text = text.strip().upper()

        if not clean_text:
            st.warning("문자열을 입력해 주세요.")

        elif not clean_text.isalpha() or not clean_text.isascii():
            st.error("영어 알파벳만 입력할 수 있습니다.")

        elif math.gcd(int(calc_a), 26) != 1:
            st.error(
                "a와 26은 서로소여야 합니다. "
                "예: 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25"
            )

        else:

            if mode == "복호화":
                result = affine_decrypt(
                    clean_text,
                    int(calc_a),
                    int(calc_b)
                )

                st.success(f"복호화 결과: {result}")

                inverse = pow(int(calc_a), -1, 26)

                st.info(
                    f"a의 역원은 {inverse}입니다."
                )

            else:
                result = affine_encrypt(
                    clean_text,
                    int(calc_a),
                    int(calc_b)
                )

                st.success(f"암호화 결과: {result}")


# =====================================================
# 하단 안내
# =====================================================

st.divider()

st.caption(
    "암호 탈출 프로젝트 | Caesar Cipher · Affine Cipher · Hill Cipher"
)
