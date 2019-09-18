from ..models import ObjectMenuItem


def menu_items():
    q = ObjectMenuItem.query.filter_by(
        active=True
    ).order_by(ObjectMenuItem.menu_order, ObjectMenuItem.title)
    return q
