from typing import Dict, Any, Union, List

class ValidationError(Exception):
    """Exception raised when DTO validation fails."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)
    
    def __str__(self):
        if self.field:
            return f"Validation error for field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"

def validate_required_field(data: Dict[str, Any], field: str) -> None:
    """Validate that a required field exists in the data."""
    if field not in data:
        raise ValidationError(f"Missing required field '{field}'", field, None)

def validate_type(value: Any, expected_type: type, field: str) -> None:
    """Validate that a value is of the expected type."""
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"Expected {expected_type.__name__}, got {type(value).__name__}", 
            field, 
            value
        )

def ensure_dict(value: Any, field: str) -> Dict[str, Any]:
    """Ensure a value is a dictionary, return empty dict if None or invalid."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    raise ValidationError(f"Expected dictionary for {field}", field, value)

def validate_feature_collection(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that data is a valid GeoJSON FeatureCollection."""
    if not isinstance(data, dict):
        raise ValidationError("Expected dictionary for feature collection")
    
    if data.get("type") != "FeatureCollection":
        raise ValidationError("Expected type 'FeatureCollection'", "type", data.get("type"))
    
    if "features" not in data:
        raise ValidationError("Missing 'features' field in feature collection")
    
    if not isinstance(data["features"], list):
        raise ValidationError("Expected list for 'features' field", "features", data["features"])
    
    return data
