
from linkahead.common.versioning import *
from warnings import warn

warn(("CaosDB was renamed to LinkAhead. Please import this library as `import linkahead.common.versioning`. Using the"
      " old name, starting with caosdb, is deprecated."), DeprecationWarning)
