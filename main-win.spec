# main.spec
# PyInstaller spec file for building the BreakTrack application

# (1) 필요하면 추가로 import할 모듈들:
# import PyInstaller.utils.hooks
# etc.

block_cipher = None

a = Analysis(
    # 프로젝트의 진입점(엔트리 스크립트)
    ['breaktrack/main.py'],
    
    # pyinstaller가 소스코드를 탐색할 경로
    pathex=['.'],

    # C/C++ 동적 라이브러리(.dll/.so 등) - 여기서는 별도 지정 없이 기본값
    binaries=[],

    # (2) 데이터(아이콘, 사운드, 설정 파일 등)를 파이썬 실행 파일에 포함
    #   (상대 경로, 타겟 내부 경로) 형식으로 지정
    datas=[
        # 아이콘 파일들
        ('breaktrack/assets/icons/BreakTrack.ico', 'assets/icons'),
        ('breaktrack/assets/icons/BreakTrack.png', 'assets/icons'),
        ('breaktrack/assets/icons/BreakTrack.icns', 'assets/icons'),

        # 사운드 파일들
        ('breaktrack/assets/sounds/long_brk.wav', 'assets/sounds'),
        ('breaktrack/assets/sounds/short_brk.wav', 'assets/sounds'),

        # 설정 파일(config.json)  
        # (코드에서 'config.json' 을 루트 경로로 사용하므로, 
        #  빌드 후 실행 시에도 같은 위치(혹은 적절한 상대 위치)에 있도록 조정)
        ('breaktrack/config.json', '.'),

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
    a.scripts,       # 이 애플리케이션 실행에 필요한 스크립트
    a.binaries,      # 바이너리
    a.zipfiles,      # zip형식으로 넣은 라이브러리들
    a.datas,         # 데이터
    [],
    name='BreakTrack',      # 빌드 후 exe 이름 (예: BreakTrack.exe)
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # 콘솔창 숨김 (GUI 앱이므로)
    icon='breaktrack/assets/icons/BreakTrack.ico'  # exe 아이콘
)


# ----- (4-1) 단일 파일(OneFile)로 만들기 -----
#  아래와 같이 하면, 빌드 결과가 exe 단일 파일로 생성
#  하지만 리소스 용량이 큰 경우 로딩 지연이 있을 수 있음
#
# exe = EXE(
#     pyz,
#     a.scripts,
#     ...
#     name='BreakTrack',
#     debug=False,
#     strip=False,
#     upx=True,
#     console=False,
#     icon='breaktrack/assets/icons/BreakTrack.ico',
# )


# ----- (4-2) 폴더 구조로 수집(COLLECT) -----
#  빌드 결과물이 dist/BreakTrack/ 폴더 형태로 생성되어,
#  exe + 필요한 데이터들이 폴더에 모여 배포. 로딩 속도가 조금 빠를 수 있음.
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='BreakTrack'
)