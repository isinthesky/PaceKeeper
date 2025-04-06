#!/bin/bash
# 스크립트에 실행 권한 부여

chmod +x run_prototype.sh
chmod +x validate_prototype.sh
chmod +x designer.sh

echo "실행 권한이 부여되었습니다. 다음 명령으로 프로토타입을 실행할 수 있습니다:"
echo "./run_prototype.sh     # 프로토타입 애플리케이션 실행"
echo "./validate_prototype.sh # 프로토타입 검증 실행"
echo "./designer.sh          # Qt Designer 실행"
