#!/bin/bash
# PaceKeeper Qt 프로토타입 검증 스크립트 실행

# 가상 환경 활성화
source ./venv/bin/activate

# PYTHONPATH 설정 (패키지 임포트 경로 설정)
export PYTHONPATH=$(pwd)

# 프로토타입 검증 스크립트 실행
python app/prototype_validation.py
