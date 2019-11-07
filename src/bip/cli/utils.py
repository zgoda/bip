from ..models import Category, Page, User
from ..utils.cli import ColAlign, ColDataType, ColSpec


COLUMN_SPECS = {
    Category: [
        ColSpec(ColAlign.right, ColDataType.int, 'ID'),
        ColSpec(ColAlign.left, ColDataType.text, 'Tytuł'),
        ColSpec(ColAlign.right, ColDataType.int, 'Kolejność'),
        ColSpec(ColAlign.center, ColDataType.text, 'Nadrzędna'),
        ColSpec(ColAlign.center, ColDataType.text, 'Aktywna'),
    ],
    Page: [
        ColSpec(ColAlign.right, ColDataType.int, 'ID'),
        ColSpec(ColAlign.left, ColDataType.text, 'Tytuł'),
        ColSpec(ColAlign.center, ColDataType.text, 'Aktywna'),
        ColSpec(ColAlign.left, ColDataType.text, 'Kategorie'),
    ],
    User: [
        ColSpec(ColAlign.right, ColDataType.int, 'ID'),
        ColSpec(ColAlign.left, ColDataType.text, 'Nazwa'),
        ColSpec(ColAlign.left, ColDataType.text, 'Email'),
        ColSpec(ColAlign.center, ColDataType.text, 'Aktywne'),
        ColSpec(ColAlign.center, ColDataType.text, 'Administrator'),
    ]
}
