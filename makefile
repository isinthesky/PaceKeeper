.PHONY: help setup venv install run run-prod clean add remove designer lint build format

# 기본 변수 설정
PYTHON := python3.12
PIP := python3.12 -m pip
PROJECT_DIR := $(shell pwd)
VENV_DIR := $(PROJECT_DIR)/venv
PYTHONPATH := $(PROJECT_DIR)

# 도움말 표시
help:
	@echo "PaceKeeper Qt 마이그레이션 Makefile"
	@echo ""
	@echo "사용 가능한 명령어:"
	@echo "  make setup         : 가상 환경 생성 및 의존성 설치"
	@echo "  make venv          : Python 가상 환경 생성"
	@echo "  make install       : 필요한 패키지 설치"
	@echo "  make run           : 애플리케이션 실행"
	@echo "  make build         : 애플리케이션 배포 파일 빌드"
	@echo "  make lint          : 코드 정적 분석 및 오류 검사"
	@echo "  make format        : 코드 자동 포맷팅"
	@echo "  make clean         : 생성된 캐시 및 임시 파일 정리"
	@echo "  make add 패키지명    : 특정 패키지 설치"
	@echo "  make remove 패키지명 : 특정 패키지 제거"

# 전체 설정 (가상 환경 + 의존성 설치)
setup: venv install

# 가상 환경 생성
venv:
	@echo "가상 환경 생성 중..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "가상 환경이 생성되었습니다."; \
	else \
		echo "가상 환경이 이미 존재합니다."; \
	fi

# 의존성 패키지 설치
install: venv
	@echo "의존성 패키지 설치 중..."
	@. $(VENV_DIR)/bin/activate && $(PIP) install -r $(PROJECT_DIR)/requirements.txt

# Qt 애플리케이션 실행
run: venv
	@echo "PaceKeeper 애플리케이션 실행 중..."
	@. $(VENV_DIR)/bin/activate && \
	export PYTHONPATH=$(PYTHONPATH) && \
	python app/main_responsive.py

# 코드 정적 분석 및 오류 검사
lint: venv
	@echo "코드 정적 분석 및 오류 검사 중..."
	@. $(VENV_DIR)/bin/activate && \
	$(PIP) install flake8 pylint ruff && \
	echo "flake8 검사 중..." && \
	flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics && \
	echo "pylint 검사 중..." && \
	pylint --disable=C0111,C0103,C0303,W0613,R0903,W0212,R0913,R0914 app/ && \
	echo "ruff 검사 중..." && \
	ruff check app/
	@echo "코드 정적 분석 완료!"

# 코드 포맷팅
format: venv
	@echo "코드 포맷팅 중..."
	@. $(VENV_DIR)/bin/activate && \
	$(PIP) install black isort && \
	black app tests && \
	isort app tests
	@echo "코드 포맷팅 완료!"

# 캐시 및 임시 파일 정리
clean:
	@echo "캐시 및 임시 파일 정리 중..."
	@find $(PROJECT_DIR) -type d -name "__pycache__" -exec rm -rf {} +
	@find $(PROJECT_DIR) -type d -name "*.egg-info" -exec rm -rf {} +
	@find $(PROJECT_DIR) -type f -name "*.pyc" -delete
	@find $(PROJECT_DIR) -type f -name "*.pyo" -delete
	@find $(PROJECT_DIR) -type f -name "*.pyd" -delete
	@find $(PROJECT_DIR) -type f -name ".DS_Store" -delete
	@find $(PROJECT_DIR) -type d -name "*.egg-info" -exec rm -rf {} +
	@find $(PROJECT_DIR) -type d -name "*.egg" -exec rm -rf {} +
	@find $(PROJECT_DIR) -type d -name ".pytest_cache" -exec rm -rf {} +
	@find $(PROJECT_DIR) -type d -name ".ruff_cache" -exec rm -rf {} +
	@echo "캐시 및 임시 파일 정리 완료!"

# 추가 라이브러리 설치
add: venv
	@echo "라이브러리 설치 중..."
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "사용법: make add 패키지명"; \
		exit 1; \
	fi
	@. $(VENV_DIR)/bin/activate && $(PIP) install $(filter-out $@,$(MAKECMDGOALS))
	@echo "$(filter-out $@,$(MAKECMDGOALS)) 라이브러리 설치 완료!"
	@echo "$(filter-out $@,$(MAKECMDGOALS))" >> $(PROJECT_DIR)/requirements.txt
	@echo "$(filter-out $@,$(MAKECMDGOALS)) 라이브러리가 requirements.txt에 추가되었습니다."

# 라이브러리 제거
remove: venv
	@echo "라이브러리 제거 중..."
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "사용법: make remove 패키지명"; \
		exit 1; \
	fi
	@. $(VENV_DIR)/bin/activate && $(PIP) uninstall -y $(filter-out $@,$(MAKECMDGOALS))
	@echo "$(filter-out $@,$(MAKECMDGOALS)) 라이브러리 제거 완료!"
	@grep -v "^$(filter-out $@,$(MAKECMDGOALS))$$" "$(PROJECT_DIR)/requirements.txt" > "$(PROJECT_DIR)/requirements.txt.tmp" && \
	mv "$(PROJECT_DIR)/requirements.txt.tmp" "$(PROJECT_DIR)/requirements.txt"

# 빌드 (PyInstaller 사용)
build: venv
	@echo "애플리케이션 빌드 중..."
	@. $(VENV_DIR)/bin/activate && \
	$(PIP) install pyinstaller && \
	export PYTHONPATH=$(PYTHONPATH) && \
	if [ ! -f "$(PROJECT_DIR)/PaceKeeper.spec" ]; then \
		echo "빌드 스펙 파일 생성 중..." && \
		pyinstaller --name PaceKeeper --windowed --noconfirm \
		--add-data "$(PROJECT_DIR)/app/views/styles/themes:themes" \
		--paths "$(PROJECT_DIR)" \
		--hidden-import="PyQt6.QtCore" \
		--hidden-import="PyQt6.QtGui" \
		--hidden-import="PyQt6.QtWidgets" \
		"$(PROJECT_DIR)/app/main_responsive.py"; \
	else \
		echo "기존 스펙 파일을 사용합니다." && \
		pyinstaller "$(PROJECT_DIR)/PaceKeeper.spec"; \
	fi
	@echo "빌드 완료! dist/PaceKeeper 폴더에서 실행 파일을 확인하세요."

# 빌드 스펙 파일 생성
spec: venv
	@echo "빌드 스펙 파일 생성 중..."
	@. $(VENV_DIR)/bin/activate && \
	$(PIP) install pyinstaller && \
	export PYTHONPATH=$(PYTHONPATH) && \
	pyinstaller --name PaceKeeper --windowed \
	--add-data "$(PROJECT_DIR)/app/views/styles/themes:themes" \
	--paths "$(PROJECT_DIR)" \
	--hidden-import="PyQt6.QtCore" \
	--hidden-import="PyQt6.QtGui" \
	--hidden-import="PyQt6.QtWidgets" \
	"$(PROJECT_DIR)/app/main_responsive.py" --debug
	@echo "빌드 스펙 파일 생성 완료!"

%:
	@:
