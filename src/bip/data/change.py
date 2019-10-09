from typing import Any, Union

from ..models import ChangeRecord, ChangeType, User


def record(
            obj: Any, change_type: Union[ChangeType, str], user: User, description: str
        ) -> ChangeRecord:
    if isinstance(change_type, str):
        change_type = ChangeType[change_type]
    return ChangeRecord.log_change(obj, change_type, user, description)
