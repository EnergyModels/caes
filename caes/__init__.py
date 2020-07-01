import os

# functions
from .help_functions import remove_ext
from .help_functions import create_dir
from .caes import CAES
from .icaes import ICAES
from .compressor_sizing import size_caes_cmp
from .turbine_sizing import size_caes_trb
from .plot_functions import plot_series
from .pressure_drop import aquifer_dp
from .pressure_drop import pipe_fric_dp
from .pressure_drop import pipe_grav_dp
from .pressure_drop import friction_coeff

# storing where resources folder is
resource_path = os.path.join(os.path.split(__file__)[0], "resources")