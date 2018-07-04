from .base_settings import *

try:
    from .development_settings import *
except:
    pass

try:
    from .production_settings import *
except:
    pass
