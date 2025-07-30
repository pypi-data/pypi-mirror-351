"""the_utils
"""

__version__ = "0.9.0"

from .bot import notify
from .plt import draw_chart
from .common import *
from .file import refresh_file, make_parent_dirs, csv2file, save_to_csv_files, csv_to_table
from .setting import set_device, set_seed
from .save_load import (
    load_model,
    save_model,
    get_modelfile_path,
    check_modelfile_exists,
    save_embedding,
)
from .evaluation import *
