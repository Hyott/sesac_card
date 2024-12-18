# sesac_card
SeSac Fintechers3 - Card Recommendation Chat bot


# 카드 추천 챗봇 서비스

## 프로젝트 소개
RAG(검색-증강 생성) 기술을 활용한 **카드 추천 챗봇 서비스**를 개발하였습니다. 본 서비스는 사용자의 소비 내역과 성향을 분석하여 맞춤형 신용카드를 추천하고, 지속 가능한 카드 사용 환경을 지원합니다.

---

## 배경 및 필요성
- **신용카드 사용 증가**: 1인당 평균 사용 신용카드 개수 4.4개, 유효 카드 760개.
- **기존 추천 서비스 한계**:
  - 복잡한 지출내역 입력 방식.
  - 단조로운 추천 결과 및 챗봇의 피드백 미반영.
- **지속 가능성 문제**: 카드 플라스틱 분해에 약 1000년 소요, 유해물질 배출.

---

## 주요 기능
### 1. 맞춤형 카드 추천
- 사용자의 소비 내역 및 성향 기반 실시간 추천.
- 주요 혜택 요약 및 시각화 제공.
- 챗봇과의 대화를 통해 피드백 반영.

### 2. 데이터 분석 및 시각화
- 소비습관 분석 차트 제공.
- 지출 비율을 그래프로 시각화.

### 3. 지속 가능성 고려
- 불필요한 카드 발급 최소화로 환경 및 경제적 개선 효과.

---

## 기술 스택
- **데이터 수집**: Selenium 기반 웹 스크래핑.
- **데이터 전처리**: Regular Expression을 활용한 텍스트 분류 및 처리.
- **임베딩 및 검색**: Upstage 및 Pinecone를 사용하여 벡터 데이터 저장.
- **LLM 통합**: Langchain 기반 RAG 프로세스로 사용자와의 실시간 인터랙션 구현.
- **프론트엔드**: Streamlit을 활용한 직관적인 UI 설계.

---

## 개발 과정
1. **웹 스크래핑**
   - 카드 정보 사이트에서 주요 데이터 수집.
   - JSON 형식으로 저장 및 병합.

2. **데이터 전처리**
   - 카드 이름, 혜택, 브랜드 등 주요 항목 분류.
   - 정규표현식을 활용한 데이터 구조화.

3. **RAG 모델 구현**
   - Langchain을 활용한 질문 응답 체인 구성.
   - 사용자의 입력에 기반한 메타데이터 필터링 및 추천 카드 출력.

4. **결과 시각화**
   - 사용자의 지출 분석 결과를 백분율 그래프로 표현.
   - 추천 카드 이미지와 상세 정보 제공.

---

## 기대 효과
- **사용자 편의성 증대**:
  - 맞춤형 카드 추천 및 피드백 반영.
  - 지출 분석 결과 제공으로 소비 습관 개선.

- **환경 및 경제적 개선**:
  - 불필요한 카드 발급 최소화.
  - 데이터 기반 금융 트렌드 분석 가능.

- **차별화된 서비스**:
  - 기존 추천 서비스와 달리 실시간 응답 및 정확한 추천 제공.

---

## 향후 계획
- UI/UX 개선 및 캐시 관리 최적화.
- MyData API 활용으로 정밀도 향상.
- 체크카드 추천 서비스 추가.
- 주요 소비 카테고리 예측 모델 개발.

---

## 팀 소개
- **타임키퍼**: 김태식, 이호영
- **발표자료 작성**: 김태식, 이호영
- **기술 구현**: 서예은, 김영탁
- **커뮤니케이터**: 안효철

---

## 문의
서비스에 대한 궁금한 점이 있다면 아래 연락처로 문의해주세요.  
Email: [YourTeamEmail@example.com](mailto:YourTeamEmail@example.com)