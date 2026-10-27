import random
import time
import string
import math

import streamlit as st

# =========================================================
# 🔐 암호 방탈출 게임 - 시저 / 아핀 / 힐 암호
# Streamlit 단일 파일 버전 (utils.py 불필요)
# =========================================================

st.set_page_config(
    page_title="수학 실험실 탈출 게임",
    page_icon="🔐",
    layout="centered",
)

# ---------- 밝고 읽기 쉬운 디자인 ----------
st.markdown("""
<style>
.stApp {
    background: #F4F7FB;
    color: #172033;
}
[data-testid="stHeader"] { background: rgba(244,247,251,0.95); }
[data-testid="stSidebar"] {
    background: #E7EDF6;
}
h1, h2, h3, h4, p, li, label, .stMarkdown, .stText, [data-testid="stMetricValue"] {
    color: #172033 !important;
}
h1 { font-weight: 800 !important; }
h2, h3 { font-weight: 750 !important; }
.stAlert p { color: #172033 !important; }
div[data-testid="stCode"] {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 12px;
}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #FFFFFF !important;
    color: #111827 !important;
    border: 1px solid #94A3B8 !important;
    border-radius: 9px !important;
}
.stButton > button {
    background: #1D4ED8;
    color: #FFFFFF !important;
    border: 0;
    border-radius: 9px;
    font-weight: 700;
    min-height: 42px;
}
.stButton > button:hover {
    background: #1E40AF;
    color: #FFFFFF !important;
    border: 0;
}
details {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 10px;
    padding: 8px 12px;
}
hr { border-color: #CBD5E1; }
.small-note { color: #334155 !important; font-size: 0.95rem; }
.challenge {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-left: 6px solid #2563EB;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 12px 0;
}
.ciphertext {
    font-size: 2rem;
    font-weight: 850;
    letter-spacing: 0.12em;
    color: #123A78 !important;
    text-align: center;
    padding: 10px 0;
}
</style>
""", unsafe_allow_html=True)

ALPHABET = string.ascii_uppercase
WORD_BANK = [
    "CODE", "MATH", "DATA", "BYTE", "ROBOT", "LOGIC", "BRAIN",
    "LIGHT", "PLANT", "WATER", "APPLE", "GRAPE", "MUSIC", "WORLD",
    "HELLO", "QUEST", "PIXEL", "CLOUD", "DREAM", "SMART", "TIGER",
    "RIVER", "STONE", "HEART", "NIGHT", "SPACE", "EARTH", "TRAIN",
    "HOUSE", "GREEN", "HAPPY", "SCORE", "TRACE", "LEARN", "LASER",
]

def mod_inverse(a, m=26):
    a %= m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def caesar_encrypt(text, shift):
    return "".join(ALPHABET[(ord(ch) - 65 + shift) % 26] for ch in text)

def caesar_decrypt(text, shift):
    return "".join(ALPHABET[(ord(ch) - 65 - shift) % 26] for ch in text)

def affine_encrypt(text, a, b):
    return "".join(ALPHABET[(a * (ord(ch) - 65) + b) % 26] for ch in text)

def affine_decrypt(text, a, b):
    inv = mod_inverse(a, 26)
    if inv is None:
        raise ValueError("a와 26은 서로소여야 합니다.")
    return "".join(ALPHABET[(inv * ((ord(ch) - 65) - b)) % 26] for ch in text)

