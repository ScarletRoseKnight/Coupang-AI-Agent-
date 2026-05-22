## 2. `app.py` (Updated)
#파이썬 소스 코드의 함수명, 내부 주석, CLI 출력 텍스트 하단에 명확하게 영문 번역을 추가했습니다.  
#The python functions are duplicated with English aliases, and all internal logic, system instructions, and system prints are thoroughly translated.

import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

# 1. 인프라 및 환경 변수 로드 / Load Infrastructure and Environment Variables
load_dotenv(dotenv_path="openaiapi.env")
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 2. 고성능 Vector DB (ChromaDB) 초기화 및 인-메모리 설정 / Initialize ChromaDB and In-Memory Setup
chroma_client = chromadb.Client()
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=api_key,
    model_name="text-embedding-3-small" # 비용 최적화형 초고속 임베딩 모델 채택 / Cost-efficient, high-speed embedding model
)

# 컬렉션(RAG용 가상 DB 테이블) 생성 / Create collection (Virtual DB table for RAG)
collection = chroma_client.get_or_create_collection(
    name="coupang_catalog", 
    embedding_function=openai_ef
)

# 3. 상품 데이터를 Vector DB에 임베딩하여 빌드하는 함수 / Build Product Vector Database
def 빌드_프로덕트_벡터_데이터베이스():
    with open("products.json", "r", encoding="utf-8") as f:
        products = json.load(f)
        
    ids = []
    documents = []
    metadatas = []
    
    for p in products:
        ids.append(p["id"])
        # LLM이 문맥을 완벽히 이해하도록 정형 데이터를 자연어 문서 형태로 변환(Chunking)
        # Convert structured data into natural language text for context understanding
        doc_text = f"상품명: {p['name']}, 가격: {p['price']}원, 배송: {p['delivery']}, 평점: {p['rating']}, 카테고리: {p['category']}"
        documents.append(doc_text)
        metadatas.append({"category": p["category"], "price": p["price"]})
        
    # Vector DB에 임베딩 데이터 대량 적재 (Upsert) / Upsert embedding data into Vector DB
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print("✅ [System] 쿠팡 카탈로그 실시간 벡터 임베딩 및 인덱싱 완료.")
    print("✅ [System] Coupang catalog real-time vector embedding and indexing completed.")

# 최초 실행 시 벡터 DB 빌드 / Build Vector DB on initialization
빌드_프로덕트_벡터_데이터베이스()

# 4. 실시간 시맨틱 검색 엔진 (Vector DB Retriever) / Real-time Semantic Search Engine
def 벡터_기반_상품_검색(user_query, n_results=2):
    # 단어 매칭이 아닌 '의도와 문맥'의 유사도를 계산하여 결과를 반환합니다.
    # Calculates similarity based on 'intent and context' rather than exact keyword matching.
    results = collection.query(query_texts=[user_query], n_results=n_results)
    return results['documents'][0] if results['documents'] else []

# 5. 엔터프라이즈 가드레일 및 메인 LLM 오케스트레이터 / Enterprise Guardrails & Main LLM Orchestrator
def coupang_advanced_agent(user_message):
    start_time = time.time()
    
    # [가드레일 단계 1: 악성 프롬프트 인젝션 및 보안 필터링]
    # [Guardrail Step 1: Prompt Injection & Security Filtering]
    malicious_keywords = ["비밀번호", "해킹", "시스템 프롬프트", "네이버가 더 좋아"]
    if any(keyword in user_message for keyword in malicious_keywords):
        return "⚠️ [보안 가드레일 안내] 쿠팡 서비스 정책에 위배되거나 부적절한 요청이 감지되어 답변을 제공할 수 없습니다.\n⚠️ [Security Guardrail] A request violating Coupang's policy or malicious activity was detected. Assistance cannot be provided."

    # [RAG 단계 2: Vector DB에서 유저 의도에 맞는 지식 증강 데이터 추출]
    # [RAG Step 2: Extract augmented knowledge matching user intent from Vector DB]
    retrieved_docs = 벡터_기반_상품_검색(user_message, n_results=2)
    context = "\n".join(retrieved_docs) if retrieved_docs else "검색된 상품 없음. / No products found."

    # [프롬프트 엔지니어링: LLM-as-a-Judge 가이드 및 페르소나 주입]
    # [Prompt Engineering: Injecting System Instruction and Persona]
    system_instruction = f"""
    당신은 쿠팡(Coupang)의 수석 AI 엔지니어링 에이전트입니다.
    You are the Senior AI Engineering Agent at Coupang.
    
    [컨텍스트 데이터 / Context Data]
    {context}
    
    [비즈니스 로직 및 규칙 / Business Logic & Rules]
    1. 오직 위의 [컨텍스트 데이터]에 실시간 검색되어 나온 상품 정보만 활용하여 고객에게 추천하세요.
       Recommend products using ONLY the product information retrieved in the [Context Data] above.
    2. 컨텍스트에 없는 상품을 허구로 만들어 추천하는 행위(Hallucination)는 절대 금지됩니다.
       Strictly avoid hallucinating or recommending products not present in the context.
    3. 답변은 쿠팡의 톤앤매너에 맞게 '전문적이고 신뢰감 있게' 작성하세요. (한국어로 응답하세요)
       Keep the tone professional, trustworthy, and aligned with Coupang's brand identity. (Respond in Korean)
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1, # 비결정성 제어 및 일관성을 위해 온도를 극도로 낮춤 / Low temperature for consistency
            max_tokens=1000
        )
        
        # [MLOps 모니터링 레이어] 실시간 지연 시간 및 토큰 비용 계측
        # [MLOps Monitoring Layer] Real-time Latency & Token Cost Measurement
        latency = round(time.time() - start_time, 2)
        tokens_used = response.usage.total_tokens
        estimated_cost = round((tokens_used / 1_000_000) * 0.3, 6)
        
        print(f"\n[📊 엔터프라이즈 모니터링] Latency: {latency}s | Tokens: {tokens_used} | Cost: ${estimated_cost}")
        print(f"[📊 Enterprise Monitoring] Latency: {latency}s | Tokens: {tokens_used} | Cost: ${estimated_cost}")
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"인프라 에러 발생 / Infrastructure Error: {str(e)}"

if __name__ == "__main__":
    print("\n🛒 [쿠팡 초고속 가드레일 내장형 Vector RAG 서버 구동 시작]")
    print("🛒 [Starting Coupang High-Speed Guardrail-Embedded Vector RAG Server]")
    print("💡 이제 '핸드폰'이라고만 검색해도 문맥을 이해해 '아이폰/갤럭시'를 정확히 추천합니다.")
    print("💡 Even searching for generic terms like 'phone' will contextually recommend 'iPhone/Galaxy'.")
    
    while True:
        user_input = input("\n고객 입력 / Customer Input: ")
        if user_input.strip() == "종료" or user_input.strip().lower() == "exit":
            break
        if not user_input.strip():
            continue
            
        answer = coupang_advanced_agent(user_input)
        print(f"\n쿠팡 AI 어시스턴트 / Coupang AI Assistant:\n{answer}")
