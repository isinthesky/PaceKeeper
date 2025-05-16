# PaceKeeper 사운드 재생 문제 해결

작성일: 2025년 5월 16일

## 문제 설명

macOS 빌드에서 "알람 재생 에러: Unknown WAVE format" 오류 발생

## 원인 분석

1. **파일 경로 문제**: PyInstaller 환경에서 리소스 파일 경로가 올바르게 해석되지 않음
2. **pygame.mixer 초기화 문제**: PyInstaller 환경에서 pygame.mixer가 제대로 초기화되지 않을 수 있음
3. **리소스 번들링 문제**: spec 파일에서 사운드 파일이 올바른 위치에 포함되지 않음

## 해결 방법

### 1. sound_manager.py 수정

```python
# pygame.mixer 초기화 최적화
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# PyInstaller 환경에서는 mixer.Sound 사용
if getattr(sys, 'frozen', False):
    sound = pygame.mixer.Sound(sound_file)
    sound.set_volume(volume)
    sound.play()
else:
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()
```

### 2. resource_path.py 개선

```python
def resource_path(relative_path):
    """PyInstaller 환경과 개발 환경에서 올바른 리소스 경로 반환"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # pacekeeper/ 접두사 처리
    if relative_path.startswith('pacekeeper/'):
        if not getattr(sys, 'frozen', False):
            full_path = os.path.join(base_path, relative_path)
        else:
            relative_path = relative_path.replace('pacekeeper/', '')
            full_path = os.path.join(base_path, relative_path)
    else:
        full_path = os.path.join(base_path, relative_path)
    
    return full_path
```

### 3. main_controller.py 수정

```python
# 절대 경로 대신 상대 경로 사용
self.sound_manager.play_sound("pacekeeper/assets/sounds/long_brk.wav")
self.sound_manager.play_sound("pacekeeper/assets/sounds/short_brk.wav")
```

### 4. spec 파일에 pygame.mixer 명시

```python
hiddenimports=[
    'pygame',
    'pygame.mixer',  # 명시적으로 추가
    'PyQt5',
    'sqlalchemy',
],
```

## 테스트 방법

1. 빌드 다시 실행: `make clean && make build`
2. 앱 실행: `open dist/PaceKeeper.app`
3. 타이머 동작 테스트로 알람 소리 확인

## 추가 고려사항

1. **사운드 파일 형식**: 모든 WAV 파일이 표준 PCM 형식인지 확인
2. **권한 문제**: macOS의 오디오 권한 설정 확인
3. **대체 방안**: PyGame 대신 PyQt5의 QSound 사용 고려

## 로깅 추가

디버그 로깅을 통해 정확한 파일 경로와 에러 추적:
- 파일 존재 여부
- 전체 경로
- 초기화 성공 여부
- 재생 성공 여부

## 향후 개선사항

1. 사운드 파일을 Base64로 인코딩하여 코드에 포함
2. PyQt5 QSound로 완전히 마이그레이션
3. 사운드 재생 실패 시 시각적 알림으로 대체