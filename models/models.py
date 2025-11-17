# models.py
import sqlite3
from utils.path_utils import get_db_path
DB_PATH = get_db_path() #r"Z:/pos_hipermarket/db/beta_sb_pos_sqlite.db"

def verify_user(username, password_hash):
    from utils.path_utils import get_db_path
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama, password FROM per_employee WHERE nama = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def load_customer_list():
    from utils.path_utils import get_db_path
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama, alamat_1, tlp_1 FROM per_customers")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "nama": row[1], "alamat_1": row[2], "tlp_1": row[3]} for row in rows]