def matrix_det(matrix):
    return (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 26

def matrix_mod_inverse(matrix):
    a, b = matrix[0]
    c, d = matrix[1]
    det = (a * d - b * c) % 26
    det_inv = mod_inverse(det, 26)
    if det_inv is None:
        return None
    return [
        [(det_inv * d) % 26, (det_inv * (-b)) % 26],
        [(det_inv * (-c)) % 26, (det_inv * a) % 26],
    ]

def hill_encrypt(text, matrix):
    # 2글자씩 처리하므로 홀수 길이는 X를 붙여 짝수로 만듭니다.
    padded = text if len(text) % 2 == 0 else text + "X"
    result = []
    for i in range(0, len(padded), 2):
        x, y = ord(padded[i]) - 65, ord(padded[i + 1]) - 65
        c1 = (matrix[0][0] * x + matrix[0][1] * y) % 26
        c2 = (matrix[1][0] * x + matrix[1][1] * y) % 26
        result.extend([ALPHABET[c1], ALPHABET[c2]])
    return "".join(result)

def hill_decrypt(text, matrix):
    inv = matrix_mod_inverse(matrix)
    if inv is None:
        raise ValueError("복호화할 수 없는 행렬입니다.")
    result = []
    for i in range(0, len(text), 2):
        x, y = ord(text[i]) - 65, ord(text[i + 1]) - 65
        p1 = (inv[0][0] * x + inv[0][1] * y) % 26
        p2 = (inv[1][0] * x + inv[1][1] * y) % 26
        result.extend([ALPHABET[p1], ALPHABET[p2]])
    return "".join(result)

def new_hill_key():
    # 행렬식과 26이 서로소인 행렬만 사용해 복호화가 항상 가능하도록 합니다.
    candidates = []
    for _ in range(500):
        matrix = [
            [random.randint(0, 25), random.randint(0, 25)],
            [random.randint(0, 25), random.randint(0, 25)],
        ]
        det = matrix_det(matrix)
        if math.gcd(det, 26) == 1 and matrix_mod_inverse(matrix) is not None:
            candidates.append(matrix)
            break
    if candidates:
        return candidates[0]
    return [[3, 3], [2, 5]]

def make_question(stage):
    word = random.choice(WORD_BANK)
    if stage == 1:
        shift = random.randint(1, 25)
        return {"word": word, "shift": shift, "cipher": caesar_encrypt(word, shift)}
    if stage == 2:
        valid_a = [a for a in range(1, 26) if math.gcd(a, 26) == 1]
        a = random.choice(valid_a)
        b = random.randint(0, 25)
        return {"word": word, "a": a, "b": b, "cipher": affine_encrypt(word, a, b)}
    key = new_hill_key()
    padded = word if len(word) % 2 == 0 else word + "X"
    return {"word": word, "key": key, "padded": padded, "cipher": hill_encrypt(word, key)}

def reset_game():
    st.session_state.stage = 1
    st.session_state.score = 100
    st.session_state.start_time = time.time()
    st.session_state.hints = {1: False, 2: False, 3: False}
    st.session_state.wrong = {1: 0, 2: 0, 3: 0}
    st.session_state.cleared = False
    st.session_state.questions = {i: make_question(i) for i in (1, 2, 3)}
    for i in (1, 2, 3):
        st.session_state.pop(f"answer_{i}", None)
        st.session_state.pop(f"feedback_{i}", None)

if "stage" not in st.session_state:
    reset_game()

def go_next_stage():
    st.session_state.stage += 1
    if st.session_state.stage <= 3:
        # 단계에 새로 들어갈 때마다 새 문제 생성
        st.session_state.questions[st.session_state.stage] = make_question(st.session_state.stage)
        st.session_state.hints[st.session_state.stage] = False
        st.session_state.wrong[st.session_state.stage] = 0
        st.session_state.pop(f"answer_{st.session_state.stage}", None)
        st.session_state.pop(f"feedback_{st.session_state.stage}", None)

def show_hint(stage, text):
    if st.button("힌트 보기 (10점 감점)", key=f"hint_btn_{stage}"):
        if not st.session_state.hints[stage]:
            st.session_state.score = max(0, st.session_state.score - 10)
            st.session_state.hints[stage] = True
    if st.session_state.hints[stage]:
        st.info(text)

def answer_form(stage, expected, explanation, allow_padding=False):
    answer = st.text_input(
        "평문을 입력하세요 (영어 단어)",
        key=f"answer_{stage}",
        placeholder="예: CODE",
    ).strip().upper().replace(" ", "")
    if st.button("정답 확인", key=f"submit_{stage}", use_container_width=True):
        cleaned = answer
        if allow_padding and len(cleaned) == len(expected) - 1 and expected.endswith("X"):
            pass
        if cleaned == expected or (allow_padding and expected.endswith("X") and cleaned == expected[:-1]):
            st.session_state[f"feedback_{stage}"] = ("success", explanation)
            if stage < 3:
                st.success("정답입니다! 다음 단계로 이동합니다.")
                time.sleep(0.5)
                go_next_stage()
                st.rerun()
            else:
                st.session_state.cleared = True
                st.rerun()
        elif not cleaned:
            st.session_state[f"feedback_{stage}"] = ("warning", "답을 입력해 주세요.")
        else:
            st.session_state.score = max(0, st.session_state.score - 10)
            st.session_state.wrong[stage] += 1
            st.session_state[f"feedback_{stage}"] = ("error", "아직 정답이 아니에요. 설명과 힌트를 확인하고 다시 시도해 보세요.")
    feedback = st.session_state.get(f"feedback_{stage}")
    if feedback:
        kind, message = feedback
        if kind == "success":
            st.success(message)
        elif kind == "warning":
            st.warning(message)
        else:
            st.error(message)

# ---------- 사이드바 ----------
with st.sidebar:
    st.title("🔐 게임 현황")
    st.metric("점수", f"{st.session_state.score}점")
    st.metric("진행 단계", f"{min(st.session_state.stage, 3)} / 3")
    elapsed = int(time.time() - st.session_state.start_time)
    st.metric("경과 시간", f"{elapsed}초")
    st.divider()
    st.subheader("진행 순서")
    st.markdown("**1. 시저 암호**  \n**2. 아핀 암호**  \n**3. 힐 암호**")
    st.caption("각 단계의 새 문제는 무작위로 출제됩니다.")
    if st.button("게임 처음부터 다시 시작", use_container_width=True):
        reset_game()
        st.rerun()

st.title("🔐 수학 실험실 탈출 게임")
st.markdown("문제를 풀어 암호의 문을 열어 보세요.")
st.progress(min((st.session_state.stage - 1) / 3, 1.0), text=f"진행률: {min(st.session_state.stage - 1, 3)} / 3 단계 완료")

if st.session_state.cleared:
    st.balloons()
    st.title("🎉 탈출 성공!")
    elapsed = int(time.time() - st.session_state.start_time)
    st.markdown(f"### 최종 점수: {st.session_state.score}점")
    st.write(f"걸린 시간: {elapsed}초")
    st.write("단계별 오답 횟수: " + " / ".join(f"{i}단계 {st.session_state.wrong[i]}회" for i in (1, 2, 3)))
    if st.button("새로운 문제로 다시 도전", use_container_width=True):
        reset_game()
        st.rerun()
    st.stop()

stage = st.session_state.stage
q = st.session_state.questions[stage]

# =========================================================
# 1단계: 시저 암호
# =========================================================
if stage == 1:
    st.header("1단계 · 시저 암호")
    st.markdown("""
<div class="challenge">
<b>문제</b><br>
아래 암호문은 모든 알파벳을 같은 칸 수만큼 이동시켜 만들었습니다.
이동량을 확인하고 원래 영어 단어를 찾아보세요.
</div>
""", unsafe_allow_html=True)
    st.markdown(f'<div class="ciphertext">{q["cipher"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**이동량:** {q['shift']}칸 앞으로 암호화했습니다.")
    with st.expander("📘 시저 암호란? 자세한 설명 보기", expanded=True):
        st.markdown("""
**시저 암호**는 알파벳을 일정한 칸 수만큼 옮겨 다른 알파벳으로 바꾸는 가장 단순한 암호예요.

**푸는 방법**
1. 암호문 글자를 확인합니다.
2. 암호화할 때 앞으로 이동했으므로, 복호화할 때는 같은 칸 수만큼 **뒤로** 이동합니다.
3. 알파벳 끝을 지나면 처음으로 돌아갑니다. 예를 들어 A에서 한 칸 뒤로 가면 Z입니다.
4. 바꾼 글자를 순서대로 이어 영어 단어를 만듭니다.

**알파벳 번호표:** A=0, B=1, C=2, …, Z=25  
**계산식:** 평문 번호 = (암호문 번호 − 이동량) mod 26
""")
    with st.expander("🧮 글자 하나를 직접 계산해 보는 예시"):
        st.write(f"이 문제의 이동량은 {q['shift']}칸입니다.")
        example_cipher_letter = q["cipher"][0]
        example_num = ord(example_cipher_letter) - 65
        plain_num = (example_num - q["shift"]) % 26
        st.write(f"첫 글자 {example_cipher_letter}의 번호는 {example_num}입니다.")
        st.write(f"({example_num} − {q['shift']}) mod 26 = {plain_num}")
        st.write(f"번호 {plain_num}은 알파벳 **{ALPHABET[plain_num]}**입니다. 나머지 글자에도 같은 방법을 적용하세요.")
    show_hint(1, f"정답은 {len(q['word'])}글자입니다. 각 암호문 글자를 {q['shift']}칸씩 뒤로 이동해 보세요.")
    answer_form(1, q["word"], f"정답은 {q['word']}입니다. 각 문자를 {q['shift']}칸 뒤로 이동하면 원래 단어가 나옵니다.")

# =========================================================
# 2단계: 아핀 암호
# =========================================================
elif stage == 2:
    st.header("2단계 · 아핀 암호")
    st.markdown("""
<div class="challenge">
<b>문제</b><br>
아래 암호문은 알파벳 번호에 곱셈과 덧셈을 적용해 만들었습니다.
주어진 a, b 값을 이용해 원래 영어 단어를 찾아보세요.
</div>
""", unsafe_allow_html=True)
    st.markdown(f'<div class="ciphertext">{q["cipher"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**키 값:** a = {q['a']}, b = {q['b']}")
    with st.expander("📘 아핀 암호란? 자세한 설명 보기", expanded=True):
        st.markdown("""
**아핀 암호**는 각 알파벳을 숫자로 바꾼 뒤, 곱하고 더하는 계산으로 암호화하는 방법이에요.

**암호화 공식:** C = (a × M + b) mod 26  
**복호화 공식:** M = a⁻¹ × (C − b) mod 26

- M: 원래 알파벳의 번호
- C: 암호문 알파벳의 번호
- a⁻¹: a의 곱셈 역원. (a × a⁻¹) mod 26 = 1을 만족하는 수
- b: 더해 준 값
- mod 26: 26으로 나눈 나머지

**푸는 방법**
1. 암호문 글자를 A=0, B=1, …, Z=25로 바꿉니다.
2. 먼저 a의 역원 a⁻¹을 찾습니다.
3. 각 글자에 M = a⁻¹ × (C − b) mod 26을 적용합니다.
4. 결과 숫자를 알파벳으로 되돌려 단어를 완성합니다.
""")
    with st.expander("🧮 역원과 복호화 계산 예시"):
        inv = mod_inverse(q["a"], 26)
        st.write(f"이 문제에서 a={q['a']}의 역원은 **{inv}**입니다. 왜냐하면 ({q['a']} × {inv}) mod 26 = 1이기 때문입니다.")
        c_letter = q["cipher"][0]
        c_num = ord(c_letter) - 65
        m_num = (inv * (c_num - q["b"])) % 26
        st.write(f"첫 암호문 글자 {c_letter}는 숫자 {c_num}입니다.")
        st.write(f"M = {inv} × ({c_num} − {q['b']}) mod 26 = {m_num}")
        st.write(f"숫자 {m_num}은 **{ALPHABET[m_num]}**입니다. 나머지 글자에도 같은 계산을 해 보세요.")
    show_hint(2, f"정답은 {len(q['word'])}글자입니다. 먼저 a={q['a']}의 역원을 찾고, 각 글자에 복호화 공식을 적용하세요.")
    answer_form(2, q["word"], f"정답은 {q['word']}입니다. a⁻¹={mod_inverse(q['a'], 26)}을 이용해 복호화할 수 있습니다.")

# =========================================================
# 3단계: 힐 암호
# =========================================================
else:
    st.header("3단계 · 힐 암호 최종 관문")
    st.markdown("""
<div class="challenge">
<b>문제</b><br>
아래 암호문은 두 글자씩 묶어 2×2 행렬로 암호화했습니다.
키 행렬과 설명을 참고해 원래 영어 단어를 찾아보세요.
</div>
""", unsafe_allow_html=True)
    st.markdown(f'<div class="ciphertext">{q["cipher"]}</div>', unsafe_allow_html=True)
    key = q["key"]
    st.markdown("**암호화 키 행렬 K**")
    st.latex(r"K=\begin{pmatrix}%d&%d\\%d&%d\end{pmatrix}" % (key[0][0], key[0][1], key[1][0], key[1][1]))
    with st.expander("📘 힐 암호란? 자세한 설명 보기", expanded=True):
        st.markdown("""
**힐 암호**는 알파벳을 숫자로 바꾸고, 여러 글자를 묶어 행렬 곱셈으로 암호화하는 방법이에요.

**알파벳 번호:** A=0, B=1, …, Z=25

**암호화 방법**
1. 평문을 두 글자씩 나눕니다. 예: CODE → CO / DE
2. 각 글자를 숫자로 바꿉니다. 예: C=2, O=14
3. 두 숫자를 세로 벡터로 만들고 키 행렬 K를 곱합니다.
4. 각 결과를 26으로 나눈 나머지로 바꾼 뒤 알파벳으로 되돌립니다.
5. 글자 수가 홀수라면 마지막에 X를 붙여 짝수로 맞춥니다.

**복호화 방법**
1. 키 행렬의 역행렬을 mod 26에서 구합니다.
2. 암호문을 두 글자씩 숫자로 바꿉니다.
3. 역행렬을 각 숫자 벡터에 곱하고 mod 26을 적용합니다.
4. 결과 숫자를 알파벳으로 되돌립니다. 홀수 단어를 위해 붙인 마지막 X는 제외합니다.

힐 암호는 행렬식과 26이 서로소인 키 행렬만 복호화에 사용할 수 있습니다. 이 게임은 복호화 가능한 행렬만 자동으로 골라 사용합니다.
""")
    with st.expander("🧮 이번 문제의 복호화 계산 도우미"):
        inv_key = matrix_mod_inverse(key)
        st.write("1. 키 행렬의 역행렬(mod 26)은 다음과 같습니다.")
        st.latex(r"K^{-1}=\begin{pmatrix}%d&%d\\%d&%d\end{pmatrix}" % (inv_key[0][0], inv_key[0][1], inv_key[1][0], inv_key[1][1]))
        st.write("2. 암호문을 두 글자씩 나누고 A=0, …, Z=25로 바꿉니다.")
        first_pair = q["cipher"][:2]
        cx, cy = ord(first_pair[0]) - 65, ord(first_pair[1]) - 65
        px = (inv_key[0][0] * cx + inv_key[0][1] * cy) % 26
        py = (inv_key[1][0] * cx + inv_key[1][1] * cy) % 26
        st.write(f"첫 묶음 **{first_pair}** → 숫자 벡터 ({cx}, {cy})")
        st.write(f"3. 역행렬을 곱합니다: 결과는 ({px}, {py})이고, 알파벳 **{ALPHABET[px]}{ALPHABET[py]}**가 됩니다.")
        st.write("4. 나머지 두 글자 묶음에도 같은 과정을 반복하세요.")
        if len(q["word"]) % 2 == 1:
            st.caption("참고: 이번 평문은 홀수 글자이므로 암호화 전에 X가 하나 붙었습니다. 정답에는 원래 단어만 입력하세요.")
    show_hint(3, f"원래 단어는 {len(q['word'])}글자입니다. 암호문을 두 글자씩 나누고, 키 행렬의 역행렬을 곱해 보세요.")
    answer_form(3, q["word"], f"정답은 {q['word']}입니다. 힐 암호는 두 글자씩 행렬 연산을 하며, 홀수 글자 단어는 마지막에 붙인 X를 정답에서 제외합니다.")

st.divider()
st.caption("문제는 단계에 들어갈 때마다 새로 생성됩니다. 알파벳은 대소문자를 구분하지 않으며, 답 입력 시 공백은 무시됩니다.")
