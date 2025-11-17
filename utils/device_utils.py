import platform
import socket
import uuid
import requests
import mysql.connector
from datetime import datetime
import sqlite3

import requests
# import requests
import json
import datetime
import pymysql


def post_device_registration(data):
    url = "https://beta.mayagrahakencana.com/main_sb/eusvc/NonRest/postDeviceRegistrasi"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        # Format waktu sekarang
        data["dtime_in"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["toko_id"] = 1001  # sesuai permintaan
        data["status"] = 1

        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()

        result = response.json()
        return result

    except requests.exceptions.RequestException as e:
        print("❌ Error submit registrasi:", e)
        return {"status": 0, "reason": str(e)}

def cek_device_ke_server(device_id):
    url = "https://beta.mayagrahakencana.com/main_sb/eusvc/NonRest/checkDevRegisV2"
    params = {'device_id': device_id}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        result = response.json()
        return result

    except requests.exceptions.RequestException as e:
        print("⚠️ Error checking device registration:", e)
        return {"status": 500, "reason": "Gagal konek ke server"}

def get_device_id():
    return str(uuid.getnode())


def get_ip_address():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "0.0.0.0"


def get_os_info():
    return platform.system() + " " + platform.release()


def get_com_info():
    return platform.node()


def get_cpu_info():
    return platform.processor()


def get_browser_verif():
    return "desktop"  # Karena berbasis aplikasi desktop


def get_gps_location():
    try:
        res = requests.get('https://ipinfo.io/json', timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("loc", "")
    except:
        return ""
    return ""


def cek_device_terdaftar(device_id):
    # conn = mysql.connector.connect(
    #     host='192.168.5.14',
    #     user='beta',
    #     password='beta556699',
    #     database='beta_main_sb_pos'
    # )
    # cursor = conn.cursor(dictionary=True)
    # ceknya bukan ke server tapi ke pos lokal
    print('masuk fungsi cek_device_terdaftar')
    # Koneksi SQLite
    import sys
    import os
    from utils.path_utils import get_db_path
    BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
    DB_PATH = get_db_path() #  os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
    print("DB Path device utils:", DB_PATH)
    # conn_sqlite = sqlite3.connect(db_path)

    conn = sqlite3.connect(DB_PATH)
    # conn = sqlite3.connect("z:/beta_desktop/db/beta_sb_pos_sqlite.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    print("SELECT * FROM per_cabang_device WHERE machine_id = ? AND status = 1 AND trash = 0", (device_id,))
    cursor.execute("SELECT * FROM per_cabang_device WHERE machine_id = ? AND status = 1 AND trash = 0", (device_id,))
     
    result = cursor.fetchone()
    conn.close()
    return result


def simpan_device_baru(
    device_id,
    alias,
    cabang_id,
    cabang_nama,
    nama,
    keterangan='',
    kelurahan='',
    kecamatan='',
    kabupaten='',
    propinsi='',
    alamat='',
    toko_id=1
):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # conn = mysql.connector.connect(
    #     host='192.168.5.14',
    #     user='beta',
    #     password='beta556699',
    #     database='beta_main_sb_pos'
    # )
    # def get_mysql_connection():
    conn = pymysql.connect(
        host="192.168.5.14",
        user="beta",
        password="beta556699",
        database="beta_main_sb_pos",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    query = """
    INSERT INTO per_cabang_device (
        last_update, machine_id, com_info, cpu_info, browser_verif, nama, alias, keterangan,
        cabang_id, cabang_nama, kelurahan, kecamatan, kabupaten, propinsi, alamat, toko_id,
        status, trash, jenis, dtime_in
    )
    VALUES (
        %(last_update)s, %(machine_id)s, %(com_info)s, %(cpu_info)s, %(browser_verif)s, %(nama)s, %(alias)s, %(keterangan)s,
        %(cabang_id)s, %(cabang_nama)s, %(kelurahan)s, %(kecamatan)s, %(kabupaten)s, %(propinsi)s, %(alamat)s, %(toko_id)s,
        %(status)s, %(trash)s, %(jenis)s, %(dtime_in)s
    )
    ON DUPLICATE KEY UPDATE 
        last_update = VALUES(last_update),
        alias = VALUES(alias),
        keterangan = VALUES(keterangan),
        cabang_id = VALUES(cabang_id),
        cabang_nama = VALUES(cabang_nama),
        alamat = VALUES(alamat)
    """
    data = {
        'last_update': now,
        'machine_id': device_id,
        'com_info': get_com_info(),
        'cpu_info': get_cpu_info(),
        'browser_verif': get_browser_verif(),
        'nama': nama,
        'alias': alias,
        'keterangan': keterangan,
        'cabang_id': cabang_id,
        'cabang_nama': cabang_nama,
        'kelurahan': kelurahan,
        'kecamatan': kecamatan,
        'kabupaten': kabupaten,
        'propinsi': propinsi,
        'alamat': alamat,
        'toko_id': toko_id,
        'status': 0,  # Pending approval
        'trash': 0,
        'jenis': 'POS',
        'dtime_in': now
    }
    cursor.execute(query, data)
    conn.commit()
    conn.close()
    return True
