# app.spec
# letakkan file ini di samping app.py

block_cipher = None

from PyInstaller.utils.hooks import collect_submodules
hidden_imports = collect_submodules('views') + collect_submodules('controllers') + collect_submodules('utils')

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_data_files

# ambil semua data dari escpos (termasuk capabilities.json)
datas = collect_data_files('escpos')

mysql_locales = collect_data_files("mysql.connector.locales", include_py_files=True)
mysql_plugins = collect_data_files("mysql.connector.plugins", include_py_files=True)

binaries = [
    ('C:/Users/Beta/AppData/Roaming/Python/lib/site-packages/libmysql.dll', '.')
]
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=[
    ('resources/fonts/DejaVuSans.ttf', 'resources/fonts'),
    ('resources/styles/main.qss.css', 'resources/styles'),
    ('resources/setting_struk.csv', 'resources'),
    ('resources/printers.json', 'resources'),
    ('db/beta_sb_pos_sqlite.db', 'db'),
    *mysql_locales,
    *mysql_plugins,  # ⬅️ tambahkan ini agar auth plugin ikut terbundle
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='POSApp',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='POSApp'
)
