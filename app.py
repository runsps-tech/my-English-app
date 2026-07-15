import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

# 1. Streamlit 비밀 금고(Secrets)에서 구글 제미나이 API 키 가져오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API Key를 찾을 수 없습니다. Streamlit Cloud의 Secrets 설정을 확인해 주세요!")
    st.stop()

# 2. 스마트폰 앱 스타일 설정 및 제목 구성
st.set_page_config(page_title="English Friend AI", page_icon="🎓", layout="centered")
st.title("English Friend AI 🎓")
st.write("나에게 딱 맞춘 상황별 영어 회화 & 진단 파트너!")

# 3. 대화 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "persona" not in st.session_state:
    st.session_state.persona = ""
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

# 4. 앱 설정 영역 (이름 입력)
name = st.text_input("당신의 이름을 입력해주세요:", value="Logan")

# 5. 대화 대상 선택 (직접 입력 항목 추가!)
theme_option = st.selectbox(
    "어떤 상대와 대화하며 배우고 싶으신가요?",
    [
        "또래 친구와 캐주얼한 대화 (Liam)",
        "직장 상사/격식 있는 어른과의 대화 (Mr. Smith)",
        "8살 조카와 재미있는 대화 (Lily)",
        "병원 진료실에서 의사와의 대화 (Dr. Jones)",
        "✍️ 내가 원하는 상대 직접 입력하기"
    ]
)

# 직접 입력하기를 선택했을 때만 나타나는 비밀 입력창
custom_persona = ""
if theme_option == "✍️ 내가 원하는 상대 직접 입력하기":
    custom_persona = st.text_input(
        "대화하고 싶은 상대방이나 구체적인 상황을 적어주세요:",
        placeholder="예: 스타벅스 점원, 호텔 프론트 직원, 친절한 길거리 행인 등"
    )

# 6. 테마에 따른 AI 페르소나 지침서(System Prompt) 구성
personas = {
    "또래 친구와 캐주얼한 대화 (Liam)": (
        f"너는 유저의 친절하고 친근한 동갑내기 미국인 친구 'Liam'이야. "
        f"유저의 이름은 {name}이야. 대화할 때 영어 슬랭이나 구어체('Hey', 'What's up?', 'cool')를 섞어 아주 편하게 반말로 대화해 줘. "
        f"친구가 영어로 답하면, 그 문장에서 혹시 더 자연스럽게 고쳐 쓸 수 있는 캐주얼한 표현이 있다면 부드럽고 다정하게 짚어줘."
    ),
    "직장 상사/격식 있는 어른과의 대화 (Mr. Smith)": (
        f"너는 격식 있고 예의 바른 영어를 사용하는 직장 상사 'Mr. Smith'야. "
        f"유저의 이름은 {name}이야. 정중하고 비즈니스 매너에 맞는 표현(Polite English)을 사용하여 대화를 이끌어가 줘. "
        f"유저의 영어 문장에서 격식에 어긋나거나 어색한 격식 표현이 있다면 비즈니스 팁과 함께 부드럽게 고쳐줘."
    ),
    "8살 조카와 재미있는 대화 (Lily)": (
        f"너는 호기심 많고 귀여운 8살 미국인 조카 'Lily'야. "
        f"유저의 이름은 {name}이야. 아주 쉽고 짧은 영어 단어를 사용하고, 조카답게 신나고 활발하게 질문해 줘. "
        f"유저가 어렵게 이야기하면 '그게 무슨 뜻이야 삼촌/이모?'라는 식으로 귀엽게 받아주면서, 어린이와 대화하기에 알맞은 일상 표현 꿀팁을 전해줘."
    ),
    "병원 진료실에서 의사와의 대화 (Dr. Jones)": (
        f"너는 친절한 병원 내과 의사 'Dr. Jones'야. "
        f"유저의 이름은 {name}이야. 어디가 아파서 병원에 왔는지 상냥하게 물어보고, 의료 및 건강 관련 대화를 친절하게 이끌어줘. "
        f"유저가 증상을 영어로 표현할 때, 의사소통을 더 원활하게 해줄 증상 묘사 표현이나 유용한 서바이벌 메디컬 어휘를 교정해 줘."
    )
}

