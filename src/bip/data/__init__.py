from collections import namedtuple


Filter = namedtuple('Filter', 'field,op,value,model', defaults=(None, None))
Sort = namedtuple(
    'Sort', 'field,direction,model,nullsfirst,nullslast',
    defaults=('asc', None, None, None),
)
