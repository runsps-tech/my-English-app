import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import speech_to_text

# 1. API 키 및 클라이언트 설정
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
except Exception as e:
    st.error("API Key를 찾을 수 없습니다. Secrets 설정을 확인해 주세요!")
    st.stop()

st.set_page_config(page_title="Custom English Academy", page_icon="🏫", layout="centered")
st.title("🏫 Logan 전용 맞춤형 영어 아카데미")

# 2. 세션 상태 초기화 (앱의 기억 장치)
if "app_stage" not in st.session_state:
    st.session_state.app_stage = "LOGIN"  # STAGES: LOGIN -> TEST -> ANALYSIS -> STUDY_SETTING -> MAIN_STUDY
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "test_step" not in st.session_state:
    st.session_state.test_step = 1
if "test_answers" not in st.session_state:
    st.session_state.test_answers = {}
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""
if "study_mode" not in st.session_state:
    st.session_state.study_mode = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "custom_request" not in st.session_state:
    st.session_state.custom_request = ""
if "selected_level" not in st.session_state:
    st.session_state.selected_level = "기초 레벨 (유치원 스타일)"

# --- STAGE 1: 로그인 (이름 입력) ---
if st.session_state.app_stage == "LOGIN":
    st.subheader("👋 안녕하세요! 학습을 시작하기 위해 이름을 입력해주세요.")
    name_input = st.text_input("당신의 이름:", value="Logan")
    if st.button("회원가입 및 레벨 테스트 시작하기 🚀"):
        if name_input.strip():
            st.session_state.user_name = name_input
            st.session_state.app_stage = "TEST"
            st.rerun()

# --- STAGE 2: 필수 레벨 테스트 (단어, 영작, 스피킹) ---
elif st.session_state.app_stage == "TEST":
    st.subheader(f"📝 {st.session_state.user_name}님의 실력 진단 테스트 (필수 고스)")
    st.progress(st.session_state.test_step / 3)

    if st.session_state.test_step == 1:
        st.markdown("**[1단계: 단어 테스트]** 아래 한글에 맞는 올바른 영어 단어를 주관식으로 적어주세요.")
        st.write("문제: '결정하다, 결심하다' (ㄷ으로 시작하는 6글자 단어)")
        ans1 = st.text_input("당신의 답변:", key="ans1")
        if st.button("다음 단계로 이동 ➡️"):
            st.session_state.test_answers["word"] = ans1
            st.session_state.test_step = 2
            st.rerun()

    elif st.session_state.test_step == 2:
        st.markdown("**[2단계: 영작 테스트]** 다음 문장을 영어로 바꾸어 보세요.")
        st.write("문제: '나는 어제 친구와 함께 저녁을 먹었다.'")
        ans2 = st.text_input("당신의 답변:", key="ans2")
        if st.button("다음 단계로 이동 ➡️"):
            st.session_state.test_answers["writing"] = ans2
            st.session_state.test_step = 3
            st.rerun()

    elif st.session_state.test_step == 3:
        st.markdown("**[3단계: 스피킹 테스트]** 아래 문장을 소리 내어 읽거나, 아는 대로 영어로 말해보세요.")
        st.write("지문: 'Nice to meet you. I want to improve my English speaking.'")
        
        # 반복 버그 차단을 위해 대화 전용 변수로 분리
        v_text = speech_to_text(start_prompt="🎤 누르고 녹음 시작", stop_prompt="⏹️ 녹음 완료", language='en-US', key='test_speech')
        if v_text:
            st.success(f"인식된 목소리: {v_text}")
            st.session_state.test_answers["speaking"] = v_text
        
        # 주관식 텍스트 입력도 허용
        t_text = st.text_input("말하기 대신 텍스트로 입력하셔도 됩니다:")
        if t_text:
            st.session_state.test_answers["speaking"] = t_text

        if st.button("테스트 완료 및 AI 분석 요청 📊"):
            st.session_state.app_stage = "ANALYSIS"
            st.rerun()

# --- STAGE 3: AI 분석 및 결과 레포트 ---
elif st.session_state.app_stage == "ANALYSIS":
    st.subheader("📊 AI 맞춤 실력 진단 결과")
    
    if not st.session_state.analysis_result:
        with st.spinner("Logan님의 답변을 분석하여 맞춤형 성적표를 생성 중입니다..."):
            prompt = f"""
            유저 이름: {st.session_state.user_name}
            [유저의 테스트 답변]
            1. 단어(결정하다): {st.session_state.test_answers.get('word')}
            2. 영작(어제 친구와 저녁): {st.session_state.test_answers.get('writing')}
            3. 스피킹/표현: {st.session_state.test_answers.get('speaking')}
            
            위 답변을 바탕으로 유저의 현재 영어 레벨(초급/중급/상급)을 진단하고, 강점과 보완점을 한국어로 다정하게 분석해줘.
            """
            resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            st.session_state.analysis_result = resp.choices[0].message.content
    
    st.write(st.session_state.analysis_result)
    st.divider()
    
    if st.button("나의 학습 환경 설정하러 가기 ⚙️"):
        st.session_state.app_stage = "STUDY_SETTING"
        st.rerun()

