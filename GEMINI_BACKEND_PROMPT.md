# 🤖 EasyGeo Backend - Gemini CLI 자동 코드 생성 프롬프트

**사용법**: `gemini < GEMINI_BACKEND_PROMPT.md`

---

## 프로젝트 개요

EasyGeo는 Vision(Python) 모듈에서 수집한 설비 센서 데이터를 받아서 실시간으로 저장, 조회하는 시스템입니다.

### 핵심 요구사항
- **Framework**: FastAPI
- **Database**: MySQL  
- **Cache**: Redis
- **Async**: AsyncIO
- **Real-time**: WebSocket
- **Test**: pytest

---

## 데이터베이스 스키마

### sensor_data 테이블 (핵심)
```sql
CREATE TABLE sensor_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME NOT NULL,
    iso_temp_pv FLOAT NOT NULL COMMENT 'ISO 원액온도(PV)',
    iso_temp_sv FLOAT NOT NULL COMMENT 'ISO 원액온도(SV)',
    iso_pump_speed INT NOT NULL COMMENT 'ISO 펌프속도(RPM)',
    iso_press FLOAT NOT NULL COMMENT 'ISO 압력(bar)',
    pol1_temp_pv FLOAT NOT NULL COMMENT 'POL1 원액온도(PV)',
    pol1_temp_sv FLOAT NOT NULL COMMENT 'POL1 원액온도(SV)',
    pol1_pump_speed INT NOT NULL COMMENT 'POL1 펌프속도',
    pol1_press FLOAT NOT NULL COMMENT 'POL1 압력',
    pol2_temp_pv FLOAT NOT NULL COMMENT 'POL2 원액온도(PV)',
    pol2_temp_sv FLOAT NOT NULL COMMENT 'POL2 원액온도(SV)',
    pol2_pump_speed INT NOT NULL COMMENT 'POL2 펌프속도',
    pol2_press FLOAT NOT NULL COMMENT 'POL2 압력',
    mix_motor_speed INT NOT NULL COMMENT '믹싱 모터 속도',
    total_count INT NOT NULL COMMENT '누적 생산량',
    error_count INT NOT NULL COMMENT '불량 생산량',
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 수신 시간',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성 시간',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 시간',
    
    INDEX idx_timestamp (timestamp),
    INDEX idx_received_at (received_at),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='설비 센서 데이터';
```

### statistics 테이블
```sql
CREATE TABLE statistics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    stat_date DATE NOT NULL,
    total_count INT NOT NULL COMMENT '일일 총 생산량',
    error_count INT NOT NULL COMMENT '일일 불량량',
    avg_iso_temp_pv FLOAT COMMENT '평균 ISO 온도(PV)',
    avg_pol1_temp_pv FLOAT COMMENT '평균 POL1 온도(PV)',
    avg_pol2_temp_pv FLOAT COMMENT '평균 POL2 온도(PV)',
    max_iso_press FLOAT COMMENT '최고 ISO 압력',
    min_iso_press FLOAT COMMENT '최저 ISO 압력',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_stat_date (stat_date),
    UNIQUE KEY unique_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='통계 데이터';
```

### error_logs 테이블
```sql
CREATE TABLE error_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sensor_data_id BIGINT COMMENT '센서 데이터 ID (FK)',
    error_type VARCHAR(100) COMMENT '에러 타입',
    error_message TEXT COMMENT '에러 메시지',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성 시간',
    
    FOREIGN KEY (sensor_data_id) REFERENCES sensor_data(id) ON DELETE CASCADE,
    INDEX idx_sensor_data_id (sensor_data_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='에러 로그';
```

---

## API 명세

### 1. POST /api/v1/sensor-data
**설명**: Vision(Python) 모듈에서 센서 데이터 수신

