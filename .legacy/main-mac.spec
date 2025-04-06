import os
from PyInstaller.utils.hooks import collect_all

# 배포 모드 설정 (MINUTE_TO_SECOND = 60)
os.environ['PACEKEEPER_DEV_MODE'] = '0'

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

datas = []
# Collect icons
datas += collect_all_files('breaktrack/assets/icons/', 'assets/icons')
# Collect sounds
datas += collect_all_files('breaktrack/assets/sounds', 'assets/sounds')
# Include config.json
datas += [('breaktrack/config.json', '.')]

a = Analysis(
    ['breaktrack/main.py'],            # Project entry point
    pathex=['.'],                      # Path to search for source code
    binaries=[],                       # Binary files
    datas=datas,                       # Data files
    hiddenimports=[
        'pygame',                       # Uncomment if pygame is not auto-detected
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
    name='BreakTrack',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                  # Hide console window (GUI app)
    icon='assets/icons/BreakTrack.icns'  # Use .icns for macOS
)

app = BUNDLE(
    exe,
    name='BreakTrack.app',
    icon='assets/icons/BreakTrack.icns',
    bundle_identifier=None,
)
