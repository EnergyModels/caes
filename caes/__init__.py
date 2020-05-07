import os

# functions
from .help_functions import remove_ext
from .help_functions import create_dir
from .compressor_isothermal import isothermal_cmp
from .expander_isothermal import isothermal_exp
from .wellbore import wellbore

# storing where resources folder is
resource_path = os.path.join(os.path.split(__file__)[0], "resources")