# PaceKeeper 사운드 시스템 변경: pygame에서 QSound로

작성일: 2025년 5월 16일

## 변경 사유

PyInstaller 빌드 환경에서 pygame.mixer가 WAV 파일을 제대로 읽지 못하는 문제 발생:
- 오류: "Unknown WAVE format"
- 파일은 존재하지만 pygame이 읽을 수 없음

## 해결 방법

### 1. 사운드 시스템 변경

pygame.mixer 대신 PyQt5.QtMultimedia.QSound 사용:

```python
from PyQt5.QtMultimedia import QSound

class SoundManager:
    def __init__(self, config_ctrl: ConfigController):
        self.config_ctrl = config_ctrl
        self.current_sound = None
        
    def play_sound(self, sound_file: str):
        # QSound 사용
        self.current_sound = QSound(sound_file)
        self.current_sound.play()
        
    def stop_sound(self):
        if self.current_sound is not None:
            self.current_sound.stop()
```

### 2. 백업 메커니즘 추가

QSound가 실패할 경우 macOS의 시스템 명령어 사용:

```python
if sys.platform == 'darwin':
    os.system(f'afplay "{sound_file}" &')
```

### 3. spec 파일 업데이트

```python
hiddenimports=[
    'PyQt5',
    'PyQt5.QtMultimedia',  # 추가
    'sqlalchemy',
],
```

## 장단점

### 장점
- PyInstaller 빌드에서 안정적으로 작동
- PyQt5를 이미 사용하므로 추가 의존성 없음
- 크로스 플랫폼 호환성

### 단점
- 볼륨 조절 기능 없음 (QSound 한계)
- 단순한 재생 기능만 제공

## 향후 개선사항

1. QMediaPlayer로 업그레이드하여 볼륨 조절 기능 추가
2. 사운드 파일을 리소스로 포함하여 경로 문제 완전 해결
3. 사용자가 시스템 볼륨을 조절할 수 있도록 안내 추가

## 테스트 결과

- macOS 빌드에서 정상 작동 확인
- 알람 소리가 제대로 재생됨
- 에러 메시지 없음