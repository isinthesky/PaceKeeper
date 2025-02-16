import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Function to collect all files in a directory
def collect_all_files(src_dir, dest_dir):
    data_files = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            fullpath = os.path.join(root, file)
            relative_path = os.path.relpath(fullpath, src_dir)
            data_files.append((fullpath, os.path.join(dest_dir, relative_path)))
    return data_files

datas = [
        # Asset paths
        ('assets/icons/*.png', 'assets/icons'),
        ('assets/icons/*.ico', 'assets/icons'),
        ('assets/icons/*.icns', 'assets/icons'),
        ('assets/sounds/*.wav', 'assets/sounds'),
        ('config.json', '.'),
        # 언어 리소스 파일 추가
        ('pacekeeper/consts/lang_ko.json', 'pacekeeper/consts'),
        ('pacekeeper/consts/lang_en.json', 'pacekeeper/consts')
]

a = Analysis(
    ['pacekeeper/main.py'],           # Updated entry point
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pygame',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PaceKeeper',               # Updated name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icons/PaceKeeper.icns'  # Updated icon path
)

app = BUNDLE(
    exe,
    name='PaceKeeper.app',           # Updated bundle name
    icon='assets/icons/PaceKeeper.icns',
    bundle_identifier='com.pacekeeper.app',  # Added bundle identifier
)
