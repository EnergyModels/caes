import os

# functions
from .help_functions import remove_ext
from .help_functions import create_dir

# storing where resources folder is
resource_path = os.path.join(os.path.split(__file__)[0], "resources")