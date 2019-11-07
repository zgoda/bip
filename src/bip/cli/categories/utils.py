import click

from ...data import category
from ...models import Category


def check_category(pk: int, fail: bool = True, message: str = None) -> Category:
    obj = category.get(pk)
    if obj is None and fail:
        if message is None:
            message = 'Nie znaleziono kategorii o ID {pk}'
        raise click.ClickException(message.format(pk=pk))
    return obj


def check_parent(obj: Category, parent_pk: int, fail: bool = True) -> Category:
    parent = check_category(
        parent_pk, message='Nie znaleziono kategorii nadrzędnej o ID {pk}'
    )
    if parent == obj and fail:
        raise click.ClickException(
            'Kategoria nie może być nadrzędna wobec samej siebie'
        )
    return parent
