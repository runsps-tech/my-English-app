import streamlit as st

# 1. 앱 제목 설정
st.title("English Friend AI 🎓")
st.subheader("영어 실력 진단 테스트")

# 2. 사용자 정보 입력
name = st.text_input("당신의 이름을 입력해주세요:")

if name:
    st.write(f"반가워요, {name}님! 어떤 부분을 가장 연습하고 싶으신가요?")
    
    # 3. 실력 체크 질문 (간단한 예시)
    interest = st.selectbox("가장 관심 있는 주제를 골라주세요:", 
                           ["일상 생활", "여행", "비즈니스", "음식과 취미"])
    
    st.write(f"좋아요! {interest} 주제로 간단한 대화를 시작해볼까요?")
    
    # 4. 테스트 시작 버튼
    if st.button("테스트 시작하기"):
        st.info("AI가 당신의 답변을 분석하고 약점을 알려드릴 거예요.")
        # 여기서 실제 대화 로직이 이어집니다.
