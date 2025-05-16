# PaceKeeper Makefile
# 프로젝트 관리, 빌드, 실행을 위한 스크립트

# 기본 설정
SHELL := /bin/bash

# 플랫폼 감지
ifeq ($(OS),Windows_NT)
	PLATFORM := windows
	SPEC_FILE := main-win.spec
	EXE_EXT := .exe
	PYTHON := python
	PIP := pip
	VENV_ACTIVATE := $(VENV)\Scripts\activate
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Darwin)
		PLATFORM := macos
		SPEC_FILE := main-mac.spec
		EXE_EXT :=
		# macOS에서는 python3, pip3 사용
		PYTHON := python3
		PIP := pip3
		VENV_ACTIVATE := . ./$(VENV)/bin/activate
	else
		PLATFORM := linux
		SPEC_FILE := main.spec
		EXE_EXT :=
		# Linux에서는 환경에 따라 python 또는 python3
		PYTHON := python3
		PIP := pip3
		VENV_ACTIVATE := . ./$(VENV)/bin/activate
	endif
endif

# 가상 환경 경로 및 명령어 설정
VENV := venv
PYTHON_COMMAND := $(PYTHON)
PIP_COMMAND := $(PIP)

# 가상 환경이 활성화된 경우 경로 재설정
ifneq (,$(wildcard $(VENV)/.))
	ifeq ($(OS),Windows_NT)
		PYTHON_COMMAND := $(VENV)\Scripts\python
		PIP_COMMAND := $(VENV)\Scripts\pip
	else
		PYTHON_COMMAND := ./$(VENV)/bin/python
		PIP_COMMAND := ./$(VENV)/bin/pip
	endif
endif

# 디렉토리 설정
SRC_DIR := pacekeeper
OUTPUT_DIR := dist
BUILD_DIR := build
DOCS_DIR := docs

# 의존성 파일 설정
REQUIREMENTS := requirements.txt
REQUIREMENTS_DEV := requirements-dev.txt

# 실행파일 이름
APP_NAME := PaceKeeper

# 툴 명령어 설정
PYINSTALLER := pyinstaller
RUFF := ruff
VULTURE := vulture

# 기본 타겟
.PHONY: help
help:
	@echo "PaceKeeper 프로젝트 관리 스크립트"
	@echo "사용법: make [타겟]"
	@echo ""
	@echo "주요 타겟:"
	@echo "  run         - 개발 환경에서 애플리케이션 실행"
	@echo "  venv        - 가상 환경 생성"
	@echo "  install     - 의존성 설치"
	@echo "  install-dev - 개발 의존성 포함 설치"
	@echo "  build       - 실행 가능한 애플리케이션 빌드 ($(PLATFORM)용)"
	@echo "  clean       - 빌드 결과물 및 캐시 파일 정리"
	@echo "  lint        - 코드 문법 및 스타일 검사"
	@echo "  lint-fix    - 코드 문법 및 스타일 자동 수정"
	@echo "  dead-code   - 사용되지 않는 코드 검사"
	@echo "  docs        - 문서 확인"
	@echo "  merge-code  - 코드 병합 (코드 리뷰용)"
	@echo "  dummy-data  - 테스트용 더미 데이터 생성"
	@echo ""
	@echo "환경 정보:"
	@echo "  플랫폼: $(PLATFORM)"
	@echo "  스펙 파일: $(SPEC_FILE)"
	@echo "  Python 명령어: $(PYTHON)"
	@echo "  가상 환경 Python: $(PYTHON_COMMAND)"

# 가상 환경 생성
.PHONY: venv
venv:
	@echo "가상 환경 생성 중..."
	$(PYTHON) -m venv $(VENV)
	@echo "가상 환경 생성 완료: $(VENV)"

# 애플리케이션 실행
.PHONY: run
run:
	@echo "애플리케이션 실행 중..."
	$(PYTHON_COMMAND) -m $(SRC_DIR).main

