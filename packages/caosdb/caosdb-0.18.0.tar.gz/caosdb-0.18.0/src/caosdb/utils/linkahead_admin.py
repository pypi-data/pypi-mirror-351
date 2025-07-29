
from linkahead.utils.linkahead_admin import *
from warnings import warn

warn(("CaosDB was renamed to LinkAhead. Please import this library as `import linkahead.utils.linkahead_admin`. Using the"
      " old name, starting with caosdb, is deprecated."), DeprecationWarning)
