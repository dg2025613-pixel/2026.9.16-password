import random
import streamlit as st

# =========================================================
# 1. 기본 설정: 정답으로 사용할 단어 목록
#    이 목록에 있는 단어만 정답으로 출제됩니다.
# =========================================================
WORD_BANK = [
    "APPLE", "GRAPE", "BRAIN", "PLANT", "DREAM",
    "LIGHT", "MUSIC", "WATER", "HOUSE", "SMILE",
    "CLOUD", "TRAIN", "EARTH", "HEART", "STONE",
    "RIVER", "SPACE", "NIGHT", "SUGAR", "BEACH",
    "TIGER", "ZEBRA", "CHAIR", "PAPER", "PHONE",
    "MOUSE", "GREEN", "BLACK", "WHITE", "BREAD",
]

# 단어 목록이 모두 4~5글자인지 확인
WORD_BANK = [word.strip().upper() for word in WORD_BANK
             if word.strip().isalpha() and 4 <= len(word.strip()) <= 5]

STAGES = {
    1: {
        "name": "1단계 · 시저 암호",
        "short": "시저 암호",
        "description": "알파벳을 일정한 칸 수만큼 이동시켜 암호화하는 방법입니다.",
        "howto": "암호문을 풀 때는 암호화할 때 이동한 칸 수만큼 알파벳을 반대 방향으로 이동하세요.",
        "example": "예: 암호화할 때 3칸 오른쪽으로 이동했다면, 복호화할 때는 3칸 왼쪽으로 이동합니다.",
        "hint": "알파벳을 왼쪽으로 몇 칸 이동해야 원래 단어가 되는지 생각해 보세요.",
    },
    2: {
        "name": "2단계 · 아트바시 암호",
        "short": "아트바시 암호",
        "description": "알파벳 순서를 반대로 대응시키는 암호입니다.",
        "howto": "A는 Z, B는 Y, C는 X처럼 알파벳의 양 끝을 서로 바꾸면 됩니다.",
        "example": "예: A ↔ Z, B ↔ Y, C ↔ X, D ↔ W",
        "hint": "알파벳 순서에서 반대편에 있는 글자를 찾아보세요. A와 Z의 위치를 떠올리면 쉽습니다.",
    },
    3: {
        "name": "3단계 · 전치 암호",
        "short": "전치 암호",
        "description": "글자 자체는 바꾸지 않고, 글자의 순서만 바꾸는 암호입니다.",
        "howto": "암호문에 있는 글자들을 살펴보고, 섞인 순서를 되돌려 원래 단어를 찾아보세요.",
        "example": "예: STOP의 글자 순서를 바꾸면 POTS처럼 만들 수 있습니다.",
        "hint": "암호문에 포함된 글자는 정답에도 그대로 들어 있습니다. 글자 배열을 바꿔 보세요.",
    },
}


def caesar_encrypt(word: str, shift: int) -> str:
    result = []
    for char in word:
        if "A" <= char <= "Z":
            result.append(chr((ord(char) - ord("A") + shift) % 26 + ord("A")))
        else:
            result.append(char)
    return "".join(result)


def atbash_encrypt(word: str) -> str:
    return "".join(chr(ord("Z") - (ord(char) - ord("A"))) for char in word)


def transposition_encrypt(word: str, permutation: list[int]) -> str:
    return "".join(word[i] for i in permutation)


