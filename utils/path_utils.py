# utils/path_utils.py
import os
import sys

def get_project_base_dir():
    return getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.argv[0])))

def get_db_path():
    return os.path.join(get_project_base_dir(), 'db', 'beta_sb_pos_sqlite.db')
