from app.schemas.sensor_data import SensorDataCreate


class ValidationService:
    @staticmethod
    def validate_sensor_data(data: SensorDataCreate) -> None:
        """
        센서 데이터 유효성 검사.
        현재는 기본 타입 검사만 수행 (Pydantic이 처리).
        추후 정상 범위 검사 로직 추가 예정.
        """
        pass

    @staticmethod
    def is_out_of_range(data: SensorDataCreate) -> bool:
        """
        센서값 비정상 범위 여부 확인.
        추후 각 필드의 정상 범위 기준 추가 예정.
        """
        # TODO: 범위 기준 추가 예정
        return False