**요청 (15개 필드 모두 필수)**:
```json
{
  "timestamp": "2026-04-14T09:00:00Z",
  "iso_temp_pv": 180.5,
  "iso_temp_sv": 180.0,
  "iso_pump_speed": 1500,
  "iso_press": 1.55,
  "pol1_temp_pv": 175.2,
  "pol1_temp_sv": 175.0,
  "pol1_pump_speed": 1450,
  "pol1_press": 1.42,
  "pol2_temp_pv": 178.8,
  "pol2_temp_sv": 178.0,
  "pol2_pump_speed": 1480,
  "pol2_press": 1.48,
  "mix_motor_speed": 1200,
  "total_count": 550,
  "error_count": 2
}
```

**응답 (201 Created)**:
```json
{
  "id": 1,
  "status": "created",
  "message": "센서 데이터가 저장되었습니다",
  "timestamp": "2026-04-14T09:00:00Z"
}
```

**에러 응답 (400 Bad Request)**:
```json
{
  "detail": "필드 'iso_temp_pv' 누락"
}
```

**구현 요구사항**:
- 15개 필드 모두 필수 (하나라도 누락되면 400 에러)
- 모든 필드가 정확한 타입이어야 함
- MySQL에 저장
- Redis에 최신 데이터 캐싱
- WebSocket /ws/live로 실시간 전송
- 에러 발생 시 error_logs 테이블 기록

---

### 2. GET /api/v1/sensor-data/latest
**설명**: 최신 센서 데이터 조회

**응답 (200 OK)**:
```json
{
  "id": 100,
  "timestamp": "2026-04-14T09:05:30Z",
  "iso_temp_pv": 180.5,
  "iso_temp_sv": 180.0,
  "iso_pump_speed": 1500,
  "iso_press": 1.55,
  "pol1_temp_pv": 175.2,
  "pol1_temp_sv": 175.0,
  "pol1_pump_speed": 1450,
  "pol1_press": 1.42,
  "pol2_temp_pv": 178.8,
  "pol2_temp_sv": 178.0,
  "pol2_pump_speed": 1480,
  "pol2_press": 1.48,
  "mix_motor_speed": 1200,
  "total_count": 550,
  "error_count": 2,
  "received_at": "2026-04-14T09:05:31Z"
}
```

**구현 요구사항**:
- Redis 캐시에서 먼저 조회
- 캐시 없으면 MySQL에서 최신 데이터 조회

---

### 3. GET /api/v1/sensor-data/range
**설명**: 시간 범위로 센서 데이터 조회

**파라미터**:
- start_time: 2026-04-14T08:00:00Z (ISO 8601, 필수)
- end_time: 2026-04-14T10:00:00Z (ISO 8601, 필수)
- limit: 100 (선택사항, 기본값 100)
- offset: 0 (선택사항, 기본값 0)

**응답 (200 OK)**:
```json
{
  "data": [
    {
      "id": 1,
      "timestamp": "2026-04-14T09:00:00Z",
      "iso_temp_pv": 180.5,
      "iso_temp_sv": 180.0,
      "iso_pump_speed": 1500,
      "iso_press": 1.55,
      "pol1_temp_pv": 175.2,
      "pol1_temp_sv": 175.0,
      "pol1_pump_speed": 1450,
      "pol1_press": 1.42,
      "pol2_temp_pv": 178.8,
      "pol2_temp_sv": 178.0,
      "pol2_pump_speed": 1480,
      "pol2_press": 1.48,
      "mix_motor_speed": 1200,
      "total_count": 550,
      "error_count": 2,
      "received_at": "2026-04-14T09:00:01Z"
    }
  ],
  "total": 120,
  "limit": 100,
  "offset": 0
}
```

---

### 4. GET /api/v1/statistics/daily
**설명**: 일일 통계 조회

**파라미터**:
- date: 2026-04-14 (YYYY-MM-DD 형식, 필수)

**응답 (200 OK)**:
```json
{
  "stat_date": "2026-04-14",
  "total_count": 5500,
  "error_count": 25,
  "error_rate": 0.45,
  "avg_iso_temp_pv": 180.2,
  "avg_pol1_temp_pv": 175.1,
  "avg_pol2_temp_pv": 178.5,
  "max_iso_press": 1.60,
  "min_iso_press": 1.50,
  "data_points": 550
}
```

