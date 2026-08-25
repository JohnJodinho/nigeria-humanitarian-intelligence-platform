import logging
from typing import List, Dict, Any, Tuple, Type
from pydantic import BaseModel, ValidationError

logger = logging.getLogger("validator")

class DataValidator:
    @staticmethod
    def validate_batch(
        records: List[Dict[str, Any]], 
        model_cls: Type[BaseModel],
        endpoint_name: str
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validates a list of raw dictionaries against a Pydantic schema model.
        Returns a tuple of (valid_records, quarantined_records).
        """
        valid_records = []
        quarantined = []

        for record in records:
            try:
                # Validate using Pydantic model
                validated_obj = model_cls.model_validate(record)
                valid_records.append(validated_obj.model_dump())
            except ValidationError as ve:
                quarantined.append({
                    "endpoint_name": endpoint_name,
                    "record_payload": record,
                    "failure_rule_id": "SCHEMA_VALIDATION_ERROR",
                    "failure_reason": str(ve.errors())
                })
            except Exception as e:
                quarantined.append({
                    "endpoint_name": endpoint_name,
                    "record_payload": record,
                    "failure_rule_id": "UNEXPECTED_VALIDATION_ERROR",
                    "failure_reason": str(e)
                })

        logger.info(
            f"Validated {len(records)} records for {endpoint_name}: "
            f"{len(valid_records)} valid, {len(quarantined)} quarantined"
        )
        return valid_records, quarantined
