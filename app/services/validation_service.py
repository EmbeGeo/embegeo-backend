from app.schemas.sensor_data import SensorDataCreate


class ValidationService:
    @staticmethod
    def is_out_of_range(data: SensorDataCreate) -> bool:
        # TODO: 범위 기준 추가 예정
        return False
