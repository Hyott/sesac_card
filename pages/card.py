import streamlit as st
from components.user_info import user_info
from components.card_list import card_list
from components.upload_file import upload_file
from components.markdown_func import markdown
from components.decide import decide


def choose_yes_no():
    """파일 업로드 선택과 카드 선택을 처리"""
    markdown()  # 스타일 적용
    if 'show_decision' not in st.session_state:
        st.session_state.show_decision = False

    # 필요한 세션 상태 초기화
    if 'page' not in st.session_state:
        st.session_state.page = None

    # 가계부 등 지출 내역본 가지고 있나요? 화면에서는 홈 버튼만 표시
    if st.session_state.page is None:
        col_title, col_home = st.columns([6, 1])
        
        with col_title:
            st.title("사용자 특화 카드 추천 시스템")
        
        with col_home:
            if st.button('🏠 홈으로 가기', help='홈으로 가기'):
                st.session_state.messages = []  # 챗봇 메시지 초기화
                st.session_state.result_page = False
                st.session_state.page = None  # 페이지 상태 초기화
                st.switch_page("run.py")

        st.subheader("가계부 등 지출 내역본 가지고 있나요?")

        col1, col2 = st.columns(2)
        
        # "네" 버튼을 클릭했을 때 '네' 상태로 설정하고, '아니오' 상태 초기화
        if col1.button('네'):
            st.session_state.page = '네'
            st.session_state.selected_card = None
            st.session_state.upload_file = False
            st.rerun()  # 페이지 리로드, 상태 갱신 후 새 페이지로 이동
        
        # "아니오" 버튼을 클릭했을 때 '아니오' 상태로 설정하고, '네' 상태 초기화
        if col2.button('아니오'):
            st.session_state.page = '아니오'
            st.session_state.upload_file = False
            st.rerun()  # 페이지 리로드, 상태 갱신 후 새 페이지로 이동

    # 선택된 페이지에 따른 함수 호출
    if st.session_state.page:
        display_page()

def display_page():
    """선택된 페이지의 내용을 출력하는 함수"""
    # 결과 페이지일 때 기존 '이전 페이지로 가기' 버튼 숨기기
    if st.session_state.get('result_page', False):
        # 결과는 나오되, 기존 '이전 페이지로 가기' 버튼은 숨김
        st.empty()  # 기존 내용 지우기
        decide()
        return

    # 결과 페이지가 아닐 때만 이전/홈 버튼 표시
    if not st.session_state.get('result_page', False):
        # 타이틀과 버튼을 한 줄에 배치
        col_title, col_back, col_home = st.columns([6, 1.3, 1])
        
        with col_title:
            st.title("사용자 특화 카드 추천 시스템")
        
        with col_back:
            if st.button('↩️ 이전 페이지로 가기', help='이전 페이지로 가기'):
                st.session_state.page = None
                st.rerun()
        
        with col_home:
            if st.button('🏠 홈으로 가기', help='홈으로 가기'):
                st.session_state.messages = []  # 챗봇 메시지 초기화
                st.session_state.result_page = False
                st.session_state.page = None  # 페이지 상태 초기화
                st.switch_page("run.py")

    else:
        # 결과 페이지일 때는 홈만 표시
        col_title, _, col_home = st.columns([6, 1, 1])
        with col_title:
            st.title("사용자 특화 카드 추천 시스템")

        with col_home:
            if st.button('🏠 홈으로 가기', help='홈으로 가기'):
                st.session_state.messages = []  # 챗봇 메시지 초기화
                st.session_state.result_page = False
                st.session_state.page = None  # 페이지 상태 초기화
                
                st.switch_page("run.py")

    # 페이지에 따라 다른 함수를 호출
    if st.session_state.page == '네':
        st.session_state.uploaded_file = None
        upload_file()
        
    elif st.session_state.page == '아니오':
        card_list()
        st.session_state.uploaded_file = None
        

    user_info()
    decide()

# 실행
if 'upload_file' not in st.session_state:
    st.session_state.upload_file = None

# 페이지 선택 처리
choose_yes_no()