from pathlib import Path
import os
from spacy.util import load_model_from_init_py, get_model_meta

# Xác định đường dẫn model dựa trên vị trí thực tế của file đang chạy
base_dir = os.path.dirname(os.path.abspath(__file__))  
model_path = Path(base_dir)

# Lấy thông tin version
__version__ = get_model_meta(model_path)['version']

def load(**overrides):
    return load_model_from_init_py(str(model_path), **overrides)
