
import streamlit as st
import random
import time
import string
import math

# ==========================================
# 기본 설정
# ==========================================

st.set_page_config(
    page_title="암호 프로젝트 | 방탈출",
    page_icon="🔐",
    layout="centered"
)

# ==========================================
# 어두운 테마 디자인
# ==========================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0B1020, #111B32, #15152B);
    color: #F3F6FF;
}

[data-testid="stHeader"] {
    background: rgba(11, 16, 32, 0.92);
}

[data-testid="stSidebar"] {
    background: #10182B;
}

h1, h2, h3, h4, p, li, label,
.stMarkdown, .stText,
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    color: #F3F6FF !important;
}

h1, h2, h3 {
    font-weight: 850 !important;
}

.stCaption {
    color: #C0CBE0 !important;
}

.stButton > button {
    background: #6D5DFB;
    color: white !important;
    border: 1px solid #887BFF;
    border-radius: 10px;
    font-weight: 800;
    min-height: 42px;
}

.stButton > button:hover {
    background: #5142D8;
    color: white !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #F8FAFF !important;
    color: #111827 !important;
    border: 2px solid #7185A8 !important;
    border-radius: 9px !important;
}

.challenge {
    background: #17233B;
    border: 1px solid #344766;
    border-left: 6px solid #8B7CFF;
    border-radius: 12px;
    padding: 18px;
    margin: 12px 0;
    color: #F3F6FF;
}

.ciphertext {
    font-size: 2.1rem;
    font-weight: 900;
    letter-spacing: 0.16em;
    color: #9DE7FF;
    text-align: center;
    padding: 12px 0;
}

.info-card {
    background: #10182B;
    border: 1px solid #344766;
    border-radius: 10px;
    padding: 12px;
    margin: 8px 0;
}

div[data-testid="stExpander"] {
    background: #17233B;
    border: 1px solid #344766;
    border-radius: 12px;
}

div[data-testid="stForm"] {
    background: #17233B;
    border: 1px solid #344766;
    padding: 14px;
    border-radius: 12px;
}

