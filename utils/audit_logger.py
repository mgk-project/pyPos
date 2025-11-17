import sqlite3
import platform
import socket
from datetime import datetime
import os

def get_device_info():
    return f"{platform.system()} {platform.release()} ({platform.machine()})"

def get_ip_address():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "unknown"

def log_audit(db_path, user_id, action, table_name, record_id, details="", location="local"):
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO audit_log (
                user_id, action, table_name, record_id,
                ip_address, device_info, location, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            action.upper(),
            table_name,
            record_id,
            get_ip_address(),
            get_device_info(),
            location,
            details
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        print("‼️ Gagal menyimpan audit log:", e)
