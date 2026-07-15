import streamlit as st
import google.generativeai as genai

# 1. Streamlit 비밀 금고(Secrets)에서 구글 제미나이 API 키 가져오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API Key를 찾을 수 없습니다. Streamlit Cloud의 Secrets 설정을 확인해 주세요!")
    st.stop()

# 2. 스마트폰 앱처럼 보이도록 설정 및 제목 구성
st.set_page_config(page_title="English Friend AI", page_icon="🎓", layout="centered")
st.title("English Friend AI 🎓")
st.write("나에게 딱 맞춘 상황별 영어 회화 & 진단 파트너!")

# 3. 대화 세션 상태 초기화 (대화 기록 기억용)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "persona" not in st.session_state:
    st.session_state.persona = ""

# 4. 앱 설정 영역 (이름 및 대화 대상 선택)
name = st.text_input("당신의 이름을 입력해주세요:", value="Logan")

# 배우고 싶은 다양한 대화 테마 설정
theme = st.selectbox(
    "어떤 상대와 대화하며 배우고 싶으신가요?",
    [
        "또래 친구와 캐주얼한 대화 (Liam)",
        "직장 상사/격식 있는 어른과의 대화 (Mr. Smith)",
        "8살 조카와 재미있는 대화 (Lily)",
        "병원 진료실에서 의사와의 대화 (Dr. Jones)"
    ]
)

# 5. 테마에 따른 AI 페르소나 지침서(System Prompt) 작성
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

# 6. 대화 시작 버튼
if st.button("AI 친구와 대화 시작하기"):
    st.session_state.persona = personas[theme]
    # 대화 초기화
    st.session_state.chat_history = [
        {"role": "assistant", "content": f"Hi {name}! Let's start our conversation! 😊"}
    ]
    st.rerun()

# 7. 대화창 구현
if st.session_state.chat_history:
    st.divider()
    st.subheader(f"💬 {theme.split('(')[1].replace(')', '')}님과의 대화방")

    # 대화 기록 띄워주기
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # 사용자 입력 받기
    if user_input := st.chat_input("여기에 영어로 답변을 작성해 보세요:"):
        # 1) 유저 메시지 띄우기 및 저장
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # 2) AI 답변 생성 요청 (제미나이 호출)
        with st.chat_message("assistant"):
            with st.spinner("AI 친구가 생각하는 중..."):
                try:
                    # 제미나이 최신 가성비 모델(gemini-1.5-flash) 사용
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction=st.session_state.persona
                    )
                    
                    # 이전 대화 기록을 프롬프트에 녹여서 자연스럽게 문맥을 유지하게 함
                    chat = model.start_chat(history=[])
                    
                    # 지금까지 나눈 대화 맥락을 제미나이가 이해할 수 있게 전달
                    full_prompt = "이전 대화 기록:\n"
                    for msg in st.session_state.chat_history[:-1]:
                        full_prompt += f"{msg['role']}: {msg['content']}\n"
                    full_prompt += f"\n방금 유저가 한 말: {user_input}\n\n위의 너의 페르소나 설정에 맞추어 친절하게 리액션해주고, 질문을 던져 대화를 이어가며, 필요하다면 방금 유저의 말 중에서 다정하게 피드백을 적어줘."

                    response = chat.send_message(full_prompt)
                    ai_response = response.text
                    
                    st.write(ai_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
