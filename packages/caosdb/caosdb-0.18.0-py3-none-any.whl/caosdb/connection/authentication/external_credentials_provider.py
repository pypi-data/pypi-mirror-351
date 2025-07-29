
from linkahead.connection.authentication.external_credentials_provider import *
from warnings import warn

warn(("CaosDB was renamed to LinkAhead. Please import this library as `import linkahead.connection.authentication.external_credentials_provider`. Using the"
      " old name, starting with caosdb, is deprecated."), DeprecationWarning)
