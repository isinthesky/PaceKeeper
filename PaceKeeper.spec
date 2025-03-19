# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pacekeeper/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('pacekeeper/consts/lang_ko.json', 'pacekeeper/consts'),
        ('pacekeeper/consts/lang_en.json', 'pacekeeper/consts'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PaceKeeper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/pacekeeper.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PaceKeeper',
)

# DB 파일 (pace_log.db)과 설정 파일 (config.json)을 번들에서 제외하고 
# 외부에 저장하기 위한 컴파일 전략:
# PaceKeeper 코드는 이미 resource_path 함수를 통해 
# 운영체제별 적절한 사용자 디렉토리에 이 파일들을 저장합니다.
# 
# - Windows: %APPDATA%\PaceKeeper\
# - macOS: ~/Library/Application Support/PaceKeeper/
# - Linux: ~/.pacekeeper/