def make_question(stage: int, used_words: set[str]) -> dict:
    # 가능하면 아직 사용하지 않은 단어를 우선 사용합니다.
    available = [word for word in WORD_BANK if word not in used_words]
    if not available:
        available = WORD_BANK[:]

    answer = random.choice(available)

    if stage == 1:
        shift = random.randint(1, 25)
        cipher = caesar_encrypt(answer, shift)
        while cipher == answer:
            shift = random.randint(1, 25)
            cipher = caesar_encrypt(answer, shift)
        return {
            "answer": answer,
            "ciphertext": cipher,
            "key": shift,
            "explanation": (
                f"이 문제는 시저 암호입니다. 암호화할 때 각 글자를 오른쪽으로 "
                f"{shift}칸 이동했습니다. 따라서 복호화할 때는 각 글자를 왼쪽으로 "
                f"{shift}칸 이동하면 됩니다."
            ),
        }

    if stage == 2:
        cipher = atbash_encrypt(answer)
        return {
            "answer": answer,
            "ciphertext": cipher,
            "key": None,
            "explanation": (
                "아트바시 암호는 알파벳을 반대로 대응시킵니다. "
                "A↔Z, B↔Y, C↔X처럼 바꾸어 암호문을 복호화할 수 있습니다."
            ),
        }

    # 3단계: 전치 암호. 암호문이 원래 단어와 달라지도록 순서를 섞습니다.
    indexes = list(range(len(answer)))
    random.shuffle(indexes)
    attempts = 0
    while transposition_encrypt(answer, indexes) == answer and attempts < 20:
        random.shuffle(indexes)
        attempts += 1

    cipher = transposition_encrypt(answer, indexes)
    # 중복 글자 등으로 순서를 섞어도 똑같아지는 경우를 대비한 안전장치
    if cipher == answer:
        cipher = answer[1:] + answer[:1]

    return {
        "answer": answer,
        "ciphertext": cipher,
        "key": indexes,
        "explanation": (
            "이 문제는 전치 암호입니다. 글자 자체는 바뀌지 않고 순서만 섞였습니다. "
            "암호문에 있는 글자들을 다시 배열해 영어 단어를 찾아보세요."
        ),
    }


def reset_stage_question(stage: int):
    used = st.session_state.used_words
    question = make_question(stage, used)
    st.session_state.questions[stage] = question
    st.session_state.answers[stage] = ""
    st.session_state.checked[stage] = False
    st.session_state.revealed[stage] = False


st.set_page_config(
    page_title="암호문 해독 연구소",
    page_icon="🔐",
    layout="centered",
)

