import sqlite3
import re
import sqlite3
from utils.path_utils import get_db_path

# import sqlite3
# from utils.path_utils import get_db_path

def get_receive_on_account_debit():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT nama 
        FROM bank 
        WHERE nama LIKE '%EDC%'
    """)
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def get_debit_card_names():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT nama 
        FROM bank 
        WHERE nama NOT LIKE '%EDC%' 
          AND nama NOT LIKE '%Tunai%' 
          AND nama LIKE '%debit%'
    """)
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def get_receive_on_account_names():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT nama 
        FROM bank 
        WHERE nama LIKE '%EDC%'
    """)
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def get_credit_card_names():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT nama 
        FROM bank 
        WHERE nama NOT LIKE '%EDC%' 
          AND nama NOT LIKE '%Tunai%' 
          AND nama NOT LIKE '%debit%'
    """)
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def parse_int_safely(value):
    """
    Mengubah string yang mengandung angka, simbol %, Rp, spasi, dll. menjadi int.
    Contoh:
        "0 %"       -> 0
        "Rp 5.000"  -> 5000
        ""          -> 0
    """
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    # Hapus semua karakter non-digit
    digits_only = re.sub(r"[^\d]", "", str(value))
    return int(digits_only) if digits_only else 0

def get_ppn_from_profile(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ppn FROM company_profile LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            print(f'ambil nilai ppn di tabel company_profile  = {row[0]}')
            return str(row[0]) # str(row[0])  # harus string agar bisa setText()
    except Exception as e:
        print("Gagal ambil PPN dari company_profile:", e)
    return "10"  # fallback default
