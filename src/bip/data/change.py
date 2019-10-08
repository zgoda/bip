from ..models import ChangeRecord, ChangeType


def record(obj, change_type, user, description):
    if isinstance(change_type, str):
        change_type = ChangeType[change_type]
    return ChangeRecord.log_change(obj, change_type, user, description)
