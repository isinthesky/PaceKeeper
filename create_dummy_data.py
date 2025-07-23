#!/usr/bin/env python3
# create_dummy_data.py
# PaceKeeper 테스트용 더미 데이터 생성 스크립트

import datetime
import json
import os
import random
import sqlite3
import sys

# 직접 실행 시 패키지 경로 설정
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pacekeeper.consts.settings import DB_FILE
from pacekeeper.repository.category_repository import CategoryRepository
from pacekeeper.repository.entities import Category, Log, Tag
from pacekeeper.repository.log_repository import LogRepository
from pacekeeper.repository.tag_repository import TagRepository
from pacekeeper.utils.functions import extract_tags

# 카테고리 더미 데이터
CATEGORIES = [
    {"name": "업무", "description": "회사 관련 업무", "color": "#FF9AA2"},
    {"name": "학습", "description": "공부 및 자기계발", "color": "#FFB7B2"},
    {"name": "프로젝트", "description": "개인 및 팀 프로젝트", "color": "#FFDAC1"},
    {"name": "일상", "description": "일상 생활 관련 활동", "color": "#E2F0CB"},
    {"name": "건강", "description": "운동, 식단 등 건강 관련", "color": "#B5EAD7"},
    {"name": "취미", "description": "취미 활동 관련", "color": "#C7CEEA"}
]

# 태그 생성을 위한 예시 단어 목록
TAG_WORDS = {
    "업무": ["이메일", "회의", "보고서", "기획", "전화", "미팅", "고객응대", "문서작업", "HR", "마케팅"],
    "학습": ["프로그래밍", "책읽기", "강의", "영어", "수학", "알고리즘", "데이터분석", "통계", "논문", "자격증"],
    "프로젝트": ["개발", "설계", "코딩", "테스트", "기획", "회의", "문서화", "리팩토링", "디버깅", "배포"],
    "일상": ["청소", "요리", "쇼핑", "식사", "정리", "세탁", "은행", "관공서", "대화", "계획"],
    "건강": ["달리기", "요가", "헬스", "명상", "수영", "영양", "스트레칭", "산책", "조깅", "자전거"],
    "취미": ["영화", "게임", "여행", "음악", "그림", "사진", "독서", "요리", "원예", "악기"]
}

# 로그 메시지 템플릿
LOG_MESSAGE_TEMPLATES = [
    "{tag1} {activity} 진행",
    "{tag1} {activity} 완료",
    "{tag1}, {tag2} 관련 {activity}",
    "{activity} - {tag1}",
    "{tag1} {activity} 중 {tag2} 작업",
    "{activity}와 관련된 {tag1}",
    "{tag1} 분야 {activity} 수행",
    "{activity} 하면서 {tag1} 정리",
    "{tag1}와 {tag2} {activity} 병행",
    "{tag1} 위주의 {activity}",
]

# 활동 예시
ACTIVITIES = {
    "업무": ["업무 처리", "자료 준비", "회의 참석", "보고서 작성", "계획 수립", "이메일 확인", "전화 응대", "고객 미팅", "자료 분석", "프레젠테이션 준비"],
    "학습": ["공부", "학습", "강의 듣기", "책 읽기", "필기", "연습", "복습", "문제 풀이", "정리", "과제 제출"],
    "프로젝트": ["개발", "코딩", "설계", "기획", "문서화", "테스트", "디버깅", "회의", "검토", "발표"],
    "일상": ["정리", "청소", "요리", "쇼핑", "계획 세우기", "정리정돈", "메모", "준비", "연락", "일정 관리"],
    "건강": ["운동", "트레이닝", "스트레칭", "휴식", "명상", "식단 관리", "계획 수립", "기록", "준비", "마무리"],
    "취미": ["감상", "연습", "참여", "체험", "감상", "탐색", "수집", "정리", "준비", "계획"]
}

def create_dummy_categories() -> list[Category]:
    """6개의 더미 카테고리를 생성하고 반환합니다."""
    print("카테고리 생성 중...")
    category_repo = CategoryRepository()
    categories = []

    for cat_data in CATEGORIES:
        category = category_repo.add_category(
            name=cat_data["name"],
            description=cat_data["description"],
            color=cat_data["color"]
        )
        categories.append(category)
        print(f"  카테고리 생성: {category.name}")

    print(f"총 {len(categories)}개의 카테고리 생성 완료")
    return categories

def generate_log_message(category_name: str) -> str:
    """특정 카테고리에 맞는 로그 메시지를 생성합니다."""
    tags = random.sample(TAG_WORDS[category_name], min(2, len(TAG_WORDS[category_name])))
    tag1, tag2 = f"#{tags[0]}", f"#{tags[1]}" if len(tags) > 1 else ""

    activity = random.choice(ACTIVITIES[category_name])
    template = random.choice(LOG_MESSAGE_TEMPLATES)

    message = template.format(tag1=tag1, tag2=tag2, activity=activity)
    return message

