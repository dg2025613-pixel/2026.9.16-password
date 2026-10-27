from pathlib import Path

app_code = r'''import random
import time
import string
import math
import streamlit as st

st.set_page_config(page_title="암호 프로젝트 | 방탈출", page_icon="🔐", layout="centered")

# ---------- 어두운 테마: 짙은 남색 배경 + 밝은 글자 ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0B1020 0%, #111B32 55%, #15152B 100%);
    color: #F3F6FF;
}
[data-testid="stHeader"] { background: rgba(11,16,32,0.92); }
[data-testid="stSidebar"] { background: #10182B; }
h1, h2, h3, h4, p, li, label, .stMarkdown, .stText, [data-testid="stMetricValue"],
[data-testid="stMetricLabel"], .stCaption, .stRadio label, .stCheckbox label {
    color: #F3F6FF !important;
}
h1 { font-weight: 850 !important; }
h2, h3 { font-weight: 800 !important; }
.stCaption, small { color: #C0CBE0 !important; }
.stAlert p { color: #F3F6FF !important; }
div[data-testid="stCode"], div[data-testid="stExpander"] {
    background: #17233B;
    border: 1px solid #344766;
    border-radius: 12px;
}
details {
    background: #17233B;
    border: 1px solid #344766;
    border-radius: 12px;
    padding: 8px 12px;
}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #F8FAFF !important;
    color: #111827 !important;
    border: 2px solid #7185A8 !important;
    border-radius: 9px !important;
}
.stButton > button {
    background: #6D5DFB;
    color: #FFFFFF !important;
    border: 1px solid #887BFF;
    border-radius: 10px;
    font-weight: 800;
    min-height: 42px;
}
.stButton > button:hover {
    background: #5142D8;
    color: #FFFFFF !important;
    border: 1px solid #A69DFF;
}
hr { border-color: #344766; }
.challenge {
    background: #17233B;
    border: 1px solid #344766;
    border-left: 6px solid #8B7CFF;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 12px 0;
    color: #F3F6FF;
}
.ciphertext {
    font-size: 2.15rem;
    font-weight: 900;
    letter-spacing: 0.16em;
    color: #9DE7FF !important;
    text-align: center;
    padding: 12px 0;
}
.info-card {
    background: #10182B;
    border: 1px solid #344766;
    border-radius: 10px;
    padding: 12px 15px;
    margin: 8px 0;
    color: #F3F6FF;
}
div[data-testid="stForm"] {
    background: #17233B;
    border: 1px solid #344766;
    padding: 14px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

ALPHABET = string.ascii_uppercase
# 정답은 이 목록에서만 선택되며 모두 4~5글자입니다.
WORD_BANK = [
    "APPLE", "GRAPE", "BRAIN", "PLANT", "DREAM", "LIGHT", "MUSIC",
    "WATER", "HOUSE", "SMILE", "CLOUD", "TRAIN", "EARTH", "HEART",
    "STONE", "RIVER", "SPACE", "NIGHT", "SUGAR", "BEACH", "TIGER",
    "ZEBRA", "CHAIR", "PAPER", "PHONE", "MOUSE", "GREEN", "BLACK",
    "WHITE", "BREAD",
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
    for _ in range(2000):
        matrix = [[random.randint(0, 25), random.randint(0, 25)],
                  [random.randint(0, 25), random.randint(0, 25)]]
        det = matrix_det(matrix)
        if math.gcd(det, 26) == 1 and matrix_mod_inverse(matrix) is not None:
            return matrix
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
    # 행렬 추론에 사용할 알려진 평문-암호문 쌍
    known1, known2 = "BA", "BD"
    return {
        "word": word, "key": key,
        "known1": known1, "known2": known2,
        "known_cipher1": hill_encrypt(known1, key),
        "known_cipher2": hill_encrypt(known2, key),
        "cipher": hill_encrypt(word, key),
    }

def reset_game():
    st.session_state.stage = 1
    st.session_state.score = 100
    st.session_state.start_time = time.time()
    st.session_state.hints = {1: False, 2: False, 3: False}
    st.session_state.wrong = {1: 0, 2: 0, 3: 0}
    st.session_state.cleared = False
    st.session_state.questions = {i: make_question(i) for i in (1, 2, 3)}
    for key in list(st.session_state.keys()):
        if key.startswith(("answer_", "feedback_", "matrix_", "hill_")):
            del st.session_state[key]

if "stage" not in st.session_state:
    reset_game()

def go_next_stage():
    st.session_state.stage += 1
    if st.session_state.stage <= 3:
        stage = st.session_state.stage
        st.session_state.questions[stage] = make_question(stage)
        st.session_state.hints[stage] = False
        st.session_state.wrong[stage] = 0
        for key in list(st.session_state.keys()):
            if key.startswith((f"answer_{stage}", f"feedback_{stage}", "matrix_", "hill_")):
                del st.session_state[key]

def show_hint(stage, text):
    if st.button("힌트 보기 (10점 감점)", key=f"hint_btn_{stage}"):
        if not st.session_state.hints[stage]:
            st.session_state.score = max(0, st.session_state.score - 10)
            st.session_state.hints[stage] = True
    if st.session_state.hints[stage]:
        st.info(text)

def answer_form(stage, expected, explanation):
    answer = st.text_input("복호화한 영어 단어를 입력하세요", key=f"answer_{stage}",
                           placeholder="예: APPLE").strip().upper().replace(" ", "")
    if st.button("정답 확인", key=f"submit_{stage}", use_container_width=True):
        if not answer:
            st.session_state[f"feedback_{stage}"] = ("warning", "답을 입력해 주세요.")
        elif answer == expected:
            st.session_state[f"feedback_{stage}"] = ("success", explanation)
            if stage < 3:
                go_next_stage()
                st.rerun()
            else:
                st.session_state.cleared = True
                st.rerun()
        else:
            st.session_state.score = max(0, st.session_state.score - 10)
            st.session_state.wrong[stage] += 1
            st.session_state[f"feedback_{stage}"] = ("error", "아직 정답이 아니에요. 설명과 계산을 다시 확인해 보세요.")
    feedback = st.session_state.get(f"feedback_{stage}")
    if feedback:
        kind, message = feedback
        if kind == "success":
            st.success(message)
        elif kind == "warning":
            st.warning(message)
        else:
            st.error(message)

with st.sidebar:
    st.title("🔐 게임 현황")
    st.metric("점수", f"{st.session_state.score}점")
    st.metric("진행 단계", f"{min(st.session_state.stage, 3)} / 3")
    st.metric("경과 시간", f"{int(time.time() - st.session_state.start_time)}초")
    st.divider()
    st.markdown("**진행 순서**  \n1. 시저 암호  \n2. 아핀 암호  \n3. 힐 암호: 행렬 추론")
    st.caption("각 단계에 들어갈 때 새로운 문제가 만들어집니다.")
    if st.button("게임 처음부터 다시 시작", use_container_width=True):
        reset_game()
        st.rerun()

st.title("🔐 암호 프로젝트: 방탈출")
st.markdown("암호의 원리를 이해하고 세 개의 관문을 통과해 탈출하세요.")
st.progress(min((st.session_state.stage - 1) / 3, 1.0),
             text=f"진행률: {min(st.session_state.stage - 1, 3)} / 3 단계 완료")

if st.session_state.cleared:
    st.balloons()
    st.title("🎉 탈출 성공!")
    st.markdown(f"### 최종 점수: {st.session_state.score}점")
    st.write(f"걸린 시간: {int(time.time() - st.session_state.start_time)}초")
    st.write("단계별 오답 횟수: " + " / ".join(f"{i}단계 {st.session_state.wrong[i]}회" for i in (1, 2, 3)))
    if st.button("새로운 문제로 다시 도전", use_container_width=True):
        reset_game()
        st.rerun()
    st.stop()

stage = st.session_state.stage
q = st.session_state.questions[stage]

if stage == 1:
    st.header("1단계 · 시저 암호")
    st.markdown("""
<div class="challenge"><b>문제</b><br>
암호문은 알파벳을 모두 같은 칸 수만큼 이동시켜 만들었습니다.
이동량을 확인하고 원래 영어 단어를 찾아보세요.</div>
""", unsafe_allow_html=True)
    st.markdown(f'<div class="ciphertext">{q["cipher"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**암호화 이동량:** 알파벳을 {q['shift']}칸 앞으로 이동했습니다.")
    with st.expander("📘 시저 암호란? 원리와 풀이 방법", expanded=True):
        st.markdown("""
**시저 암호**는 알파벳을 일정한 칸 수만큼 이동해 다른 글자로 바꾸는 암호입니다.

**푸는 순서**
1. 알파벳을 숫자로 생각합니다: A=0, B=1, …, Z=25.
2. 암호화할 때 앞으로 이동했으므로, 복호화할 때는 주어진 이동량만큼 뒤로 이동합니다.
3. Z 다음은 A로 이어지는 것처럼 알파벳 끝에서는 처음으로 돌아갑니다.
4. 모든 글자에 같은 계산을 한 뒤 순서대로 이어 붙입니다.

**공식:** 평문 번호 = (암호문 번호 − 이동량) mod 26  
예를 들어 암호문 글자가 D(3)이고 이동량이 3이면 (3−3) mod 26 = 0이므로 A입니다.
""")
    with st.expander("🧮 이 문제의 첫 글자 계산"):
        c = q["cipher"][0]
        cv = ord(c) - 65
        pv = (cv - q["shift"]) % 26
        st.write(f"{c}는 {cv}번입니다. ({cv} − {q['shift']}) mod 26 = {pv}이므로 첫 글자는 **{ALPHABET[pv]}**입니다.")
        st.write("같은 계산을 나머지 글자에도 적용하세요.")
    show_hint(1, f"정답 단어는 {len(q['word'])}글자입니다. 각 글자를 {q['shift']}칸씩 뒤로 이동하세요.")
    answer_form(1, q["word"], f"정답입니다! {q['word']}를 찾았습니다.")

elif stage == 2:
    st.header("2단계 · 아핀 암호")
    st.markdown("""
<div class="challenge"><b>문제</b><br>
암호문은 각 알파벳 번호에 곱셈과 덧셈을 적용해 만들었습니다.
주어진 a, b 값을 이용해 원래 영어 단어를 찾아보세요.</div>
""", unsafe_allow_html=True)
    st.markdown(f'<div class="ciphertext">{q["cipher"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**키 값:** a = {q['a']}, b = {q['b']}")
    with st.expander("📘 아핀 암호란? 원리와 풀이 방법", expanded=True):
        st.markdown("""
**아핀 암호**는 각 알파벳을 숫자로 바꾼 다음, 곱하고 더하는 계산을 적용하는 암호입니다.

- 평문 번호 M, 암호문 번호 C (A=0, B=1, …, Z=25)
- **암호화:** C = (aM + b) mod 26
- **복호화:** M = a⁻¹(C − b) mod 26
- a⁻¹은 a의 곱셈 역원입니다. 즉 (a × a⁻¹) mod 26 = 1을 만족합니다.
- a와 26은 서로소여야 역원이 존재합니다. 이 게임은 복호화 가능한 a만 사용합니다.

**푸는 순서**
1. a의 곱셈 역원 a⁻¹을 찾습니다.
2. 암호문 글자를 숫자로 바꿉니다.
3. 각 글자에 M = a⁻¹(C−b) mod 26을 계산합니다.
4. 결과 숫자를 알파벳으로 바꾸고 이어 붙입니다.
""")
    with st.expander("🧮 이 문제의 첫 글자 계산"):
        inv = mod_inverse(q["a"], 26)
        c = q["cipher"][0]
        cv = ord(c) - 65
        mv = (inv * (cv - q["b"])) % 26
        st.write(f"a={q['a']}의 역원은 {inv}입니다. ({q['a']}×{inv}) mod 26 = 1입니다.")
        st.write(f"첫 암호문 {c}는 {cv}입니다. M = {inv}×({cv}−{q['b']}) mod 26 = {mv}이므로 첫 글자는 **{ALPHABET[mv]}**입니다.")
        st.write("같은 계산을 나머지 글자에도 적용하세요.")
    show_hint(2, f"정답 단어는 {len(q['word'])}글자입니다. a={q['a']}의 역원을 먼저 찾으세요.")
    answer_form(2, q["word"], f"정답입니다! {q['word']}를 복호화했습니다.")

else:
    st.header("3단계 · 힐 암호: 행렬 추론")
    st.markdown("""
<div class="challenge"><b>문제</b><br>
암호화에 사용된 2×2 키 행렬을 직접 추론한 뒤, 그 행렬로 목표 암호문을 복호화하세요.
아래에 주어진 두 쌍의 평문과 암호문은 같은 키 행렬을 사용했습니다.</div>
""", unsafe_allow_html=True)

    st.markdown("**알려진 평문-암호문 쌍**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="info-card"><b>평문</b><div class="ciphertext">BA</div><b>암호문</b><div class="ciphertext">' + q["known_cipher1"] + '</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="info-card"><b>평문</b><div class="ciphertext">BD</div><b>암호문</b><div class="ciphertext">' + q["known_cipher2"] + '</div></div>', unsafe_allow_html=True)

    st.markdown("**목표 암호문**")
    st.markdown(f'<div class="ciphertext">{q["cipher"]}</div>', unsafe_allow_html=True)

    with st.expander("📘 힐 암호란? 원리와 풀이 방법", expanded=True):
        st.markdown("""
**힐 암호**는 알파벳을 숫자로 바꾸고, 두 글자씩 묶어 행렬 곱셈으로 암호화하는 방법입니다.

**기본 약속**
- A=0, B=1, …, Z=25로 바꿉니다.
- 두 글자 XY는 세로 벡터 \\(\\begin{pmatrix}X\\\\Y\\end{pmatrix}\\)로 나타냅니다.
- 암호화는 \\(C=KP\\pmod{26}\\)입니다. K는 키 행렬, P는 평문 벡터, C는 암호문 벡터입니다.
- 글자 수가 홀수이면 암호화 전에 X를 붙여 짝수로 만듭니다.

**행렬 추론 방법**
1. 평문 BA는 숫자 벡터 \\((1,0)^T\\)입니다. 따라서 K를 곱하면 K의 첫 번째 열이 그대로 암호문 숫자가 됩니다.
2. 평문 BD는 \\((1,3)^T\\)입니다. 암호문은 K의 첫 번째 열에 K의 두 번째 열의 3배를 더한 값입니다(각 계산은 mod 26).
3. 두 번째 열의 각 원소를 구할 때는 \\(3^{-1}\\equiv9\\pmod{26}\\)을 이용합니다. 3×9=27이고 27을 26으로 나눈 나머지는 1입니다.
4. 이렇게 구한 네 숫자로 K를 완성합니다.
5. 목표 암호문을 두 글자씩 묶고, K의 역행렬을 곱해 평문을 복원합니다.

키 행렬은 행렬식과 26이 서로소일 때만 mod 26에서 역행렬을 가집니다. 이 게임은 복호화할 수 있는 키만 출제합니다.
""")
    with st.expander("🧮 행렬을 어떻게 추론하나요?"):
        st.markdown("""
키 행렬을 \\(K=\\begin{pmatrix}a&b\\\\c&d\\end{pmatrix}\\)라고 합시다.

- BA=(1,0)ᵀ이므로 첫 번째 알려진 암호문의 숫자는 \\((a,c)^T\\)입니다. 즉 a와 c를 바로 알 수 있습니다.
- BD=(1,3)ᵀ이므로 두 번째 암호문의 숫자는 \\((a+3b,c+3d)^T\\pmod{26}\\)입니다.
- 따라서 \\(b=9(C_1-a)\\pmod{26}\\), \\(d=9(C_2-c)\\pmod{26}\\)로 구할 수 있습니다. 여기서 C₁, C₂는 두 번째 알려진 암호문의 첫째·둘째 숫자입니다.
- 구한 a,b,c,d를 입력하고 **행렬 확인**을 누르세요.
""")

    show_hint(3, "BA=(1,0)ᵀ이므로 첫 번째 암호문에서 행렬의 첫 번째 열을 바로 알 수 있습니다. BD=(1,3)ᵀ이므로 두 번째 열은 (두 번째 암호문 숫자 − 첫 번째 열)×9 mod 26으로 구합니다.")

    st.markdown("**추론한 키 행렬을 입력하세요** (각 숫자는 0~25)")
    m1, m2 = st.columns(2)
    with m1:
        k11 = st.number_input("첫째 행 · 첫째 열", min_value=0, max_value=25, value=0, step=1, key="matrix_k11")
        k21 = st.number_input("둘째 행 · 첫째 열", min_value=0, max_value=25, value=0, step=1, key="matrix_k21")
    with m2:
        k12 = st.number_input("첫째 행 · 둘째 열", min_value=0, max_value=25, value=0, step=1, key="matrix_k12")
        k22 = st.number_input("둘째 행 · 둘째 열", min_value=0, max_value=25, value=0, step=1, key="matrix_k22")

    if st.button("행렬 확인", key="check_matrix", use_container_width=True):
        entered = [[int(k11), int(k12)], [int(k21), int(k22)]]
        if entered == q["key"]:
            st.session_state["hill_matrix_verified"] = True
            st.success("행렬 추론 성공! 이제 이 행렬로 목표 암호문을 복호화하세요.")
        else:
            st.session_state["hill_matrix_verified"] = False
            st.session_state.score = max(0, st.session_state.score - 5)
            st.session_state.wrong[3] += 1
            st.error("아직 행렬이 맞지 않습니다. 알려진 두 쌍과 mod 26 계산을 다시 확인하세요.")

    if st.session_state.get("hill_matrix_verified", False):
        st.success("추론한 키 행렬이 맞습니다.")
        st.latex(r"K=\begin{pmatrix}%d&%d\\%d&%d\end{pmatrix}" % (q["key"][0][0], q["key"][0][1], q["key"][1][0], q["key"][1][1]))
        inv_key = matrix_mod_inverse(q["key"])
        with st.expander("🧮 목표 암호문 복호화 계산"):
            st.write("1. 키 행렬의 역행렬을 mod 26에서 구합니다.")
            st.latex(r"K^{-1}=\begin{pmatrix}%d&%d\\%d&%d\end{pmatrix}" % (inv_key[0][0], inv_key[0][1], inv_key[1][0], inv_key[1][1]))
            st.write("2. 목표 암호문을 두 글자씩 나누고, 각 글자를 숫자로 바꿉니다.")
            first_pair = q["cipher"][:2]
            cx, cy = ord(first_pair[0]) - 65, ord(first_pair[1]) - 65
            px = (inv_key[0][0] * cx + inv_key[0][1] * cy) % 26
            py = (inv_key[1][0] * cx + inv_key[1][1] * cy) % 26
            st.write(f"첫 묶음 {first_pair} → ({cx}, {cy})ᵀ")
            st.write(f"역행렬을 곱하면 ({px}, {py})ᵀ이므로 첫 두 글자는 **{ALPHABET[px]}{ALPHABET[py]}**입니다.")
            st.write("나머지 묶음에도 같은 계산을 반복하세요.")
            if len(q["word"]) % 2:
                st.caption("원래 단어가 홀수 글자여서 마지막에 붙인 X가 있을 수 있습니다. 답에는 원래 단어만 입력하세요.")
        show_hint(3, "목표 암호문을 두 글자씩 나누고, 각 숫자 벡터에 K⁻¹을 곱한 뒤 mod 26을 적용하세요.")
        answer_form(3, q["word"], f"정답입니다! {q['word']}를 복호화해 최종 관문을 통과했습니다.")
    else:
        st.info("먼저 키 행렬 네 숫자를 추론해 입력하고 확인하세요. 행렬이 맞아야 평문 답안을 제출할 수 있습니다.")

st.divider()
st.caption("정답 단어는 지정된 단어 목록에서만 선택됩니다. 각 단계의 문제는 새로 시작하거나 다음 단계로 이동할 때 무작위로 바뀝니다.")
'''
Path("/mnt/data/app.py").write_text(app_code, encoding="utf-8")
Path("/mnt/data/requirements.txt").write_text("streamlit>=1.32.0\n", encoding="utf-8")
print("Created app.py and requirements.txt")
