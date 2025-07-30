from typing import Generic, TypeVar, Optional, Any, Dict, List
import datetime as dt
import json
from pydantic import BaseModel, ConfigDict
from fastapi.responses import JSONResponse
from ipulse_shared_core_ftredge.utils.json_encoder import EnsureJSONEncoderCompatibility, convert_to_json_serializable


T = TypeVar('T')

class BaseAPIResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    success: bool
    chargeable: bool = False # Added chargeable attribute
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None

    metadata: Dict[str, Any] = {
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat()
    }

class UserCreditBalance(BaseModel):
    sbscrptn_based_insight_credits: float
    extra_insight_credits: float

class UpdatedUserCreditInfo(BaseModel):
    charge_attempted: bool
    charge_successful: bool
    cost_incurred: float
    items_processed_for_charge: int
    user_balance: UserCreditBalance

class CreditChargeableAPIResponse(BaseAPIResponse[T], Generic[T]):
    updated_user_credit_info: Optional[UpdatedUserCreditInfo] = None

class PaginatedAPIResponse(BaseAPIResponse, Generic[T]):
    total_count: int
    page: int
    page_size: int
    items: List[T]

class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        # First preprocess content with our utility function
        if isinstance(content, dict) and "data" in content and hasattr(content["data"], "model_dump"):
            # If content["data"] is a Pydantic model, use model_dump with exclude_unset=True
            # and exclude_computed=True to prevent serialization of computed fields
            content = dict(content)  # Create a copy to avoid modifying the original
            content["data"] = content["data"].model_dump(
                exclude_unset=True,
                exclude_computed=True
            )

        # Now convert all problematic types to JSON serializable values
        json_safe_content = convert_to_json_serializable(content)

        # Use the CustomJSONEncoder for additional safety
        return json.dumps(
            json_safe_content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=EnsureJSONEncoderCompatibility
        ).encode("utf-8")