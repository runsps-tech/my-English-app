import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import speech_to_text

# 1. Streamlit 비밀 금고(Secrets)에서 Groq API 키 가져오기
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )
except Exception as e:
    st.error("API Key를 찾을 수 없습니다. Streamlit Cloud의 Secrets 설정을 확인해 주세요!")
    st.stop()

# 2. 스마트폰 앱 스타일 설정 및 제목 구성
st.set_page_config(page_title="Kindergarten English Friend", page_icon="🧸", layout="centered")
st.title("🧸 다정한 영어유치원 AI 친구")
st.write("마이크 없이 텍스트로도 편하게! 천천히 친절하게 가르쳐주는 나만의 유치원 선생님")

# 3. 대화 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "persona" not in st.session_state:
    st.session_state.persona = ""

# 4. 앱 설정 영역 (이름 입력)
name = st.text_input("당신의 이름을 입력해주세요:", value="Logan")

# 5. 대화 대상 선택
theme_option = st.selectbox(
    "어떤 스타일의 선생님과 대화하고 싶으신가요?",
    [
        "칭찬 가득한 다정한 유치원 선생님 (Miss Emily)",
        "차분하고 천천히 알려주는 삼촌 같은 선생님 (Teacher Chris)",
        "재미있는 놀이 중심의 친구 같은 선생님 (Sunny)",
        "✍️ 내가 원하는 선생님 직접 만들기"
    ]
)

custom_persona = ""
if theme_option == "✍️ 내가 원하는 선생님 직접 만들기":
    custom_persona = st.text_input(
        "원하는 선생님의 성격이나 상황을 적어주세요:",
        placeholder="예: 애니메이션 캐릭터 같은 목소리, 비즈니스 기초 유치원 등"
    )

# ⭐ 핵심: 영어유치원 교수법 지침 (한글 피드백 + 영어 천천히 여러 번 반복)
kindergarten_base_instruction = (
    f"너는 영어유치원에서 아이들을 가르치는 세상에서 가장 다정하고 친근한 AI 선생님이야. 유저의 이름은 {name}이야.\n"
    f"[가장 중요한 답변 규칙]\n"
    f"1. 실시간 대화를 위해 대답은 너무 길지 않게, 아이에게 말하듯 친근하고 따뜻한 어조로 말해줘.\n"
    f"2. 유저가 영어로 문장을 말하면(텍스트나 음성 모두), 먼저 그 문장을 아주 잘했다고 듬뿍 칭찬해줘.\n"
    f"3. 혹시 어색한 표현이나 오타가 있다면, '영어유치원 선생님처럼 한글로' 다정하게 이유를 설명해주고, "
    f"가장 올바른 문장을 추천해줘.\n"
    f"4. 유저가 핵심 문장을 입으로나 글로 따라 칠 수 있도록, 추천 영어 문장을 [천천히 따라해봐요! 📢] 란에 "
    f"단어를 쪼개거나 여러 번 반복해서 강조해줘. (예: 'Let's... go... to... school! Let's go to school!')\n"
    f"5. 마지막에는 유저가 마이크 없이 텍스트로도 바로 대답할 수 있게 쉽고 직관적인 질문을 영어로 던져서 대화를 계속 이끌어줘."
)

personas = {
    "칭찬 가득한 다정한 유치원 선생님 (Miss Emily)": (
        f"{kindergarten_base_instruction}\n너의 이름은 Miss Emily야. 리액션이 엄청 풍부하고 하트와 이모티콘을 많이 쓰며 온화하게 격려해주는 스타일이야."
    ),
    "차분하고 천천히 알려주는 삼촌 같은 선생님 (Teacher Chris)": (
        f"{kindergarten_base_instruction}\n너의 이름은 Teacher Chris야. 나긋나긋하고 신뢰감을 주는 목소리 톤으로, 서두르지 않고 하나씩 꼼꼼하게 짚어주는 삼촌 같은 스타일이야."
    ),
    "재미있는 놀이 중심의 친구 같은 선생님 (Sunny)": (
        f"{kindergarten_base_instruction}\n너의 이름은 Sunny야. 에너지가 넘치고 위트가 있어서, 공부라기보다는 재미있는 퀴즈나 대화를 나누는 듯한 유쾌한 친구 스타일이야."
    )
}

if theme_option == "✍️ 내가 원하는 선생님 직접 만들기" and custom_persona:
    chosen_persona = f"{kindergarten_base_instruction}\n너의 성격 컨셉은 다음과 같아: {custom_persona}. 이 컨셉에 완벽히 몰입해서 가르쳐줘."
else:
    chosen_persona = personas.get(theme_option, "")

# 7. 대화 시작 버튼
if st.button("🧸 선생님과 대화 시작하기"):
    if theme_option == "✍️ 내가 원하는 선생님 직접 만들기" and not custom_persona:
        st.warning("선생님의 스타일을 입력해 주세요!")
    else:
        st.session_state.persona = chosen_persona
        display_name = custom_persona if custom_persona else theme_option.split('(')[1].replace(')', '') if '(' in theme_option else theme_option
        st.session_state.chat_history = [
            {"role": "assistant", "content": f"안녕 {name}! 반가워요! 오늘부터 유저님의 다정한 영어 단짝이 될 {display_name} 선생님이에요. 🥰 오늘 기분은 어떤가요? How are you today?"}
        ]
        st.rerun()

# 8. 대화창 구현
if st.session_state.chat_history:
    st.divider()
    display_title = custom_persona if custom_persona else theme_option
    st.subheader(f"💬 {display_title} 수업방")

    # 대화 기록 화면에 표시
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    st.write("---")
    
    # 💡 텍스트 입력창을 상단으로 올리고 마이크는 선택사항으로 하단 배치
    manual_input = st.chat_input("여기에 편하게 타이핑해서 선생님께 답장해 보세요 (마이크 없이 가능!):")
    
    st.write("🎙️ **목소리로 대화하고 싶을 때만 아래 마이크 버튼을 활용하세요:**")
    voice_text = speech_to_text(
        start_prompt="🔴 마이크 켜고 말하기",
        stop_prompt="🟢 말하기 완료",
        language='en-US',
        use_container_width=True,
        key='speech_input'
    )

    user_message = ""
    if manual_input:
        user_message = manual_input
    elif voice_text:
        user_message = voice_text

    if user_message:
        with st.chat_message("user"):
            st.write(user_message)
        st.session_state.chat_history.append({"role": "user", "content": user_message})

        with st.chat_message("assistant"):
            with st.spinner("선생님이 유저님의 말을 듣고 다정한 답변을 생각 중이에요... 💭"):
                try:
                    messages = [{"role": "system", "content": st.session_state.persona}]
                    for msg in st.session_state.chat_history:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                    
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages
                    )
                    ai_response = response.choices[0].message.content
                    
                    st.write(ai_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