**구현 요구사항**:
- statistics 테이블에서 먼저 조회
- 없으면 sensor_data에서 계산 후 statistics 테이블에 저장

---

### 5. GET /api/v1/statistics/summary
**설명**: 최근 7일 요약 통계

**응답 (200 OK)**:
```json
{
  "period": "last_7_days",
  "total_production": 38500,
  "total_errors": 180,
  "error_rate": 0.47,
  "daily_data": [
    {
      "date": "2026-04-14",
      "total_count": 5500,
      "error_count": 25
    },
    {
      "date": "2026-04-13",
      "total_count": 5450,
      "error_count": 28
    }
  ]
}
```

---

### 6. WebSocket /ws/live
**설명**: 실시간 센서 데이터 스트리밍

**메시지 (클라이언트로 전송)**:
```json
{
  "id": 101,
  "timestamp": "2026-04-14T09:10:00Z",
  "iso_temp_pv": 180.5,
  "iso_temp_sv": 180.0,
  "iso_pump_speed": 1500,
  "iso_press": 1.55,
  "pol1_temp_pv": 175.2,
  "pol1_temp_sv": 175.0,
  "pol1_pump_speed": 1450,
  "pol1_press": 1.42,
  "pol2_temp_pv": 178.8,
  "pol2_temp_sv": 178.0,
  "pol2_pump_speed": 1480,
  "pol2_press": 1.48,
  "mix_motor_speed": 1200,
  "total_count": 551,
  "error_count": 2
}
```

**구현 요구사항**:
- 클라이언트 연결 유지
- 새 센서 데이터 들어올 때마다 실시간 전송
- 연결 끊김 처리

---

### 7. GET /api/v1/health
**설명**: 헬스 체크

**응답 (200 OK)**:
```json
{
  "status": "ok",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2026-04-14T09:00:15Z"
}
```

---

## 프로젝트 구조

```
app/
├── __init__.py
├── main.py
├── config.py
├── dependencies.py
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── sensor_data.py
│   ├── statistics.py
│   └── error_log.py
├── schemas/
│   ├── __init__.py
│   ├── sensor_data.py
│   ├── statistics.py
│   └── common.py
├── routes/
│   ├── __init__.py
│   ├── health.py
│   ├── sensor_data.py
│   └── statistics.py
├── services/
│   ├── __init__.py
│   ├── sensor_service.py
│   ├── cache_service.py
│   ├── statistics_service.py
│   └── validation_service.py
├── database/
│   ├── __init__.py
│   ├── session.py
│   ├── connection.py
│   └── base.py
├── cache/
│   ├── __init__.py
│   └── redis_client.py
├── websocket/
│   ├── __init__.py
│   ├── manager.py
│   └── handlers.py
├── middleware/
│   ├── __init__.py
│   ├── error_handler.py
│   └── logger.py
└── utils/
    ├── __init__.py
    ├── logger.py
    ├── exceptions.py
    └── constants.py

tests/
├── __init__.py
├── conftest.py
├── test_health.py
├── test_sensor_data_routes.py
├── test_sensor_service.py
├── test_cache_service.py
└── test_statistics_service.py
```

---

## 주요 파일별 구현 요구사항

### app/main.py
- FastAPI 앱 초기화
- CORS 미들웨어 설정
- 라우트 포함 (health, sensor_data, statistics)
- WebSocket 핸들러 등록
- 에러 핸들러 설정

### app/models/sensor_data.py
- SensorData ORM 모델
- 필드: id, timestamp, iso_temp_pv, iso_temp_sv, iso_pump_speed, iso_press, pol1_temp_pv, pol1_temp_sv, pol1_pump_speed, pol1_press, pol2_temp_pv, pol2_temp_sv, pol2_pump_speed, pol2_press, mix_motor_speed, total_count, error_count, received_at, created_at, updated_at
- 관계: error_logs (역관계)

