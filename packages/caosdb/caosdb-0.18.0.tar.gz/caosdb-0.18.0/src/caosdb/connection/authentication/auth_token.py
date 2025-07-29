
from linkahead.connection.authentication.auth_token import *
from warnings import warn

warn(("CaosDB was renamed to LinkAhead. Please import this library as `import linkahead.connection.authentication.auth_token`. Using the"
      " old name, starting with caosdb, is deprecated."), DeprecationWarning)
