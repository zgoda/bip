import collections

VisibilityOptions = collections.namedtuple(
    'VisibilityOptions', ['authenticated', 'anonymous']
)

MenuItem = collections.namedtuple(
    'MenuItem', ['title', 'url', 'hide']
)
