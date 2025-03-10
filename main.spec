# main.spec
# PyInstaller spec file for building the BreakTrack application

# (1) 필요하면 추가로 import할 모듈들:
import os
# import PyInstaller.utils.hooks
# etc.

# 배포 모드 설정 (MINUTE_TO_SECOND = 60)
os.environ['PACEKEEPER_DEV_MODE'] = '0'

block_cipher = None

a = Analysis(
    # 프로젝트의 진입점(엔트리 스크립트)
    ['pacekeeper/main.py'],
    
    # pyinstaller가 소스코드를 탐색할 경로
    pathex=['.'],

    # C/C++ 동적 라이브러리(.dll/.so 등) - 여기서는 별도 지정 없이 기본값
    binaries=[],

    # (2) 데이터(아이콘, 사운드, 설정 파일 등)를 파이썬 실행 파일에 포함
    #   (상대 경로, 타겟 내부 경로) 형식으로 지정
    datas=[
        # 아이콘 파일들
        ('pacekeeper/assets/icons/pacekeeper.ico', 'assets/icons'),
        ('pacekeeper/assets/icons/pacekeeper.png', 'assets/icons'),
        ('pacekeeper/assets/icons/pacekeeper.icns', 'assets/icons'),

        # 사운드 파일들
        ('pacekeeper/assets/sounds/long_brk.wav', 'assets/sounds'),
        ('pacekeeper/assets/sounds/short_brk.wav', 'assets/sounds'),

        # 언어 리소스 파일
        ('pacekeeper/consts/lang_ko.json', 'pacekeeper/consts'),
        ('pacekeeper/consts/lang_en.json', 'pacekeeper/consts'),

        # 설정 파일(config.json)  
        # (코드에서 'config.json' 을 루트 경로로 사용하므로, 
        #  빌드 후 실행 시에도 같은 위치(혹은 적절한 상대 위치)에 있도록 조정)
        ('pacekeeper/config.json', '.'),
        
        # 데이터베이스 파일 (없는 경우 생성됨)
        # 기존 DB 파일이 있다면 포함, 없으면 빈 파일 생성
        ('pacekeeper/pace_log.db', '.') if os.path.exists('pacekeeper/pace_log.db') else ('README.md', '.'),

        # 그 밖에 필요한 다른 파일이 있다면 이곳에 추가...
    ],

    # 파이썬 소스 상에서 임포트한 적이 있으나 PyInstaller가 자동으로
    # 찾지 못하는 모듈이 있다면 아래에 기재
    hiddenimports=[
        # 'pygame',  # 예: pygame이 자동으로 인식되지 않으면 추가
    ],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    
    # Windows 배포 시 관련 설정
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

# (3) exe (단일 실행파일) or (4) COLLECT (폴더 구조) 선택
# - console=False이면 터미널 창 없이 GUI 앱으로 실행됨(windows)
# - icon 매개변수로 exe 아이콘 지정 (Windows 환경)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PaceKeeper',      # 빌드 후 exe 이름 (예: pacekeeper.exe)
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # 콘솔창 숨김 (GUI 앱이므로)
    icon='pacekeeper/assets/icons/pacekeeper.ico'  # exe 아이콘
)


# ----- (4-1) 단일 파일(OneFile)로 만들기 -----
#  아래와 같이 하면, 빌드 결과가 exe 단일 파일로 생성
#  하지만 리소스 용량이 큰 경우 로딩 지연이 있을 수 있음
#
# exe = EXE(
#     pyz,
#     a.scripts,
#     ...
#     name='pacekeeper',
#     debug=False,
#     strip=False,
#     upx=True,
#     console=False,
#     icon='pacekeeper/assets/icons/pacekeeper.ico',
# )


# ----- (4-2) 폴더 구조로 수집(COLLECT) -----
#  빌드 결과물이 dist/pacekeeper/ 폴더 형태로 생성되어,
#  exe + 필요한 데이터들이 폴더에 모여 배포. 로딩 속도가 조금 빠를 수 있음.
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='PaceKeeper'
)