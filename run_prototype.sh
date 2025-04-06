#!/bin/bash
# PaceKeeper Qt 프로토타입 실행 스크립트

# 가상 환경 활성화
source ./venv/bin/activate

# PYTHONPATH 설정 (패키지 임포트 경로 설정)
export PYTHONPATH=$(pwd)

# 프로토타입 애플리케이션 실행
python prototype/main.py