### app/models/statistics.py
- Statistics ORM 모델
- 필드: id, stat_date, total_count, error_count, avg_iso_temp_pv, avg_pol1_temp_pv, avg_pol2_temp_pv, max_iso_press, min_iso_press, created_at

### app/models/error_log.py
- ErrorLog ORM 모델
- 필드: id, sensor_data_id, error_type, error_message, created_at

### app/schemas/sensor_data.py
- SensorDataCreate (POST 요청) - 15개 필드 모두 필수
- SensorDataResponse (GET 응답)
- 필드 검증: 타입 체크, 필드 필수 체크

### app/schemas/statistics.py
- DailyStatistics
- WeeklySummary
- StatisticsResponse

### app/services/sensor_service.py
- save_sensor_data(data) - 센서 데이터 저장
- get_latest_sensor_data() - 최신 데이터 조회
- get_sensor_data_range(start, end, limit, offset) - 시간 범위 조회
- 모든 메서드는 async

### app/services/statistics_service.py
- calculate_daily_statistics(date) - 일일 통계 계산
- get_daily_statistics(date) - 일일 통계 조회
- get_weekly_summary() - 주간 요약
- 모든 메서드는 async

### app/services/cache_service.py
- cache_latest_sensor_data(data) - 최신 센서 데이터 캐싱
- get_cached_latest_sensor_data() - 캐시에서 조회
- invalidate_latest() - 캐시 무효화
- 모든 메서드는 async

### app/services/validation_service.py
- validate_sensor_data(data) - 센서 데이터 검증
- validate_all_required_fields(data) - 필드 필수 체크 (15개 모두 필수)
- validate_field_types(data) - 타입 체크

### app/routes/health.py
- GET /api/v1/health

### app/routes/sensor_data.py
- POST /api/v1/sensor-data
- GET /api/v1/sensor-data/latest
- GET /api/v1/sensor-data/range

### app/routes/statistics.py
- GET /api/v1/statistics/daily
- GET /api/v1/statistics/summary

### app/websocket/manager.py
- ConnectionManager 클래스
- connect(), disconnect(), broadcast() 메서드

### app/websocket/handlers.py
- websocket_live() - WebSocket /ws/live 핸들러
- 새 센서 데이터 들어올 때마다 모든 클라이언트에게 전송

### 테스트 파일들
- test_health.py - 헬스 체크 테스트
- test_sensor_data_routes.py - API 엔드포인트 테스트
- test_sensor_service.py - 센서 서비스 테스트
- test_cache_service.py - 캐싱 테스트
- test_statistics_service.py - 통계 테스트

---

## 필수 설정 파일

### .env.example
```env
DATABASE_URL=mysql+pymysql://easygeo:password123@localhost:3306/easygeo
REDIS_URL=redis://localhost:6379/0
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
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
```

---

## 생성 요청사항

위의 요구사항을 모두 만족하는 완전한 FastAPI 백엔드 코드를 생성해주세요.

**핵심 요구사항**:
- 모든 함수는 `async def`
- 모든 DB 작업은 `await` 사용
- 모든 라우트는 비동기 처리
- POST /api/v1/sensor-data: 15개 필드 모두 필수, 하나 누락되면 400 에러
- 필드명 대소문자 엄격히 준수 (필드명: iso_temp_pv, iso_temp_sv, iso_pump_speed, iso_press, pol1_temp_pv, pol1_temp_sv, pol1_pump_speed, pol1_press, pol2_temp_pv, pol2_temp_sv, pol2_pump_speed, pol2_press, mix_motor_speed, total_count, error_count)
- MySQL에 저장
- Redis에 최신 데이터 캐싱
- WebSocket으로 실시간 전송
- 모든 에러는 HTTPException으로 처리
- 모든 데이터는 Pydantic 스키마로 검증
- 모든 테스트는 pytest로 작성

---

**생성 시작!**