# 밝고 읽기 쉬운 화면
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f5f9ff 0%, #ffffff 70%);
        color: #182338;
    }
    [data-testid="stHeader"] { background: rgba(255,255,255,0.8); }
    .main .block-container {
        max-width: 850px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3, p, label, li { color: #182338 !important; }
    .hero {
        background: linear-gradient(135deg, #e5efff, #f0eaff);
        border: 1px solid #d7e3fa;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .hero h1 { margin: 0 0 8px 0; font-size: 2rem; }
    .hero p { margin: 0; color: #3f506c !important; }
    .cipher-card {
        background: #ffffff;
        border: 1px solid #d9e3f0;
        border-radius: 18px;
        padding: 22px;
        text-align: center;
        box-shadow: 0 5px 18px rgba(38, 63, 99, 0.06);
        margin: 12px 0 18px 0;
    }
    .cipher-label {
        color: #5b6b83;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .cipher-word {
        color: #173b78;
        font-size: 2.5rem;
        letter-spacing: 0.28rem;
        font-weight: 800;
        overflow-wrap: anywhere;
    }
    .info-card {
        background: #f2f7ff;
        border-left: 5px solid #5288e8;
        border-radius: 10px;
        padding: 14px 16px;
        margin: 10px 0;
    }
    .small-muted { color: #596981 !important; font-size: 0.92rem; }
    div.stButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 2.7rem;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 10px;
        font-size: 1.05rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "current_stage" not in st.session_state:
    st.session_state.current_stage = 1
    st.session_state.completed = set()
    st.session_state.used_words = set()
    st.session_state.questions = {}
    st.session_state.answers = {1: "", 2: "", 3: ""}
    st.session_state.checked = {1: False, 2: False, 3: False}
    st.session_state.revealed = {1: False, 2: False, 3: False}
    reset_stage_question(1)

st.markdown(
    """
    <div class="hero">
      <h1>🔐 암호문 해독 연구소</h1>
      <p>세 가지 암호 규칙을 배우고, 짧은 영어 단어 암호를 풀어 보세요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### 진행 상황")
progress = len(st.session_state.completed) / 3
st.progress(progress, text=f"{len(st.session_state.completed)} / 3 단계 완료")

stage_cols = st.columns(3)
for idx, col in enumerate(stage_cols, start=1):
    with col:
        if idx in st.session_state.completed:
            st.success(f"✓ {idx}단계 완료")
        elif idx == st.session_state.current_stage:
            st.info(f"▶ {idx}단계 진행 중")
        else:
            st.caption(f"🔒 {idx}단계")

stage = st.session_state.current_stage
stage_info = STAGES[stage]
question = st.session_state.questions[stage]

st.divider()
st.markdown(f"## {stage_info['name']}")
st.write(stage_info["description"])

with st.expander("📘 암호 규칙과 풀이 방법", expanded=True):
    st.write(stage_info["howto"])
    st.info(stage_info["example"])

st.markdown(
    f"""
    <div class="cipher-card">
      <div class="cipher-label">해독할 암호문</div>
      <div class="cipher-word">{question['ciphertext']}</div>
      <div class="small-muted">영어 대문자 · {len(question['ciphertext'])}글자</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("💡 힌트 보기"):
    st.write(stage_info["hint"])

with st.form(key=f"answer_form_{stage}"):
    user_answer = st.text_input(
        "정답 영어 단어를 입력하세요",
        value=st.session_state.answers[stage],
        placeholder="예: APPLE",
        max_chars=5,
        help="영어 단어 4~5글자를 입력하세요.",
    )
    submitted = st.form_submit_button("정답 확인", use_container_width=True)

if submitted:
    normalized = user_answer.strip().upper()
    st.session_state.answers[stage] = normalized
    st.session_state.checked[stage] = True
    if normalized == question["answer"]:
        st.session_state.completed.add(stage)
        st.session_state.used_words.add(question["answer"])
        st.success("정답입니다! 🎉 단계를 완료했어요.")
    else:
        st.error("아직 정답이 아니에요. 암호 규칙과 힌트를 다시 확인해 보세요.")

if st.session_state.checked[stage] and st.session_state.answers[stage] != question["answer"]:
    st.caption("원하는 만큼 다시 시도할 수 있어요.")

left, right = st.columns(2)
with left:
    if st.button("정답과 풀이 보기", use_container_width=True, key=f"reveal_{stage}"):
        st.session_state.revealed[stage] = True
with right:
    if st.button("새 문제로 바꾸기", use_container_width=True, key=f"new_{stage}"):
        reset_stage_question(stage)
        st.rerun()

if st.session_state.revealed[stage]:
    st.warning(f"정답: **{question['answer']}**")
    st.write(question["explanation"])
    if stage == 1:
        st.write(f"복호화 방법: 각 글자를 왼쪽으로 {question['key']}칸 이동합니다.")
    elif stage == 2:
        st.write("각 글자를 알파벳의 반대편 글자로 바꾸면 됩니다.")
    else:
        st.write("암호문에 포함된 글자를 원래 영어 단어가 되도록 재배열합니다.")

if stage in st.session_state.completed:
    st.divider()
    if stage < 3:
        if st.button("다음 단계로 이동 →", type="primary", use_container_width=True):
            next_stage = stage + 1
            st.session_state.current_stage = next_stage
            if next_stage not in st.session_state.questions:
                reset_stage_question(next_stage)
            st.rerun()
    else:
        st.balloons()
        st.success("축하합니다! 3단계를 모두 완료했어요.")
        if st.button("처음부터 다시 도전하기", type="primary", use_container_width=True):
            for key in [
                "current_stage", "completed", "used_words",
                "questions", "answers", "checked", "revealed"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

with st.expander("⚙️ 내가 설정한 정답 단어 목록"):
    st.write("문제의 정답은 아래 목록에 있는 단어에서만 선택됩니다.")
    st.code(", ".join(WORD_BANK), language="text")
    st.caption("단어를 추가하거나 바꾸려면 app.py 위쪽의 WORD_BANK 목록을 수정하세요.")

st.caption("학습용 암호 퍼즐 · 정답 단어는 WORD_BANK 목록에서만 출제됩니다.")
