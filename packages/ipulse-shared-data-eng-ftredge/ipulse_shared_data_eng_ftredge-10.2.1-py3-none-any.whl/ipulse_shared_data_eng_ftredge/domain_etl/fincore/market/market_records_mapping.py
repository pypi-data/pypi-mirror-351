from datetime import datetime
from ipulse_shared_base_ftredge import MarketRecordType

def build_firestore_record_from_sourced_records(record_type: str, record: dict, dt: datetime) -> dict:
    match record_type:
        case str(MarketRecordType.ADJC):  # Uses AutoStrEnum string value
            return {
                "date": dt,
                "adjc": record["adjusted_close"],
            }

        case str(MarketRecordType.OHLCVA):  # Uses AutoStrEnum string value
            return {
                "date": dt,
                "open":   record["open"],
                "high":   record["high"],
                "low":    record["low"],
                "close":  record["close"],
                "adjc":   record["adjusted_close"],
                "volume": record["volume"],
            }

        case _:
            raise ValueError(f"Unsupported record type: {record_type}")

def build_firestore_record_from_bigquery_data(record_type: str, record: dict, dt: datetime) -> dict:
    """
    Build firestore record from BigQuery fact table data.
    This is similar to build_firestore_record_from_sourced_records but handles BQ field names.
    """
    match record_type:
        case str(MarketRecordType.ADJC):
            return {
                "date": dt,
                "adjc": record.get("adjusted_close"),
            }

        case str(MarketRecordType.OHLCVA):
            return {
                "date": dt,
                "open": record.get("open"),
                "high": record.get("high"),
                "low": record.get("low"),
                "close": record.get("close"),
                "adjc": record.get("adjusted_close"),
                "volume": record.get("volume"),
            }

        case str(MarketRecordType.OHLCV):
            return {
                "date": dt,
                "open": record.get("open"),
                "high": record.get("high"),
                "low": record.get("low"),
                "close": record.get("close"),
                "volume": record.get("volume"),
            }

        case str(MarketRecordType.ADJC_VOLUME):
            return {
                "date": dt,
                "adjc": record.get("adjusted_close"),
                "volume": record.get("volume"),
            }

        case _:
            raise ValueError(f"Unsupported record type: {record_type}")

def get_bigquery_select_fields_for_record_type(record_type: str) -> str:
    """
    Get the appropriate SELECT fields for BigQuery based on record type.
    """
    # Always include date_id for all record types
    base_fields = ["date_id"]
    
    match record_type:
        case str(MarketRecordType.ADJC):
            return ", ".join(base_fields + ["adjusted_close"])
            
        case str(MarketRecordType.OHLCVA):
            return ", ".join(base_fields + ["open", "high", "low", "close", "adjusted_close", "volume"])
            
        case str(MarketRecordType.OHLCV):
            return ", ".join(base_fields + ["open", "high", "low", "close", "volume"])
            
        case str(MarketRecordType.ADJC_VOLUME):
            return ", ".join(base_fields + ["adjusted_close", "volume"])
            
        case _:
            # Default to OHLCVA if unsupported type
            return ", ".join(base_fields + ["open", "high", "low", "close", "adjusted_close", "volume"])