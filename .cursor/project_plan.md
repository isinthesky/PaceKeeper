# 프로젝트 계획 (PaceKeeper)

## 1. 환경 준비 및 진입점 확인
- [x] `requirements.txt` 확인: PyQt5 등 필수 패키지 명시됨
- [x] `pacekeeper/main.py` 확인: main 함수 및 진입점 정상 구현
- [x] Makefile 내 install, run 타겟 정상 구현 확인
- [x] 프로젝트 구조 점검 (requirements, main.py, Makefile 등)
- [x] 실제 make install, make run 실행 및 결과 확인 (정상 동작)

---

### 다음 단계
- 추가 기능 개발 또는 테스트 필요시 기록 

## 2024-06-XX
- create_dummy_data.py에서 태그 ID 리스트를 DB에 저장할 때 json.dumps(tag_ids, ensure_ascii=False) 옵션을 적용하여 한글이 유니코드 이스케이프가 아닌 실제 한글로 저장되도록 수정함.
- 기존 DB에 저장된 데이터는 삭제 후 재생성 필요. 