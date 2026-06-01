# Immutable Proof API Specification (v1.0)

## 📘 개요
본 문서는 '불변성 증명(Immutable Proof)' 핵심 로직을 외부 시스템 및 마케팅 자료와 연동할 수 있도록 표준화된 RESTful API 엔드포인트를 정의합니다. 이 서비스는 어떤 데이터 트랜잭션이 **시간적, 논리적으로 변조되지 않았음**을 수학적/시스템적으로 증명하고, 그 기록(Proof)을 반환하는 것이 목적입니다.

### 🎯 핵심 목표
*   데이터의 무결성 및 출처 보장 (Source of Truth).
*   외부 시스템으로부터 안전한 트랜잭션 데이터 수신 처리 능력 확보.
*   API 호출에 대한 명확하고 예측 가능한 응답 구조 제공.

## 🌐 엔드포인트 정의

### 1. Proof Submission & Verification API
데이터를 제출하고 불변성을 검증하는 메인 엔드포인트입니다.

| 속성 | 값 | 설명 |
| :--- | :--- | :--- |
| **HTTP Method** | `POST` | 데이터 트랜잭션을 전송하여 불변성 증명을 요청합니다. |
| **Endpoint URI** | `/api/v1/proof/submit` | Proof 제출 및 검증을 담당하는 API 경로입니다. |
| **요청 헤더 (Headers)** | `Authorization: Bearer <JWT_TOKEN>` | 사용자 인증 토큰이 필수적으로 포함되어야 합니다. |

#### 📄 Request Body Schema (JSON Payload)

API의 입력 데이터 구조를 정의합니다. 모든 필드는 서버 측에서 반드시 유효성 검사(Validation)를 거쳐야 합니다.

```json
{
  "transactionId": "string",      // 필수: 외부 시스템에서 생성한 고유 트랜잭션 ID (UUID 형식 권장).
  "sourceSystem": "string",       // 필수: 데이터를 발생시킨 원천 시스템의 이름 또는 코드 (예: 'PayPal_Webhook', 'CRM_API').
  "dataPayload": {                // 필수: 검증 대상이 되는 실제 데이터 구조.
    "key1": "string/number",      // 예시 필드 1
    "key2": ["string", "number"], // 예시 필드 2 (배열 허용)
    "timestampUtc": "string"      // 필수: 트랜잭션 발생 시점의 UTC 시간 (ISO 8601 형식).
  },
  "requesterContext": {           // 선택적: 요청을 보낸 사용자의 컨텍스트 정보.
    "userId": "string",
    "ipAddress": "string"
  }
}
```

#### ✨ Success Response (HTTP 200 OK)

검증이 성공적으로 완료되었으며, 불변 증명(Proof Record)을 받았음을 의미합니다.

```json
{
  "status": "SUCCESS",                 // 처리 상태: SUCCESS, VALIDATED, etc.
  "proofId": "string",                 // 필수: 시스템에서 부여한 고유의 불변 기록 ID (WORM 로그 레퍼런스).
  "timestampProcessed": "string",      // 증명 기록이 생성된 시점 UTC 시간.
  "validatedDataHash": "string",       // 검증 대상 데이터 전체에 대한 해시 값 (SHA-256 권장).
  "proofChainReference": [             // 불변성을 입증하는 이전 단계의 레퍼런스 배열.
    {"type": "record_id", "id": "UUID_A"}, 
    {"type": "signature", "signer": "SystemKey"}
  ],
  "message": "Immutable Proof generated and stored successfully."
}
```

#### 🚨 Error Response (HTTP 4xx/5xx)

오류 발생 시, 단순한 오류 메시지 대신 **[1. 문제 정의]**, **[2. 원인 분석]**, **[3. 해결책 제시]**의 구조를 강제하여 클라이언트가 즉시 대처할 수 있도록 합니다. (이는 회사 정체성 기반 필수 아웃풋입니다.)

```json
{
  "status": "ERROR",
  "errorCode": "E400_SCHEMA_VIOLATION", // 고유 에러 코드: 개발자가 직접 처리해야 함을 명시합니다.
  "message": "API 요청 유효성 검증에 실패했습니다.",
  "details": {
    "problemDefinition": "요청된 데이터 페이로드의 구조가 예상 스키마와 다릅니다.", // 1. 문제 정의 (What went wrong?)
    "causeAnalysis": "필수 필드 'transactionId' 또는 'dataPayload'의 형식이 잘못되었습니다. 요청 바디를 검토하십시오.",   // 2. 원인 분석 (Why did it go wrong? Source/Time)
    "mitigationSuggestion": "요청 데이터를 반드시 스키마에 맞게 수정하고, 'SourceSystem' 필드를 정확히 기입해 주십시오." // 3. 해결책 제시 (How to fix it?)
  }
}
```

## 🛠️ 상세 기술 가이드라인 및 고려 사항

1.  **데이터 무결성 보장:** 모든 트랜잭션 데이터는 API 수신 직후, 시간 순서와 함께 체이닝(Chaining)되어 해시 값이 계산됩니다. 이 과정은 동기적(Synchronous)으로 처리되지만, 실제 기록 저장 로직은 비동기 큐를 거쳐야 합니다.
2.  **Rate Limiting:** API 남용 방지를 위해 사용자 컨텍스트 및 IP 기반의 Rate Limiting (예: 60초당 10회 호출 제한)을 적용해야 합니다.
3.  **Versioning:** API 변경 시 반드시 버전 관리(`v1` $\rightarrow$ `v2`)를 통해 하위 호환성을 유지해야 합니다.