# --- STAGE 4: 유저 요구사항 입력 및 공부 방법 선택 ---
elif st.session_state.app_stage == "STUDY_SETTING":
    st.subheader("⚙️ Logan님을 위한 맞춤형 학습 설계")
    
    st.markdown("**1. 원하시는 공부 방식을 선택해 주세요.**")
    mode = st.radio("학습 모드 선택:", ["✍️ 글로 공부 (텍스트 중심 피드백 수업)", "🎙️ 스피킹 공부 (리액션과 말하기 중심 수업)"])
    
    st.markdown("**2. AI 선생님의 조정 레벨을 선택해 주세요.**")
    level = st.selectbox("레벨 조정:", ["기초 레벨 (영어유치원 스타일 - 천천히 반복)", "비즈니스 기초 레벨", "자유로운 일상 대화 레벨"])
    
    st.markdown("**3. AI 선생님에게 추가로 요구하고 싶은 사항을 적어주세요.**")
    req = st.text_area("추가 요구사항:", placeholder="예: 무조건 한글로 먼저 친절하게 설명해주고 영어 문장은 단어별로 쪼개서 천천히 3번씩 반복해줘!")
    
    if st.button("설정 완료! 수업방 입장하기 🎒"):
        st.session_state.study_mode = mode
        st.session_state.selected_level = level
        st.session_state.custom_request = req
        
        # 수업 메인 지침 설계
        st.session_state.persona = f"""
        너는 {st.session_state.user_name}님의 전용 개인 인공지능 영어 교사야.
        현재 설정된 학습 모드: {mode}
        설정된 레벨: {level}
        유저의 특별 요구사항: {req}
        
        [교수법 필수 지침]
        1. 유저가 말을 걸면 무조건 칭찬을 먼저 해주고, 어색한 부분을 '영어유치원 선생님처럼 한글로' 쉽고 다정하게 교정해줘.
        2. 추천 영어 문장은 반드시 천천히 따라할 수 있도록 단어를 쪼개서 강조해주고 여러 번 반복해줘. (예: 'Let's... study... English!')
        3. 마지막에는 유저가 쉽게 단답형이나 짧은 문장으로도 대답할 수 있는 질문을 던져줘.
        """
        st.session_state.chat_history = [
            {"role": "assistant", "content": f"반가워요 {st.session_state.user_name}님! 설정을 바탕으로 한 맞춤형 {mode} 수업방이 개설되었습니다. 선생님과 즐겁게 대화를 시작해 볼까요? 궁금한 점을 치시거나 인사를 건네주세요! 😊"}
        ]
        st.session_state.app_stage = "MAIN_STUDY"
        st.rerun()

# --- STAGE 5: 본격 맞춤형 대화 수업방 ---
elif st.session_state.app_stage == "MAIN_STUDY":
    st.subheader(f"💬 {st.session_state.user_name}님의 {st.session_state.study_mode}방")
    st.caption(f"현재 레벨: {st.session_state.selected_level} | 요구사항 반영 완료 ✨")

    # 대화창 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    st.write("---")
    
    # 입력 수단 결정 및 반복 버그 차단 로직
    user_msg = ""
    
    # 1. 글로 공부 모드 -> 키보드 창을 메인으로 노출
    if "글로 공부" in st.session_state.study_mode:
        txt_input = st.chat_input("선생님께 글로 답변하기:")
        if txt_input:
            user_msg = txt_input
            
    # 2. 스피킹 공부 모드 -> 마이크를 상단에 배치
    else:
        st.write("🎙️ **말씀하시려면 아래 마이크 버튼을 한 번 터치하고 말씀하세요:**")
        # 중복 전송 버그를 막기 위해 별도의 유니크 키 부여
        voice_data = speech_to_text(start_prompt="🔴 마이크 켜기 (말하기)", stop_prompt="🟢 말하기 완료", language='en-US', key='main_study_speech')
        if voice_data:
            user_msg = voice_data
        
        txt_backup = st.chat_input("스피킹 모드 중에도 필요한 경우 타이핑으로 답변 가능합니다:")
        if txt_backup:
            user_msg = txt_backup

    # 메시지 처리 및 AI 답변 생성
    if user_msg:
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        
        with st.chat_message("assistant"):
            with st.spinner("선생님이 다정한 피드백을 준비하고 있어요... 💭"):
                try:
                    messages = [{"role": "system", "content": st.session_state.persona}]
                    for m in st.session_state.chat_history:
                        messages.append({"role": m["role"], "content": m["content"]})
                        
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages
                    )
                    ai_resp = response.choices[0].message.content
                    st.write(ai_resp)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_resp})
                    
                    # ⭐ 무한반복 버그 방지 처리를 마친 후 화면 리프레시
                    st.rerun()
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
