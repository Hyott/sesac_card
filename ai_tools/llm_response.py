import streamlit as st
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_community.vectorstores import Pinecone
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import json
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts import (
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from ai_tools.example import answer_examples
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from components.user_info import user_info
from PyPDF2 import PdfReader
import pandas as pd

# 환경변수 로드
load_dotenv()

# 전역 store 딕셔너리
if "store" not in globals():
    store = {}

if "llm_initialized" not in st.session_state:
    st.session_state.llm_initialized = False  # LLM 초기화 상태 추가

# LLM 및 Embeddings 초기화
llm = ChatUpstage(model='solar-pro')
embeddings = UpstageEmbeddings(model='embedding-query')
# Pinecone DB 로드
load_vec_db = Pinecone.from_existing_index(
    index_name='sesac-card-rag4',
    embedding=embeddings
)

# 검색기 초기화
def get_retriever():
    retriever = load_vec_db.as_retriever(search_kwargs={"k": 3})
    return retriever

def search_query(query, filter):
    search_results = load_vec_db.similarity_search(query, filter=filter)

    def document_to_dict(document):
        return {
            "content": document.page_content,  # Document의 내용
            "metadata": document.metadata      # Document의 메타데이터
        }
    result_as_dict = [document_to_dict(doc) for doc in search_results]
    result_json = json.dumps(result_as_dict, ensure_ascii=False, indent=4)

    return result_json



def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    각 세션의 채팅 기록을 관리하는 함수.
    """
    global store
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    
    chat_history = store[session_id]

    # 기존 기록 삭제
    chat_history.clear()
    # st.session_state.messages에 저장된 기록을 ChatMessageHistory에 반영
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_history.add_user_message(msg["content"])
        elif msg["role"] == "assistant":
            chat_history.add_ai_message(msg["content"])

    return chat_history

def get_history_chain():
    llm = ChatUpstage(model = 'solar-pro')
    retriever = get_retriever()
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever

def get_qa_chain(prompt_flag=False):
    llm = ChatUpstage(model = 'solar-pro')
    # 대화 기록을 고려한 검색기 생성
    history_aware_retriever = get_history_chain()

    with_excel_prompt = SystemMessagePromptTemplate.from_template("""
     당신은 다음 context를 기반으로 가장 적절한 신용카드를 추천하는 전문가입니다.
     
     먼저, [지출 내역]이 있는 경우, 분석하여 사용자의 소비 패턴과 특징을 파악해주세요.

     다음과 같은 내용을 포함하여 분석해주세요:
     - 주요 지출 카테고리와 그 비중을 반드시 "카테고리명(XX%)" 형식으로 나열해주세요.
       예시) 식비(35%), 쇼핑(25%), 교통(20%), 기타(20%)
     - 파일 내의 지출 금액을 합산한 총 지출 금액
     - 주로 어떤 업종에서 소비하는지
     - 소비 패턴의 특징 (예: 식비 위주, 쇼핑 위주, 교통비 많음 등)
     - 이러한 소비 패턴을 가진 사용자의 라이프스타일 추정
                                                                      
     그 다음, 분석한 소비 패턴을 바탕으로 가장 적합한 신용카드를 추천해주세요.
     마치 영업사원처럼 신용카드 가입욕구를 느끼도록 부드럽게 대해주세요.
     
     컨텍스트를 통해서 모든 신용카드에 대해 알고 있으며 그 이외에는 고려하지 않습니다.
     항상 카드의 이름을 통해서 어떤 카드에 대해 말하고 있는지를 명시해야 합니다.
     너무 짧지도 너무 길지도 않게 대답하되 요구사항에 따라 길이를 조절해주세요.
     혼란을 줄만한 대답은 하지 마세요. 모르면 필요한 사항에 대해서 다시 질문을 해주세요.
     
     그리고 이제 너가 참조할 [context]의 json 파일의 key에 대해 각각 설명을 해줄테니 참고해주세요:
     "card_img" : 카드의 실물 사진을 담은 url입니다.
     "name": 이 제이슨 파일이 표현하는 신용카드의 공식 대표이름입니다.
     "categories" : 이 카드가 갖고있는 혜택의 목록입니다.
     "annual_fee" : 카드이용을 위해 내야하는 연 회비입니다.
     "company": 카드를 발급한 회사의 이름입니다.
     "Monthly_spending_requirement" : 혜택을 받기위한 월별 최소실적 금액이고 단위는 한국원입니다.
     "overseas_payment" : visa, mastercard 처럼 해외 결제를 가능하게 하는 서비스의 지원 여부입니다.
                                                                 
     [context]
     {context}
     [지출 내역]
     {uploaded_file_content}
     
     위의 [context]와 지출 내역을 참고해서 다음과 같은 순서로 답변해주세요:
     1. 지출 내역 분석 결과
     2. 사용자의 추정 프로필과 라이프스타일
     3. 추천하는 카드와 그 이유
    """)


    without_excel_prompt = SystemMessagePromptTemplate.from_template("""
     당신은 다음 context를 기반으로 가장 적절한 신용카드를 추천하는 전문가입니다.
                                                                  
     마치 영업사원처럼 신용카드 가입욕구를 느끼도록 부드럽게 대해주세요.
     
     컨텍스트를 통해서 모든 신용카드에 대해 알고 있으며 그 이외에는 고려하지 않습니다.
     항상 카드의 이름을 통해서 어떤 카드에 대해 말하고 있는지를 명시해야 합니다.
     너무 짧지도 너무 길지도 않게 대답하되 요구사항에 따라 길이를 조절해주세요.
     혼란을 줄만한 대답은 하지 마세요. 모르면 필요한 사항에 대해서 다시 질문을 해주세요.
     
     그리고 이제 너가 참조할 [context]의 json 파일의 key에 대해 각각 설명을 해줄테니 참고해주세요:
     "card_img" : 카드의 실물 사진을 담은 url입니다.
     "name": 이 제이슨 파일이 표현하는 신용카드의 공식 대표이름입니다.
     "categories" : 이 카드가 갖고있는 혜택의 목록입니다.
     "annual_fee" : 카드이용을 위해 내야하는 연 회비입니다.
     "company": 카드를 발급한 회사의 이름입니다.
     "Monthly_spending_requirement" : 혜택을 받기위한 월별 최소실적 금액이고 단위는 한국원입니다.
     "overseas_payment" : visa, mastercard 처럼 해외 결제를 가능하게 하는 서비스의 지원 여부입니다.
                                                                 
     [context]
     {context}
     
     위의 [context]와 지출 내역을 참고해서 다음과 같은 순서로 답변해주세요:
     1. 추천하는 카드와 그 이유
     2. 혜택과 유의사항
                                                                     
    """)

    if prompt_flag:
        qa_system_prompt = with_excel_prompt
    else:
        qa_system_prompt = without_excel_prompt

    example_prompt = ChatPromptTemplate.from_messages(
    [
        ('human', '{input}'), 
        ('ai', '{answer}')
    ]
    )   

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        examples=answer_examples,
        example_prompt=example_prompt,
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            qa_system_prompt,
            few_shot_prompt,
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    # 질문-답변 체인 생성
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
        session_id_key="configurable.session_id",
    ).pick('answer')

    return conversational_rag_chain


def process_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None
        
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_extension == 'xlsx':
            # Excel 파일 처리
            df = pd.read_excel(uploaded_file)
            return df.to_dict()
        
        elif file_extension == 'pdf':
            # PDF 파일 처리
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
            
    except Exception as e:
        st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
        return None


def get_llm_response(user_input, session_id, filter=None):
    prompt_flag = False
    file_content = None
    
    if st.session_state.get('uploaded_file', None):
        uploaded_file_content = st.session_state.get('uploaded_file', None)
        file_content = process_uploaded_file(uploaded_file_content)
    if file_content:
        prompt_flag = True
    else:
        prompt_flag = False
    
    search_card_json = search_query(user_input, filter)
    qa_retriever = get_qa_chain(prompt_flag=prompt_flag)

    for chunk in qa_retriever.stream(
        {"input": user_input, 'context': search_card_json,
         'uploaded_file_content': file_content},  # 사용자 정보 추가
        config={"session_id": session_id},
    ):
        yield chunk

