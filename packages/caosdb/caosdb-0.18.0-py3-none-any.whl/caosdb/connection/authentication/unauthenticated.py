
from linkahead.connection.authentication.unauthenticated import *
from warnings import warn

warn(("CaosDB was renamed to LinkAhead. Please import this library as `import linkahead.connection.authentication.unauthenticated`. Using the"
      " old name, starting with caosdb, is deprecated."), DeprecationWarning)
