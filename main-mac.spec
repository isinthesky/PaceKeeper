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

datas = []
# Collect icons
datas += collect_all_files('pacekeeper/assets/icons/', 'assets/icons')
# Collect sounds
datas += collect_all_files('pacekeeper/assets/sounds', 'assets/sounds')
# Include config.json
datas += [('pacekeeper/config.json', '.')]
# Include language files
datas += [('pacekeeper/consts/lang_ko.json', 'pacekeeper/consts')]
datas += [('pacekeeper/consts/lang_en.json', 'pacekeeper/consts')]

a = Analysis(
    ['pacekeeper/main.py'],            # Project entry point
    pathex=['.'],                      # Path to search for source code
    binaries=[],                       # Binary files
    datas=datas,                       # Data files
    hiddenimports=[
        'pygame',
        'PyQt5',
        'sqlalchemy',
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
    name='PaceKeeper',
    debug=False,                   # Disable debug messages
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                 # Hide console window
    icon='assets/icons/PaceKeeper.icns'  # Use .icns for macOS
)

app = BUNDLE(
    exe,
    name='PaceKeeper.app',
    icon='assets/icons/PaceKeeper.icns',
    bundle_identifier='com.pacekeeper.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',
        'LSEnvironment': {
            'DYLD_LIBRARY_PATH': '/opt/homebrew/lib:$DYLD_LIBRARY_PATH',
            'QT_MAC_WANTS_LAYER': '1'
        }
    }
)