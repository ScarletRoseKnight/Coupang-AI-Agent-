# 🛒 Coupang-Native Vector RAG Shopping Agent (Production-Ready MVP)

- 본 프로젝트는 초당 수만 건의 대규모 트래픽과 수억 개의 상품 카탈로그 환경을 가정하고 설계된 쿠팡 차세대 AI-First 이커머스 쇼핑 에이전트의 MVP 아키텍처입니다.

This project represents the MVP architecture of Coupang's next-generation AI-First e-commerce shopping agent, designed under the assumption of high-scale traffic (tens of thousands of requests per second) and hundreds of millions of product catalogs.

## 🛠️ 핵심 아키텍처 (Key Architecture)
- **Vector DB 기반 Semantic Search (Vector DB-based Semantic Search):** 문자열 단순 매칭 한계를 극복하기 위해 `ChromaDB`와 오픈AI의 `text-embedding-3-small` 모델을 결합하여, 유저 의도와 문맥 중심의 상품 검색 파이프라인(Retriever)을 구현했습니다.

To overcome the limitations of simple keyword matching, we implemented a context-aware product retrieval pipeline by combining `ChromaDB` with OpenAI's `text-embedding-3-small` model.
  
- **Enterprise-Level Guardrails:** 시스템 해킹(Prompt Injection) 방지 및 브랜드 리스크 예방을 위한 입력값 검증 보안 필터링 레이어를 내장했습니다.

Built-in input validation security layers prevent prompt injections and mitigate brand risks.
  
- **MLOps Metric Logging:** 프로덕션 배포 관점을 고려하여 매 호출마다 Latency(지연 시간), Token 소모량, 인프라 예상 비용을 정량적으로 계측하고 모니터링 로그를 출력하도록 설계했습니다.

Designed for production deployment by quantitatively measuring and logging Latency, Token consumption, and estimated infrastructure costs for every single call.

## 📈 대규모 상용화 서비스(Production) 확장 로드맵 (Production Scaling Roadmap)
- 현재의 로컬 임메모리 구조에서 쿠팡의 실규모 서비스로 확장하기 위한 고도화 아키텍처 설계 방향성입니다:

The following architectural directions outline how to scale from the current local in-memory setup to Coupang's actual production scale:

1. **분산 Vector DB 및 비동기 파이프라인 확장 (Distributed Vector DB & Asynchronous Pipeline Scaling)**
   - 수억 개 카탈로그 대응을 위해 인메모리 구조에서 **Kubernetes(EKS)** 기반으로 클러스터링된 분산 Vector DB (**Qdrant** 또는 **Milvus**) 인프라로 전환합니다.

Transition from an in-memory setup to a distributed Vector DB (**Qdrant** or **Milvus**) infrastructure clustered on **Kubernetes (EKS)** to handle hundreds of millions of catalogs.
   
   - 대량의 대규모 상품 데이터 동기화 시 병목을 막기 위해 **Apache Kafka**를 도입하여 실시간 상품 변동 내역을 비동기(Asynchronous)로 임베딩 인덱싱하도록 설계합니다.

Introduce **Apache Kafka** to prevent bottlenecks during mass data synchronization, enabling asynchronous embedding and indexing of real-time product updates.

3. **Advanced RAG를 통한 검색 정확도 극대화 (Maximizing Retrieval Accuracy via Advanced RAG)**
   - 유저의 모호한 질의를 LLM이 최적의 검색 쿼리 여러 개로 쪼개어 변환하는 **Query Rewriting** 엔진을 전처리 단계에 배치합니다.

Deploy a **Query Rewriting** engine in the preprocessing stage to transform ambiguous user queries into multiple optimal search queries via LLM.
     
   - Vector DB가 1차 덤프한 상위 K개 결과를 쿠팡 고유의 메타데이터(가격, 판매량, 로켓배송 유무)와 결합하여 순위를 재조정하는 **Cross-Encoder 기반 Re-ranking** 레이어를 추가합니다.

     Integrate a **Cross-Encoder-based Re-ranking** layer that reranks top-K results by blending Vector DB retrieval with Coupang’s proprietary metadata (price, sales volume, Rocket Delivery status).

4. **MLOps 인프라 비용 및 성능 최적화 (MLOps Infra Cost & Performance Optimization)**
   - 반복적인 중복 유저 질문에 대응하고 LLM API 토큰 비용을 획기적으로 절감하기 위해 **GPTCache** 및 **Redis** 기반의 세션 캐싱 레이어를 적용합니다. 이를 통해 지연시간(Latency)을 1초 미만으로 단축하고 인프라 비용을 최소 40% 이상 개선합니다.
   
Apply a session caching layer based on **GPTCache** and **Redis** to handle redundant user queries and dramatically cut LLM API token costs. This will reduce latency to sub-second levels and improve infrastructure costs by at least 40%.

## 🚀 시작하기 (Getting Started)
```bash
pip install -r requirements.txt
python app.py
