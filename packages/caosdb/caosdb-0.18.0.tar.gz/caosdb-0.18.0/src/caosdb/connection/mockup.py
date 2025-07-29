
from linkahead.connection.mockup import *
from warnings import warn

warn(("CaosDB was renamed to LinkAhead. Please import this library as `import linkahead.connection.mockup`. Using the"
      " old name, starting with caosdb, is deprecated."), DeprecationWarning)