# 직접 입력한 페르소나 설정 적용
if theme_option == "✍️ 내가 원하는 상대 직접 입력하기" and custom_persona:
    chosen_persona = (
        f"너는 유저가 지정한 역할인 '{custom_persona}'이야. 유저의 이름은 {name}이야. "
        f"이 상황과 역할에 완벽하게 몰입해서 영어로 대화를 이끌어가 줘. "
        f"대화 중간중간 유저가 말한 영어 문장 중에서 더 자연스럽고 상황에 어울리는 표현이 있다면 다정하고 친절하게 고쳐서 알려줘."
    )
else:
    chosen_persona = personas.get(theme_option, "")

# 7. 대화 시작 버튼
if st.button("AI 친구와 대화 시작하기"):
    if theme_option == "✍️ 내가 원하는 상대 직접 입력하기" and not custom_persona:
        st.warning("대화하고 싶은 상대를 직접 입력해 주세요!")
    else:
        st.session_state.persona = chosen_persona
        display_name = custom_persona if custom_persona else theme_option.split('(')[1].replace(')', '') if '(' in theme_option else theme_option
        st.session_state.chat_history = [
            {"role": "assistant", "content": f"Hi {name}! I am ready to talk to you as a {display_name}. Let's start! 😊"}
        ]
        st.rerun()

# 8. 대화창 및 음성인식 마이크 구현
if st.session_state.chat_history:
    st.divider()
    display_title = custom_persona if custom_persona else theme_option
    st.subheader(f"💬 {display_title} 대화방")

    # 대화 기록 띄워주기
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    st.write("---")
    st.write("🎙️ **음성으로 말하려면 아래 마이크 버튼을 누르고 말씀하세요:**")
    
    # 🎙️ 구글 기반 실시간 한국어/영어 음성인식 마이크 탑재!
    # 스마트폰에서도 마이크 권한 동의만 하면 목소리를 영어 텍스트로 즉시 변환해 줍니다.
    voice_text = speech_to_text(
        start_prompt="🔴 마이크 켜기 (말하기 시작)",
        stop_prompt="🟢 마이크 끄기 (입력 완료)",
        language='en-US', # 영어로 말하면 텍스트로 자동 전환
        use_container_width=True,
        key='speech_input'
    )

    # 텍스트 수동 입력창도 기본 배치
    manual_input = st.chat_input("여기에 직접 키보드로 답변을 작성하셔도 됩니다:")

    # 음성 입력 혹은 텍스트 입력이 감지되었을 때 작동할 변수 선택
    user_message = ""
    if voice_text:
        user_message = voice_text
    elif manual_input:
        user_message = manual_input

    # 사용자의 입력(말 또는 타이핑) 처리하기
    if user_message:
        # 1) 유저 메시지 화면에 띄우기 및 대화 기록에 저장
        with st.chat_message("user"):
            st.write(user_message)
        st.session_state.chat_history.append({"role": "user", "content": user_message})

        # 2) AI 답변 생성 요청 (제미나이 호출)
        with st.chat_message("assistant"):
            with st.spinner("AI가 당신의 말을 듣고 생각하는 중..."):
                try:
                    model = genai.GenerativeModel(
                        model_name="gemini-2.5-flash-latest",
                        system_instruction=st.session_state.persona
                    )
                    chat = model.start_chat(history=[])
                    
                    full_prompt = "이전 대화 기록:\n"
                    for msg in st.session_state.chat_history[:-1]:
                        full_prompt += f"{msg['role']}: {msg['content']}\n"
                    full_prompt += f"\n방금 유저가 한 말: {user_message}\n\n위 설정에 맞춰 대답하고, 틀린 표현이 있다면 부드럽게 고쳐줘."

                    response = chat.send_message(full_prompt)
                    ai_response = response.text
                    
                    st.write(ai_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
