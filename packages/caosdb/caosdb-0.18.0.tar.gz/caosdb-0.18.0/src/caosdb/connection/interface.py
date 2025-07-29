
from linkahead.connection.interface import *
from warnings import warn

warn(("CaosDB was renamed to LinkAhead. Please import this library as `import linkahead.connection.interface`. Using the"
      " old name, starting with caosdb, is deprecated."), DeprecationWarning)