# 의존성 설치
.PHONY: install
install: venv
	@echo "기본 의존성 설치 중..."
	$(PIP_COMMAND) install -U pip
	$(PIP_COMMAND) install -r $(REQUIREMENTS)
	@echo "의존성 설치 완료"

# 개발 의존성 설치
.PHONY: install-dev
install-dev: venv
	@echo "개발 의존성 설치 중..."
	$(PIP_COMMAND) install -U pip
	$(PIP_COMMAND) install -r $(REQUIREMENTS_DEV)
	@echo "개발 의존성 설치 완료"

# 애플리케이션 빌드
.PHONY: build
build: install
	@echo "$(PLATFORM)용 배포 파일 빌드 중..."
	$(PYTHON_COMMAND) -m $(PYINSTALLER) $(SPEC_FILE) --clean --noconfirm
	@echo "빌드 완료: $(OUTPUT_DIR)/$(APP_NAME)$(EXE_EXT)"

# 특정 플랫폼용 빌드
.PHONY: build-macos
build-macos: install
	@echo "macOS용 빌드 중..."
	$(PYTHON_COMMAND) -m $(PYINSTALLER) main-mac.spec --clean --noconfirm
	@echo "macOS 빌드 완료: $(OUTPUT_DIR)/$(APP_NAME).app"

.PHONY: build-windows
build-windows: install
	@echo "Windows용 빌드 중..."
	$(PYTHON_COMMAND) -m $(PYINSTALLER) main-win.spec --clean --noconfirm
	@echo "Windows 빌드 완료: $(OUTPUT_DIR)/$(APP_NAME)/$(APP_NAME).exe"

# 코드 린트 검사
.PHONY: lint
lint: install-dev
	@echo "코드 린트 검사 중..."
	$(PYTHON_COMMAND) -m $(RUFF) check $(SRC_DIR)

# 코드 린트 자동 수정
.PHONY: lint-fix
lint-fix: install-dev
	@echo "코드 린트 자동 수정 중..."
	$(PYTHON_COMMAND) -m $(RUFF) check --fix $(SRC_DIR)

# 미사용 코드 검사
.PHONY: dead-code
dead-code: install-dev
	@echo "미사용 코드 검사 중..."
	$(PYTHON_COMMAND) -m $(VULTURE) $(SRC_DIR)

# 코드 병합 (코드 리뷰용)
.PHONY: merge-code
merge-code: venv
	@echo "코드 병합 중..."
	@mkdir -p $(OUTPUT_DIR)
	$(PYTHON_COMMAND) merge_files.py
	@echo "코드 병합 완료"

# 문서 확인
.PHONY: docs
docs:
	@echo "문서 디렉토리: $(DOCS_DIR)"
	@ls -la $(DOCS_DIR)

# 더미 데이터 생성
.PHONY: dummy-data
dummy-data: install
	@echo "테스트용 더미 데이터 생성 중..."
	$(PYTHON_COMMAND) create_dummy_data.py

# 빌드 결과물 및 캐시 파일 정리
.PHONY: clean
clean:
	@echo "빌드 결과물 및 캐시 파일 정리 중..."
	rm -rf $(BUILD_DIR) $(OUTPUT_DIR) *.spec
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	@echo "정리 완료"

# 전체 정리 (가상 환경 포함)
.PHONY: clean-all
clean-all: clean
	@echo "가상 환경 정리 중..."
	rm -rf $(VENV)
	@echo "모든 캐시 및 가상 환경 정리 완료"

# entry.py 스크립트 생성 (파이썬 파일로 직접 실행하기 위한 스크립트)
.PHONY: entry
entry:
	@echo "#!/usr/bin/env python3" > entry.py
	@echo "from pacekeeper.main import main" >> entry.py
	@echo "" >> entry.py
	@echo "if __name__ == '__main__':" >> entry.py
	@echo "    main()" >> entry.py
	@chmod +x entry.py
	@echo "entry.py 스크립트 생성 완료"