
from linkahead.connection.authentication.plain import *
from warnings import warn

warn(("CaosDB was renamed to LinkAhead. Please import this library as `import linkahead.connection.authentication.plain`. Using the"
      " old name, starting with caosdb, is deprecated."), DeprecationWarning)
