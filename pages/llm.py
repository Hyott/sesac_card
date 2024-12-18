# pages/llm.py
import streamlit as st
from components.markdown_func import markdown
import uuid
from ai_tools.llm_response import get_llm_response

# "홈으로 가기" 버튼을 추가하여 홈 페이지로 돌아가도록
col_title, _, col_home = st.columns([6, 1, 1])
markdown()
with col_title:
    st.title("카드 추천 챗봇")
with col_home:
    if st.button('🏠 홈으로 가기', help='홈으로 가기'):
        st.session_state.messages = []  # 챗봇 메시지 초기화
        st.switch_page("run.py")

st.markdown("안녕하세요! 카드에 대해서 궁금한 내용이 있으시면 챗봇을 통해 해결해드립니다!")
# st.write("이 페이지는 카드 추천 챗봇이 구현될 예정입니다. 진행 중인 작업이므로 추후 업데이트를 확인해주세요.")

if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []  # 채팅 기록
    st.session_state.stream_buffer = ""  # 스트림 데이터 버퍼

# 기존 메시지 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
    

# 사용자 입력 처리
if user_input := st.chat_input("채팅을 입력해주세요."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    # 비동기 스트림으로 LLM 응답 생성
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        session_id = st.session_state.session_id
        # 로딩 메시지 표시
        with st.spinner("답변을 생성 중입니다. 잠시만 기다려주세요."):
            for chunk in get_llm_response(user_input, session_id):
                st.session_state.stream_buffer += chunk
                response_placeholder.write(st.session_state.stream_buffer)
    # 전체 응답 저장
    st.session_state.messages.append(
        {"role": "assistant", "content": st.session_state.stream_buffer}
    )
    st.session_state.stream_buffer = ""  # 스트림 버퍼 초기화
   
markdown()