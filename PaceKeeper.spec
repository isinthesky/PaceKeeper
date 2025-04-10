# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# 테마 파일 경로
themes_path = os.path.join('app', 'views', 'styles', 'themes')
themes_files = []
if os.path.exists(themes_path):
    for theme_file in os.listdir(themes_path):
        if theme_file.endswith('.qss'):
            themes_files.append((os.path.join(themes_path, theme_file), 
                               os.path.join('app', 'views', 'styles', 'themes')))

# 아이콘 파일 경로
icon_path = os.path.join('app', 'assets', 'icons')
icon_files = []
if os.path.exists(icon_path):
    for icon_file in os.listdir(icon_path):
        if icon_file.endswith(('.ico', '.png', '.icns')):
            icon_files.append((os.path.join(icon_path, icon_file),
                             os.path.join('app', 'assets', 'icons')))

# 데이터 파일 결합
all_datas = [
    ('config.json', '.'),
]
all_datas.extend(themes_files)
all_datas.extend(icon_files)

a = Analysis(
    ['app/main_responsive.py'],
    pathex=[],
    binaries=[],
    datas=all_datas,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'app.views.styles.advanced_theme_manager',
        'app.views.styles.widget_helpers',
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
    icon='app/assets/icons/pacekeeper.ico' if os.path.exists('app/assets/icons/pacekeeper.ico') else None,
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

# 빌드 관련 노트:
# 1. 테마 파일이 app/views/styles/themes 디렉토리에 포함됩니다.
# 2. 아이콘 파일이 app/assets/icons 디렉토리에 포함됩니다.
# 3. PyQt6 모듈이 hiddenimports에 명시적으로 포함됩니다.
# 4. widget_helpers 모듈도 hiddenimports에 포함되었습니다.
