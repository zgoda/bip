from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass, field
from typing import List, Mapping, Optional

from .utils.cli import ColAlign, ColDataType, ColSpec
from .utils.db import Model

ColumnOverride = namedtuple(
    'ColumnOverride', ['title', 'datatype', 'align'], defaults=(None, None)
)

_COLUMN_DEFAULT_ALIGN = {
    ColDataType.int: ColAlign.right,
    ColDataType.float: ColAlign.center,
    ColDataType.exp: ColAlign.center,
    ColDataType.auto: ColAlign.left,
}

_DATATYPE_TO_COLTYPE = {
    float: ColDataType.float,
    int: ColDataType.int,
    bool: ColDataType.exp,
}


@dataclass
class DisplayMeta:
    klass: Model
    columns: List[str]
    overrides: Mapping[str, ColumnOverride] = field(default_factory=dict)

    def cli_list_columns(
                self, overrides: Optional[Mapping[str, ColumnOverride]] = None
            ) -> List[ColSpec]:
        if overrides is None:
            overrides = {}
        rv = []
        for name in self.columns:
            col_data_type = ColDataType.auto
            col_align = _COLUMN_DEFAULT_ALIGN[col_data_type]
            col_title = name
            column = self.klass.__table__.columns.get(name)
            if column is not None:
                col_data_type = _DATATYPE_TO_COLTYPE.get(
                    column.type.python_type, ColDataType.auto
                )
                col_align = _COLUMN_DEFAULT_ALIGN.get(col_data_type, ColAlign.left)
            col_override = overrides.get(name) or self.overrides.get(name)
            if col_override:
                col_data_type = col_override.datatype or col_data_type
                col_align = col_override.align or col_align
                col_title = col_override.title or name
            rv.append(ColSpec(align=col_align, dtype=col_data_type, title=col_title))
        return rv