def generate_date_range(days_back: int) -> tuple[datetime.datetime, datetime.datetime]:
    """무작위 시작/종료 날짜를 생성합니다."""
    now = datetime.datetime.now()
    start_date = now - datetime.timedelta(days=random.randint(0, days_back),
                                         hours=random.randint(0, 23),
                                         minutes=random.randint(0, 59))

    # 종료 시간 (시작 시간으로부터 15~60분 후)
    duration_minutes = random.randint(15, 60)
    end_date = start_date + datetime.timedelta(minutes=duration_minutes)

    return start_date, end_date

def create_dummy_logs(num_logs: int, categories: list[Category]) -> list[tuple[Log, list[Tag]]]:
    """지정된 수의 더미 로그를 생성합니다. 각 로그에는 메시지와 태그가 포함됩니다."""
    print(f"{num_logs}개의 더미 로그 생성 중...")
    log_repo = LogRepository()
    tag_repo = TagRepository()

    logs_with_tags = []

    for i in range(num_logs):
        # 무작위 카테고리 선택
        category = random.choice(categories)

        # 로그 메시지 생성 (태그 포함)
        message = generate_log_message(category.name)

        # 날짜 범위 생성 (최대 30일 전부터)
        start_date, end_date = generate_date_range(30)

        # 로그 객체 생성
        log = Log(
            message=message,
            tags="[]",  # 임시로 빈 태그 리스트 설정 (나중에 업데이트)
            start_date=start_date.strftime("%Y-%m-%d %H:%M:%S"),
            end_date=end_date.strftime("%Y-%m-%d %H:%M:%S"),
            state=1
        )

        # 로그 저장
        saved_log = log_repo.save_log(log)

        # 메시지에서 태그 추출
        tag_names = extract_tags(message)
        tags = []

        # 태그 생성 및 카테고리 연결
        tag_ids = []
        for tag_name in tag_names:
            tag = tag_repo.add_tag(tag_name)
            # 태그에 카테고리 연결
            tag = tag_repo.update_tag(
                tag_id=tag.id,
                category_id=category.id
            )
            tags.append(tag)
            tag_ids.append(tag.id)

        # 로그의 태그 필드 업데이트
        if tag_ids:
            # SQLite에 직접 연결하여 태그 ID 목록 업데이트
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pace_logs SET tags = ? WHERE id = ?",
                (json.dumps(tag_ids, ensure_ascii=False), saved_log.id)
            )
            conn.commit()
            conn.close()

        logs_with_tags.append((saved_log, tags))

        if (i + 1) % 20 == 0:
            print(f"  {i + 1}개의 로그 생성 완료")

    print(f"총 {len(logs_with_tags)}개의 로그 생성 완료")
    return logs_with_tags

def print_summary(categories: list[Category], logs_with_tags: list[tuple[Log, list[Tag]]]):
    """생성된 데이터 요약 정보를 표시합니다."""
    print("\n======== 생성된 더미 데이터 요약 ========")
    print(f"카테고리: {len(categories)}개")

    # 로그 수
    print(f"로그: {len(logs_with_tags)}개")

    # 태그 수 계산
    all_tags = []
    for _, tags in logs_with_tags:
        all_tags.extend(tags)
    unique_tags = {tag.id for tag in all_tags}
    print(f"태그: {len(unique_tags)}개")

    # 카테고리별 태그 수
    tag_repo = TagRepository()
    all_tags = tag_repo.get_tags()
    category_tag_counts = {}

    for tag in all_tags:
        if tag.category_id not in category_tag_counts:
            category_tag_counts[tag.category_id] = 0
        category_tag_counts[tag.category_id] += 1

    print("\n카테고리별 태그 수:")
    for category in categories:
        count = category_tag_counts.get(category.id, 0)
        print(f"  - {category.name}: {count}개")

    print("\n더미 데이터 생성이 완료되었습니다!")

def main():
    """메인 함수"""
    print("PaceKeeper 테스트용 더미 데이터 생성 시작...")

    # DB 파일 존재 확인
    if os.path.exists(DB_FILE):
        choice = input(f"기존 데이터베이스 파일 '{DB_FILE}'이 존재합니다. 삭제하고 새로 생성하시겠습니까? (y/n): ")
        if choice.lower() == 'y':
            os.remove(DB_FILE)
            print(f"'{DB_FILE}' 파일이 삭제되었습니다.")
        else:
            print("기존 데이터베이스를 사용합니다.")

    # 1. 6개의 카테고리 생성
    categories = create_dummy_categories()

    # 2. 200개의 로그 생성 (태그 포함)
    logs_with_tags = create_dummy_logs(200, categories)

    # 3. 생성된 데이터 요약 정보 출력
    print_summary(categories, logs_with_tags)

if __name__ == "__main__":
    main()
