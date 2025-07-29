from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.reference import Reference
from typing import List
from typing import Optional

@dataclass
class MatrixRow:
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    references: Optional[List[Reference]] = None

MatrixRowSchema = class_schema(MatrixRow, base_schema=RestSchema)
