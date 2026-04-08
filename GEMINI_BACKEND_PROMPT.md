# 🤖 EasyGeo Backend - Gemini CLI 자동 코드 생성 프롬프트

**사용법**: `gemini < GEMINI_BACKEND_PROMPT.md`

---

## 프로젝트 개요

EasyGeo는 OCR 기반 설비 데이터를 실시간으로 수집, 저장, 조회하는 시스템입니다.

### 핵심 요구사항
- **Framework**: FastAPI
- **Database**: MySQL
- **Cache**: Redis
- **Async**: AsyncIO
- **Real-time**: WebSocket
- **Test**: pytest

---

## 데이터베이스 스키마

### data_logs 테이블
```sql
CREATE TABLE data_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ocr_text VARCHAR(500),
    confidence_score FLOAT,
    image_path VARCHAR(255),
    camera_id INT,
    camera_angle_x FLOAT,
    camera_angle_y FLOAT,
    camera_angle_z FLOAT,
    frame_number INT,
    frame_drop BOOLEAN DEFAULT FALSE,
    status ENUM('valid', 'invalid', 'pending') DEFAULT 'pending',
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_camera_id (camera_id),
    INDEX idx_created_at (created_at),
    INDEX idx_frame_drop (frame_drop),
    INDEX idx_timestamp_camera (timestamp, camera_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### camera_calibration 테이블
```sql
CREATE TABLE camera_calibration (
    id INT PRIMARY KEY AUTO_INCREMENT,
    camera_id INT UNIQUE NOT NULL,
    angle_x FLOAT DEFAULT 0,
    angle_y FLOAT DEFAULT 0,
    angle_z FLOAT DEFAULT 0,
    calibration_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_camera_id (camera_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### error_logs 테이블
```sql
CREATE TABLE error_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    data_id BIGINT NOT NULL,
    error_type VARCHAR(100),
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (data_id) REFERENCES data_logs(id) ON DELETE CASCADE,
    INDEX idx_data_id (data_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## API 명세

### 1. POST /api/data/ocr
**설명**: AI로부터 OCR 데이터 수신

**요청**:
```json
{
  "ocr_text": "인식된 텍스트",
  "confidence_score": 0.95,
  "image_path": "/path/to/image.jpg",
  "camera_id": 1,
  "camera_angle_x": 0.5,
  "camera_angle_y": 0.2,
  "camera_angle_z": 0.0,
  "frame_number": 12345,
  "frame_drop": false,
  "timestamp": "2026-04-10T14:30:15Z"
}
```

**응답**: 
```json
{
  "id": 1,
  "status": "saved",
  "message": "데이터 저장 완료"
}
```

**기능**:
- 데이터 검증
- MySQL에 저장
- Redis에 캐싱
- WebSocket으로 브로드캐스트

---

### 2. GET /api/data/range
**설명**: 시간 범위로 데이터 조회 (분 단위)

**파라미터**:
- start_time: 2026-04-10T14:25:00Z (ISO 8601)
- end_time: 2026-04-10T14:35:00Z
- camera_id: 1 (선택사항)

**응답**:
```json
{
  "data": [
    {
      "minute": "2026-04-10T14:25:00Z",
      "records": [
        {
          "timestamp": "2026-04-10T14:25:15Z",
          "ocr_text": "텍스트1",
          "confidence_score": 0.95,
          "frame_drop": false
        }
      ],
      "frame_drop_count": 0
    }
  ],
  "total_records": 120
}
```

**기능**:
- 시간 범위로 데이터 조회
- 분 단위로 그룹화
- 프레임 드롭 개수 포함

---

### 3. GET /api/data/search
**설명**: 필터를 사용한 데이터 검색

**파라미터**:
- start_time: 2026-04-10T14:25:00Z
- end_time: 2026-04-10T14:35:00Z
- camera_id: 1 (선택사항)
- status: valid (선택사항)
- frame_drop: true (선택사항)
- limit: 20 (선택사항)
- offset: 0 (선택사항)

**응답**:
```json
{
  "data": [
    {
      "id": 1,
      "timestamp": "2026-04-10T14:25:15Z",
      "ocr_text": "텍스트",
      "confidence_score": 0.95,
      "camera_id": 1,
      "frame_drop": false,
      "status": "valid"
    }
  ],
  "total": 45,
  "page": 1,
  "per_page": 20
}
```

---

### 4. GET /api/stats/frame-drop
**설명**: 프레임 드롭 통계

**파라미터**:
- start_time: 2026-04-10T14:25:00Z
- end_time: 2026-04-10T14:35:00Z
- camera_id: 1 (선택사항)

**응답**:
```json
{
  "total_frames": 3600,
  "dropped_frames": 45,
  "drop_rate": 1.25,
  "stats_by_minute": [
    {
      "minute": "2026-04-10T14:25:00Z",
      "total": 60,
      "dropped": 0,
      "rate": 0.0
    }
  ]
}
```

---

### 5. WebSocket /ws/live
**설명**: 실시간 데이터 스트리밍

**메시지**:
```json
{
  "id": 1,
  "timestamp": "2026-04-10T14:30:15Z",
  "ocr_text": "인식된 텍스트",
  "confidence_score": 0.95,
  "camera_id": 1,
  "frame_number": 12345,
  "frame_drop": false,
  "status": "valid"
}
```

**기능**:
- 클라이언트 연결 시 준비
- 새 데이터 들어올 때마다 실시간 전송
- 연결 유지 및 에러 처리

---

### 6. GET /api/health
**설명**: 헬스 체크

**응답**:
```json
{
  "status": "ok",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2026-04-10T14:30:15Z"
}
```

---

## 프로젝트 구조

```
app/
├── __init__.py
├── main.py                           # FastAPI 진입점
├── config.py                         # 설정 관리
├── dependencies.py                   # 의존성 주입
│
├── models/
│   ├── __init__.py
│   ├── base.py                      # Base 모델
│   ├── data_log.py                  # DataLog ORM
│   ├── camera_calibration.py        # CameraCalibration ORM
│   └── error_log.py                 # ErrorLog ORM
│
├── schemas/
│   ├── __init__.py
│   ├── data.py                      # 데이터 스키마
│   ├── camera.py                    # 카메라 스키마
│   └── common.py                    # 공통 스키마
│
├── routes/
│   ├── __init__.py
│   ├── health.py                    # 헬스 체크
│   ├── data.py                      # /api/data/*
│   └── camera.py                    # /api/camera/*
│
├── services/
│   ├── __init__.py
│   ├── data_service.py              # 데이터 비즈니스 로직
│   ├── cache_service.py             # Redis 캐싱
│   ├── validation_service.py        # 데이터 검증
│   └── camera_service.py            # 카메라 로직
│
├── database/
│   ├── __init__.py
│   ├── session.py                   # DB 세션 관리
│   ├── connection.py                # MySQL 연결
│   └── base.py                      # Base 모델
│
├── cache/
│   ├── __init__.py
│   └── redis_client.py              # Redis 클라이언트
│
├── websocket/
│   ├── __init__.py
│   ├── manager.py                   # WebSocket 연결 관리
│   └── handlers.py                  # WebSocket 핸들러
│
├── middleware/
│   ├── __init__.py
│   ├── error_handler.py             # 에러 처리
│   └── logger.py                    # 로깅
│
└── utils/
    ├── __init__.py
    ├── logger.py                    # 로그 설정
    ├── exceptions.py                # 커스텀 예외
    └── constants.py                 # 상수 정의

tests/
├── __init__.py
├── conftest.py                      # pytest 설정
├── test_health.py
├── test_data_routes.py
├── test_data_service.py
├── test_cache_service.py
└── test_camera_routes.py

scripts/
├── init_db.py                       # DB 초기화
└── seed_data.py                     # 더미 데이터

.env.example
requirements.txt
README.md
pytest.ini
```

---

## 주요 파일별 구현 요구사항

### app/main.py
- FastAPI 앱 초기화
- CORS 미들웨어 설정
- 라우트 포함 (health, data, camera)
- WebSocket 엔드포인트 등록
- 에러 핸들러 설정
- 시작/종료 이벤트 설정

### app/models/data_log.py
- DataLog ORM 모델
- 필드: id, timestamp, ocr_text, confidence_score, image_path, camera_id, angles, frame_number, frame_drop, status, error_message, created_at, updated_at
- 관계: error_logs (역관계)

### app/models/camera_calibration.py
- CameraCalibration ORM 모델
- 필드: id, camera_id, angle_x, angle_y, angle_z, calibration_date, created_at, updated_at

### app/models/error_log.py
- ErrorLog ORM 모델
- 필드: id, data_id, error_type, error_message, created_at
- 관계: data_log (외래키)

### app/schemas/data.py
- DataLogCreate (POST 요청)
- DataLogResponse (GET 응답)
- DataLogUpdate (PUT 요청)
- GroupedDataResponse (분 단위 그룹화)
- FrameDropStats (프레임 드롭 통계)

### app/services/data_service.py
- save_ocr_data(data) - OCR 데이터 저장
- get_data_by_minute(start, end, camera_id) - 분 단위 조회
- search_data(start, end, filters) - 필터 검색
- get_frame_drop_stats(start, end, camera_id) - 프레임 드롭 통계
- 모든 메서드는 async

### app/services/cache_service.py
- cache_latest_data(data) - 최신 데이터 캐싱
- get_latest_data() - 캐시에서 최신 데이터 조회
- invalidate_latest() - 캐시 무효화
- 모든 메서드는 async

### app/routes/health.py
- GET /api/health - 헬스 체크

### app/routes/data.py
- POST /api/data/ocr - OCR 데이터 수신
- GET /api/data/range - 시간 범위 조회
- GET /api/data/search - 필터 검색
- GET /api/stats/frame-drop - 프레임 드롭 통계

### app/routes/camera.py
- GET /api/camera/{camera_id}/calibration - 보정값 조회
- POST /api/camera/{camera_id}/calibration - 보정값 저장
- PUT /api/camera/{camera_id}/calibration - 보정값 수정
- DELETE /api/camera/{camera_id}/calibration - 보정값 삭제

### app/websocket/manager.py
- ConnectionManager 클래스
- connect() - 연결 추가
- disconnect() - 연결 제거
- broadcast() - 모든 클라이언트에게 전송

### app/websocket/handlers.py
- websocket_live() - WebSocket /ws/live 핸들러
- 새 데이터 들어올 때마다 클라이언트에 전송

### app/database/connection.py
- async_engine 설정 (MySQL)
- AsyncSessionLocal 설정
- 재시도 로직 포함

### app/database/session.py
- async get_db() - 의존성 주입용 세션

### app/cache/redis_client.py
- RedisClient 클래스
- 연결 풀 관리
- get(), set(), delete() 메서드
- 모든 메서드는 async

### tests/conftest.py
- test_db 픽스처 (테스트 DB)
- client 픽스처 (테스트 클라이언트)

### tests/test_health.py
- test_health_check() - 헬스 체크 테스트

### tests/test_data_routes.py
- test_create_ocr_data() - OCR 데이터 생성
- test_get_data_range() - 시간 범위 조회
- test_search_data() - 필터 검색
- test_frame_drop_stats() - 프레임 드롭 통계

### tests/test_cache_service.py
- test_cache_latest_data() - 캐싱 테스트
- test_get_latest_data() - 캐시 조회 테스트

---

## 필수 설정 파일

### .env.example
```env
# Database
DATABASE_URL=mysql+pymysql://easygeo:password123@localhost:3306/easygeo

# Redis
REDIS_URL=redis://localhost:6379/0

# App Settings
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here

# Server
HOST=0.0.0.0
PORT=8000
```

### requirements.txt
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
httpx==0.25.2
websockets==12.0
sqlalchemy==2.0.23
pymysql==1.1.0
alembic==1.13.0
aioredis==2.0.1
redis==5.0.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
pillow==10.1.0
numpy==1.26.3
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
python-json-logger==2.0.7
black==23.12.1
flake8==6.1.0
isort==5.13.2
```

### pytest.ini
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

---

## 구현 체크리스트

### Phase 1: 기본 설정
- [ ] FastAPI main.py
- [ ] config.py (환경 변수)
- [ ] dependencies.py (의존성)
- [ ] database/connection.py
- [ ] database/session.py
- [ ] cache/redis_client.py

### Phase 2: 모델 및 스키마
- [ ] models/base.py
- [ ] models/data_log.py
- [ ] models/camera_calibration.py
- [ ] models/error_log.py
- [ ] schemas/data.py
- [ ] schemas/camera.py

### Phase 3: 서비스
- [ ] services/data_service.py
- [ ] services/cache_service.py
- [ ] services/validation_service.py
- [ ] services/camera_service.py

### Phase 4: 라우트
- [ ] routes/health.py
- [ ] routes/data.py
- [ ] routes/camera.py

### Phase 5: WebSocket
- [ ] websocket/manager.py
- [ ] websocket/handlers.py
- [ ] main.py에 WebSocket 등록

### Phase 6: 테스트
- [ ] tests/conftest.py
- [ ] tests/test_health.py
- [ ] tests/test_data_routes.py
- [ ] tests/test_cache_service.py

### Phase 7: 유틸리티
- [ ] utils/logger.py
- [ ] utils/exceptions.py
- [ ] utils/constants.py
- [ ] middleware/error_handler.py

---

## 개발 순서

1. **Phase 1-2**: 기본 구조 및 모델 (1주)
2. **Phase 3-4**: 서비스 및 라우트 (2주)
3. **Phase 5**: WebSocket 구현 (1주)
4. **Phase 6-7**: 테스트 및 유틸리티 (1주)
5. **최적화 및 배포**: 나머지 (7주)

---

## 최종 확인 사항

생성된 코드는 다음을 만족해야 합니다:

✅ 모든 함수는 `async def`  
✅ 모든 DB 작업은 `await` 사용  
✅ 모든 라우트는 비동기 처리  
✅ 모든 에러는 HTTPException으로 처리  
✅ 모든 데이터는 Pydantic 스키마로 검증  
✅ 모든 테스트는 pytest로 작성  
✅ 모든 로그는 logger로 기록  
✅ MySQL 커넥션 풀 사용  
✅ Redis 캐싱 구현  
✅ WebSocket 연결 관리  

---

## 생성 시작!

위의 요구사항을 모두 만족하는 완전한 FastAPI 백엔드 코드를 생성해주세요.

모든 파일을 구조대로 만들고, 각 파일에는:
- 필요한 임포트
- 클래스/함수 정의
- 타입 힌트
- 에러 처리
- 주석

을 포함해야 합니다.
