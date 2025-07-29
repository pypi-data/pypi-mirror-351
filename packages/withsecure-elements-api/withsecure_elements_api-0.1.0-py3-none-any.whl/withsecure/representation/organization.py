from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from uuid import UUID


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class OrganizationRepresentation:
    id: UUID
    name: str
    type: str