import os

# functions
from .help_functions import remove_ext
from .help_functions import create_dir
from .isothermal_components import isothermal_cmp
from .isothermal_components import isothermal_exp

# storing where resources folder is
resource_path = os.path.join(os.path.split(__file__)[0], "resources")