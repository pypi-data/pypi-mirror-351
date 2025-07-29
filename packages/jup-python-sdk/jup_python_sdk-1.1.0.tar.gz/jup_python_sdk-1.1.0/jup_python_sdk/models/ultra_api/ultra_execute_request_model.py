from typing import Any, Dict

from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class UltraExecuteRequest(BaseModel):
    signed_transaction: str
    request_id: str

    def to_dict(self) -> Dict[str, Any]:
        params = self.model_dump(exclude_none=True)

        camel_case_params = {
            to_camel(key): value for key, value in params.items()
        }

        return camel_case_params
