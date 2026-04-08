class ValidationService:
    @staticmethod
    def is_valid_confidence_score(score: float) -> bool:
        """Checks if the confidence score is within a valid range (0.0 to 1.0)."""
        return 0.0 <= score <= 1.0

    @staticmethod
    def is_valid_camera_id(camera_id: int) -> bool:
        """Checks if the camera_id is positive."""
        return camera_id > 0
