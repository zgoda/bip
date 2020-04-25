from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass, field
from typing import List, Mapping

from .models import Model
from .utils.cli import ColAlign, ColDataType, ColSpec

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
    'AUTO': ColDataType.int,
    'BOOL': ColDataType.exp,
}


@dataclass
class DisplayMeta:
    """Tabular object display metadata.
    """
    klass: Model
    columns: List[str]
    overrides: Mapping[str, ColumnOverride] = field(default_factory=dict)

    def cli_list_columns(
                self, overrides: Mapping[str, ColumnOverride]
            ) -> List[ColSpec]:
        """Generate list of column specifications for displaying in CLI.

        :param overrides: column param override information
        :type overrides: Mapping[str, ColumnOverride]
        :return: list of column specifications
        :rtype: List[ColSpec]
        """
        rv = []
        for name in self.columns:
            col_data_type = ColDataType.auto
            col_align = _COLUMN_DEFAULT_ALIGN[col_data_type]
            col_title = name
            column = self.klass._meta.fields.get(name)
            if column is not None:
                col_data_type = _DATATYPE_TO_COLTYPE.get(
                    column.field_type, ColDataType.auto
                )
                col_align = _COLUMN_DEFAULT_ALIGN.get(col_data_type, ColAlign.left)
            col_override = overrides.get(name) or self.overrides.get(name)
            col_data_type = col_override.datatype or col_data_type
            col_align = col_override.align or col_align
            col_title = col_override.title or name
            rv.append(ColSpec(align=col_align, dtype=col_data_type, title=col_title))
        return rv