hr {
    border-color: #344766;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 정답 단어 목록
# ==========================================

ALPHABET = string.ascii_uppercase

WORD_BANK = [
    "APPLE", "GRAPE", "BRAIN", "PLANT", "DREAM",
    "LIGHT", "MUSIC", "WATER", "HOUSE", "SMILE",
    "CLOUD", "TRAIN", "EARTH", "HEART", "STONE",
    "RIVER", "SPACE", "NIGHT", "SUGAR", "BEACH",
    "TIGER", "ZEBRA", "CHAIR", "PAPER", "PHONE",
    "MOUSE", "GREEN", "BLACK", "WHITE", "BREAD"
]


# ==========================================
# 공통 암호 함수
# ==========================================

def mod_inverse(a, m=26):
    a %= m

    for x in range(1, m):
        if (a * x) % m == 1:
            return x

    return None


# ==========================================
# 1. 시저 암호
# ==========================================

def caesar_encrypt(text, shift):
    result = ""

    for ch in text:
        value = ord(ch) - 65
        encrypted = (value + shift) % 26
        result += ALPHABET[encrypted]

    return result


def caesar_decrypt(text, shift):
    result = ""

    for ch in text:
        value = ord(ch) - 65
        decrypted = (value - shift) % 26
        result += ALPHABET[decrypted]

    return result


# ==========================================
# 2. 아핀 암호
# ==========================================

def affine_encrypt(text, a, b):
    result = ""

    for ch in text:
        value = ord(ch) - 65
        encrypted = (a * value + b) % 26
        result += ALPHABET[encrypted]

    return result


def affine_decrypt(text, a, b):
    inverse = mod_inverse(a, 26)

    if inverse is None:
        raise ValueError("a의 역원이 존재하지 않습니다.")

    result = ""

    for ch in text:
        value = ord(ch) - 65
        decrypted = (inverse * (value - b)) % 26
        result += ALPHABET[decrypted]

    return result


# ==========================================
# 3. 힐 암호
# ==========================================

def matrix_det(matrix):
    return (
        matrix[0][0] * matrix[1][1]
        - matrix[0][1] * matrix[1][0]
    ) % 26


def matrix_mod_inverse(matrix):
    a, b = matrix[0]
    c, d = matrix[1]

    det = (a * d - b * c) % 26
    det_inverse = mod_inverse(det, 26)

    if det_inverse is None:
        return None

    return [
        [
            (det_inverse * d) % 26,
            (det_inverse * (-b)) % 26
        ],
        [
            (det_inverse * (-c)) % 26,
            (det_inverse * a) % 26
        ]
    ]


def hill_encrypt(text, matrix):
    # 홀수 글자라면 마지막에 X 추가
    if len(text) % 2 == 1:
        text += "X"

    result = ""

    for i in range(0, len(text), 2):

        x = ord(text[i]) - 65
        y = ord(text[i + 1]) - 65

        c1 = (
            matrix[0][0] * x
            + matrix[0][1] * y
        ) % 26

        c2 = (
            matrix[1][0] * x
            + matrix[1][1] * y
        ) % 26

        result += ALPHABET[c1]
        result += ALPHABET[c2]

    return result


def hill_decrypt(text, matrix):
    inverse = matrix_mod_inverse(matrix)

    if inverse is None:
        raise ValueError("역행렬이 존재하지 않습니다.")

    result = ""

    for i in range(0, len(text), 2):

        x = ord(text[i]) - 65
        y = ord(text[i + 1]) - 65

        p1 = (
            inverse[0][0] * x
            + inverse[0][1] * y
        ) % 26

        p2 = (
            inverse[1][0] * x
            + inverse[1][1] * y
        ) % 26

        result += ALPHABET[p1]
        result += ALPHABET[p2]

    return result


# ==========================================
# 힐 암호 키 행렬 생성
# ==========================================

def new_hill_key():

    while True:

        matrix = [
            [random.randint(0, 25), random.randint(0, 25)],
            [random.randint(0, 25), random.randint(0, 25)]
        ]

        det = matrix_det(matrix)

        if (
            math.gcd(det, 26) == 1
            and matrix_mod_inverse(matrix) is not None
        ):
            return matrix


# ==========================================
# 단계별 문제 생성
# ==========================================

def make_question(stage):

    word = random.choice(WORD_BANK)

    # 시저 암호 문제
    if stage == 1:

        shift = random.randint(1, 25)

        return {
            "word": word,
            "shift": shift,
            "cipher": caesar_encrypt(word, shift)
        }

    # 아핀 암호 문제
    elif stage == 2:

        valid_a = [
            a for a in range(1, 26)
            if math.gcd(a, 26) == 1
        ]

        a = random.choice(valid_a)
        b = random.randint(0, 25)

        return {
            "word": word,
            "a": a,
            "b": b,
            "cipher": affine_encrypt(word, a, b)
        }

    # 힐 암호 행렬 추론 문제
    else:

        key = new_hill_key()

        known1 = "BA"
        known2 = "BD"

        return {
            "word": word,
            "key": key,
            "known1": known1,
            "known2": known2,
            "known_cipher1": hill_encrypt(known1, key),
            "known_cipher2": hill_encrypt(known2, key),
            "cipher": hill_encrypt(word, key)
        }


# ==========================================
# 게임 초기화
# ==========================================

def reset_game():

    st.session_state.stage = 1
    st.session_state.score = 100
    st.session_state.start_time = time.time()

    st.session_state.hints = {
        1: False,
        2: False,
        3: False
    }

    st.session_state.wrong = {
        1: 0,
        2: 0,
        3: 0
    }

    st.session_state.cleared = False

    st.session_state.questions = {
        1: make_question(1),
        2: make_question(2),
        3: make_question(3)
    }

    for key in list(st.session_state.keys()):

        if key.startswith((
            "answer_",
            "feedback_",
            "matrix_",
            "hill_"
        )):
            del st.session_state[key]


if "stage" not in st.session_state:
    reset_game()


# ==========================================
# 다음 단계로 이동
# ==========================================

def go_next_stage():

    st.session_state.stage += 1

    if st.session_state.stage <= 3:

        stage = st.session_state.stage

        # 다음 단계에 진입할 때 새 문제 생성
        st.session_state.questions[stage] = make_question(stage)

        st.session_state.hints[stage] = False
        st.session_state.wrong[stage] = 0

        for key in list(st.session_state.keys()):

            if key.startswith((
                f"answer_{stage}",
                f"feedback_{stage}",
                "matrix_",
                "hill_"
            )):
                del st.session_state[key]


# ==========================================
# 힌트 기능
# ==========================================

def show_hint(stage, hint_text):

    if st.button(
        "힌트 보기 (10점 감점)",
        key=f"hint_btn_{stage}"
    ):

        if not st.session_state.hints[stage]:

            st.session_state.score = max(
                0,
                st.session_state.score - 10
            )

            st.session_state.hints[stage] = True

    if st.session_state.hints[stage]:
        st.info(hint_text)


# ==========================================
# 정답 입력 기능
# ==========================================

def answer_form(stage, expected, success_message):

    answer = st.text_input(
        "복호화한 영어 단어를 입력하세요",
        key=f"answer_{stage}",
        placeholder="예: APPLE"
    )

    answer = answer.strip().upper().replace(" ", "")

    if st.button(
        "정답 확인",
        key=f"submit_{stage}",
        use_container_width=True
    ):

        if not answer:

            st.session_state[f"feedback_{stage}"] = (
                "warning",
                "답을 입력해 주세요."
            )

        elif answer == expected:

            st.session_state[f"feedback_{stage}"] = (
                "success",
                success_message
            )

            if stage < 3:
                go_next_stage()
                st.rerun()

            else:
                st.session_state.cleared = True
                st.rerun()

        else:

            st.session_state.score = max(
                0,
                st.session_state.score - 10
            )

            st.session_state.wrong[stage] += 1

            st.session_state[f"feedback_{stage}"] = (
                "error",
                "정답이 아닙니다. 계산 과정을 다시 확인해 보세요."
            )

    feedback = st.session_state.get(f"feedback_{stage}")

    if feedback:

        kind, message = feedback

        if kind == "success":
            st.success(message)

        elif kind == "warning":
            st.warning(message)

        else:
            st.error(message)


# ==========================================
# 사이드바
# ==========================================

with st.sidebar:

    st.title("🔐 게임 현황")

    st.metric(
        "현재 점수",
        f"{st.session_state.score}점"
    )

    st.metric(
        "진행 단계",
        f"{min(st.session_state.stage, 3)} / 3"
    )

    st.metric(
        "경과 시간",
        f"{int(time.time() - st.session_state.start_time)}초"
    )

    st.divider()

    st.markdown("""
    **진행 순서**

    1. 시저 암호
    2. 아핀 암호
    3. 힐 암호: 행렬 추론
    """)

    st.caption(
        "각 단계에 진입할 때 새로운 문제가 출제됩니다."
    )

    if st.button(
        "게임 처음부터 다시 시작",
        use_container_width=True
    ):

        reset_game()
        st.rerun()


# ==========================================
# 메인 화면
# ==========================================

st.title("🔐 암호 프로젝트: 방탈출")

st.markdown(
    "암호의 원리를 이해하고 세 개의 관문을 통과해 탈출하세요."
)

st.progress(
    min((st.session_state.stage - 1) / 3, 1.0),
    text=f"진행률: {min(st.session_state.stage - 1, 3)} / 3 단계 완료"
)


# ==========================================
# 탈출 성공 화면
# ==========================================

if st.session_state.cleared:

    st.balloons()

    st.title("🎉 탈출 성공!")

    st.markdown(
        f"### 최종 점수: {st.session_state.score}점"
    )

    st.write(
        f"걸린 시간: {int(time.time() - st.session_state.start_time)}초"
    )

    st.write(
        "단계별 오답 횟수: "
        + " / ".join(
            f"{i}단계 {st.session_state.wrong[i]}회"
            for i in (1, 2, 3)
        )
    )

    if st.button(
        "새로운 문제로 다시 도전",
        use_container_width=True
    ):

        reset_game()
        st.rerun()

    st.stop()


stage = st.session_state.stage
q = st.session_state.questions[stage]


# ==========================================
# 1단계: 시저 암호
# ==========================================

if stage == 1:

    st.header("1단계 · 시저 암호")

    st.markdown("""
    <div class="challenge">
    <b>문제</b><br>
    암호문은 알파벳을 모두 같은 칸 수만큼 이동시켜 만들었습니다.
    이동량을 확인하고 원래 영어 단어를 찾아보세요.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="ciphertext">{q["cipher"]}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'**암호화 이동량:** 알파벳을 {q["shift"]}칸 앞으로 이동했습니다.'
    )

    with st.expander(
        "📘 시저 암호란? 원리와 풀이 방법",
        expanded=True
    ):

        st.markdown("""
        **시저 암호**는 알파벳을 일정한 칸 수만큼 이동해
        다른 글자로 바꾸는 암호입니다.

        **기본 원리**

        - A=0, B=1, C=2, ... Z=25로 숫자를 부여합니다.
        - 암호화할 때는 알파벳을 일정한 칸 수만큼 앞으로 이동합니다.
        - 복호화할 때는 반대로 같은 칸 수만큼 뒤로 이동합니다.
        - Z 다음은 A로 이어지므로 나머지 연산(mod 26)을 사용합니다.

        **복호화 공식**

        평문 번호 = (암호문 번호 - 이동량) mod 26

        **푸는 순서**

        1. 암호문 첫 글자를 숫자로 바꿉니다.
        2. 주어진 이동량을 뺍니다.
        3. 계산 결과를 26으로 나눈 나머지를 구합니다.
        4. 결과 숫자를 알파벳으로 바꿉니다.
        5. 모든 글자에 같은 계산을 반복합니다.
        """)

    with st.expander("🧮 첫 글자 계산 예시"):

        c = q["cipher"][0]
        cv = ord(c) - 65
        pv = (cv - q["shift"]) % 26

        st.write(
            f"{c}는 {cv}번입니다."
        )

        st.write(
            f"({cv} - {q['shift']}) mod 26 = {pv}"
        )

        st.write(
            f"따라서 첫 글자는 **{ALPHABET[pv]}**입니다."
        )

        st.write("같은 계산을 나머지 글자에도 적용하세요.")

    show_hint(
        1,
        f"정답 단어는 {len(q['word'])}글자입니다. "
        f"각 글자를 {q['shift']}칸씩 뒤로 이동하세요."
    )

    answer_form(
        1,
        q["word"],
        f"정답입니다! {q['word']}를 찾았습니다."
    )


# ==========================================
# 2단계: 아핀 암호
# ==========================================

elif stage == 2:

    st.header("2단계 · 아핀 암호")

    st.markdown("""
    <div class="challenge">
    <b>문제</b><br>
    암호문은 각 알파벳 번호에 곱셈과 덧셈을 적용해 만들었습니다.
    주어진 a, b 값을 이용해 원래 영어 단어를 찾아보세요.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="ciphertext">{q["cipher"]}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'**키 값:** a = {q["a"]}, b = {q["b"]}'
    )

    with st.expander(
        "📘 아핀 암호란? 원리와 풀이 방법",
        expanded=True
    ):

        st.markdown("""
        **아핀 암호**는 각 알파벳을 숫자로 바꾼 다음,
        곱셈과 덧셈을 적용하는 암호입니다.

        **기본 원리**

        - A=0, B=1, C=2, ... Z=25
        - M: 평문 숫자
        - C: 암호문 숫자
        - a, b: 암호화에 사용하는 키 값

        **암호화 공식**

        C = (aM + b) mod 26

        **복호화 공식**

        M = a⁻¹(C - b) mod 26

        여기서 a⁻¹은 a의 곱셈 역원입니다.

        즉, 다음 식을 만족하는 수입니다.

        (a × a⁻¹) mod 26 = 1

        a와 26이 서로소여야 곱셈 역원이 존재합니다.

        **푸는 순서**

        1. a의 곱셈 역원 a⁻¹을 찾습니다.
        2. 암호문 글자를 숫자로 바꿉니다.
        3. 암호문 숫자에서 b를 뺍니다.
        4. 그 결과에 a⁻¹을 곱하고 26으로 나눈 나머지를 구합니다.
        5. 결과 숫자를 알파벳으로 바꿉니다.
        """)

    with st.expander("🧮 첫 글자 계산 예시"):

        inv = mod_inverse(q["a"], 26)

        c = q["cipher"][0]
        cv = ord(c) - 65

        mv = (inv * (cv - q["b"])) % 26

        st.write(
            f"a={q['a']}의 곱셈 역원은 {inv}입니다."
        )

        st.write(
            f"({q['a']} × {inv}) mod 26 = 1"
        )

        st.write(
            f"첫 암호문 {c}는 {cv}입니다."
        )

        st.write(
            f"M = {inv} × ({cv} - {q['b']}) mod 26 = {mv}"
        )

        st.write(
            f"따라서 첫 글자는 **{ALPHABET[mv]}**입니다."
        )

        st.write("같은 계산을 나머지 글자에도 적용하세요.")

    show_hint(
        2,
        f"정답 단어는 {len(q['word'])}글자입니다. "
        f"a={q['a']}의 곱셈 역원을 먼저 찾으세요."
    )

    answer_form(
        2,
        q["word"],
        f"정답입니다! {q['word']}를 복호화했습니다."
    )


# ==========================================
# 3단계: 힐 암호 행렬 추론
# ==========================================

else:

    st.header("3단계 · 힐 암호: 행렬 추론")

    st.markdown("""
    <div class="challenge">
    <b>문제</b><br>
    암호화에 사용된 2×2 키 행렬을 직접 추론한 뒤,
    그 행렬로 목표 암호문을 복호화하세요.
    아래에 주어진 두 쌍의 평문과 암호문은 같은 키 행렬을 사용했습니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 알려진 평문-암호문 쌍")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            '<div class="info-card">'
            '<b>평문</b>'
            '<div class="ciphertext">BA</div>'
            '<b>암호문</b>'
            f'<div class="ciphertext">{q["known_cipher1"]}</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            '<div class="info-card">'
            '<b>평문</b>'
            '<div class="ciphertext">BD</div>'
            '<b>암호문</b>'
            f'<div class="ciphertext">{q["known_cipher2"]}</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("### 목표 암호문")

    st.markdown(
        f'<div class="ciphertext">{q["cipher"]}</div>',
        unsafe_allow_html=True
    )

    with st.expander(
        "📘 힐 암호란? 원리와 풀이 방법",
        expanded=True
    ):

        st.markdown(r"""
        **힐 암호**는 알파벳을 숫자로 바꾼 다음,
        두 글자씩 묶어 행렬 곱셈으로 암호화하는 방법입니다.

        **기본 약속**

        - A=0, B=1, C=2, ... Z=25
        - 두 글자 XY를 세로 벡터로 나타냅니다.
        - 키 행렬 K와 평문 벡터 P를 곱해 암호문 벡터 C를 만듭니다.

        암호화 공식:

        \[
        C=KP\pmod{26}
        \]

        복호화 공식:

        \[
        P=K^{-1}C\pmod{26}
        \]

        **행렬 추론 방법**

        1. 평문 BA는 숫자로 바꾸면 (1, 0)입니다.
        2. 평문 BD는 숫자로 바꾸면 (1, 3)입니다.
        3. BA의 암호문으로 키 행렬의 첫 번째 열을 알아냅니다.
        4. BD의 암호문을 이용해 두 번째 열을 계산합니다.
        5. 완성한 행렬을 입력하고 확인합니다.
        6. 행렬이 맞으면 역행렬을 이용해 목표 암호문을 복호화합니다.

        원래 단어의 글자 수가 홀수라면 암호화할 때 마지막에 X를 붙입니다.
        답을 입력할 때는 원래 단어만 입력하면 됩니다.
        """)

    with st.expander("🧮 행렬을 직접 추론하는 방법"):

        st.markdown(r"""
        키 행렬을 다음과 같이 놓겠습니다.

        \[
        K=
        \begin{pmatrix}
        a&b\\
        c&d
        \end{pmatrix}
        \]

        **① 첫 번째 평문 BA 이용하기**

        \[
        BA=
        \begin{pmatrix}
        1\\
        0
        \end{pmatrix}
        \]

        따라서

        \[
        K
        \begin{pmatrix}
        1\\
        0
        \end{pmatrix}
        =
        \begin{pmatrix}
        a\\
        c
        \end{pmatrix}
        \]

        즉, BA의 암호문 숫자 두 개가 행렬의 첫 번째 열입니다.

        **② 두 번째 평문 BD 이용하기**

        \[
        BD=
        \begin{pmatrix}
        1\\
        3
        \end{pmatrix}
        \]

        따라서

        \[
        K
        \begin{pmatrix}
        1\\
        3
        \end{pmatrix}
        =
        \begin{pmatrix}
        a+3b\\
        c+3d
        \end{pmatrix}
        \pmod{26}
        \]

        첫 번째 열을 이미 구했으므로 두 번째 열을 계산할 수 있습니다.

        **③ 두 번째 열 계산하기**

        \[
        3^{-1}\equiv9\pmod{26}
        \]

        따라서 두 번째 암호문의 첫 번째 숫자를 C₁,
        두 번째 숫자를 C₂라고 하면

        \[
        b=9(C_1-a)\pmod{26}
        \]

        \[
        d=9(C_2-c)\pmod{26}
        \]

        이렇게 a, b, c, d를 모두 구하면 키 행렬이 완성됩니다.
        """)

    show_hint(
        3,
        "BA=(1,0)이므로 BA의 암호문에서 첫 번째 열을 바로 알 수 있습니다. "
        "BD=(1,3)이므로 두 번째 열은 "
        "(BD 암호문 숫자 - 첫 번째 열 숫자) × 9 mod 26으로 구합니다."
    )

    st.markdown("### 추론한 키 행렬 입력")

    st.caption("각 숫자는 0부터 25 사이의 정수입니다.")

    col1, col2 = st.columns(2)

    with col1:

        k11 = st.number_input(
            "첫째 행 · 첫째 열",
            min_value=0,
            max_value=25,
            value=0,
            step=1,
            key="matrix_k11"
        )

        k21 = st.number_input(
            "둘째 행 · 첫째 열",
            min_value=0,
            max_value=25,
            value=0,
            step=1,
            key="matrix_k21"
        )

    with col2:

        k12 = st.number_input(
            "첫째 행 · 둘째 열",
            min_value=0,
            max_value=25,
            value=0,
            step=1,
            key="matrix_k12"
        )

        k22 = st.number_input(
            "둘째 행 · 둘째 열",
            min_value=0,
            max_value=25,
            value=0,
            step=1,
            key="matrix_k22"
        )

    if st.button(
        "행렬 확인",
        key="check_matrix",
        use_container_width=True
    ):

        entered = [
            [int(k11), int(k12)],
            [int(k21), int(k22)]
        ]

        if entered == q["key"]:

            st.session_state["hill_matrix_verified"] = True

            st.success(
                "행렬 추론 성공! 이제 목표 암호문을 복호화하세요."
            )

        else:

            st.session_state["hill_matrix_verified"] = False

            st.session_state.score = max(
                0,
                st.session_state.score - 5
            )

            st.session_state.wrong[3] += 1

            st.error(
                "행렬이 맞지 않습니다. "
                "알려진 두 쌍과 mod 26 계산을 다시 확인하세요."
            )

    # 행렬이 정답일 때만 복호화 단계 공개

    if st.session_state.get("hill_matrix_verified", False):

        st.success("추론한 키 행렬이 맞습니다!")

        key = q["key"]

        st.latex(
            r"K=\begin{pmatrix}%d&%d\\%d&%d\end{pmatrix}"
            % (key[0][0], key[0][1], key[1][0], key[1][1])
        )

        inverse = matrix_mod_inverse(key)

        with st.expander("🧮 목표 암호문 복호화 계산"):

            st.write("① 키 행렬의 역행렬을 구합니다.")

            st.latex(
                r"K^{-1}=\begin{pmatrix}%d&%d\\%d&%d\end{pmatrix}"
                % (
                    inverse[0][0],
                    inverse[0][1],
                    inverse[1][0],
                    inverse[1][1]
                )
            )

            st.write("② 목표 암호문을 두 글자씩 나눕니다.")

            first_pair = q["cipher"][:2]

            cx = ord(first_pair[0]) - 65
            cy = ord(first_pair[1]) - 65

            px = (
                inverse[0][0] * cx
                + inverse[0][1] * cy
            ) % 26

            py = (
                inverse[1][0] * cx
                + inverse[1][1] * cy
            ) % 26

            st.write(
                f"첫 묶음 {first_pair} → ({cx}, {cy})"
            )

            st.write(
                f"복호화 결과: ({px}, {py})"
            )

            st.write(
                f"따라서 첫 두 글자는 **{ALPHABET[px]}{ALPHABET[py]}**입니다."
            )

            st.write(
                "나머지 묶음에도 같은 계산을 반복하세요."
            )

            if len(q["word"]) % 2 == 1:

                st.caption(
                    "원래 단어가 홀수 글자여서 마지막에 X가 붙었습니다. "
                    "답에는 원래 단어만 입력하세요."
                )

        show_hint(
            3,
            "목표 암호문을 두 글자씩 나누고, "
            "각 숫자 벡터에 K⁻¹을 곱한 뒤 mod 26을 적용하세요."
        )

        answer_form(
            3,
            q["word"],
            f"정답입니다! {q['word']}를 복호화해 최종 관문을 통과했습니다."
        )

    else:

        st.info(
            "먼저 키 행렬 네 숫자를 추론해 입력하세요. "
            "행렬이 맞아야 평문 답안을 제출할 수 있습니다."
        )


# ==========================================
# 하단 안내
# ==========================================

st.divider()

st.caption(
    "정답은 지정된 단어 목록에서만 출제됩니다. "
    "각 단계의 문제는 새로 시작하거나 다음 단계로 이동할 때 바뀝니다."
)
