#!/usr/bin/env python3
"""데이터 마이그레이션 유틸리티"""
import json
import os
import shutil
import sqlite3
from datetime import datetime
from typing import Any

from pacekeeper.utils.app_paths import (
    get_app_data_dir,
    get_backup_dir,
    get_config_path,
    get_database_path,
    get_legacy_paths,
)
from pacekeeper.utils.desktop_logger import DesktopLogger


class DataMigration:
    """개발 환경과 프로덕션 환경 간 데이터 마이그레이션"""

    def __init__(self):
        self.logger = DesktopLogger("DataMigration")

    def find_legacy_data(self) -> dict[str, str | None]:
        """
        기존 개발 환경 데이터 파일들을 찾습니다.
        
        Returns:
            dict: 발견된 파일들의 경로 딕셔너리
        """
        legacy_paths = get_legacy_paths()
        found_files = {}

        # 데이터베이스 파일 확인
        if os.path.exists(legacy_paths['database']):
            # 파일이 비어있지 않은지 확인
            if os.path.getsize(legacy_paths['database']) > 0:
                try:
                    conn = sqlite3.connect(legacy_paths['database'])
                    cursor = conn.cursor()
                    # 테이블 존재 확인
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    conn.close()

                    if tables:
                        found_files['database'] = legacy_paths['database']
                        self.logger.log_system_event(f"기존 데이터베이스 발견: {legacy_paths['database']}")
                except Exception as e:
                    self.logger.log_error(f"데이터베이스 검증 실패: {e}")

        # 설정 파일 확인
        if os.path.exists(legacy_paths['config']):
            try:
                with open(legacy_paths['config'], encoding='utf-8') as f:
                    config_data = json.load(f)
                    if config_data:  # 비어있지 않은 설정 파일
                        found_files['config'] = legacy_paths['config']
                        self.logger.log_system_event(f"기존 설정 파일 발견: {legacy_paths['config']}")
            except Exception as e:
                self.logger.log_error(f"설정 파일 검증 실패: {e}")

        return found_files

    def check_migration_needed(self) -> bool:
        """
        마이그레이션이 필요한지 확인합니다.
        
        Returns:
            bool: 마이그레이션 필요 여부
        """
        # 기존 데이터가 있는지 확인
        legacy_data = self.find_legacy_data()
        if not legacy_data:
            return False

        # 현재 프로덕션 데이터가 비어있는지 확인
        current_db = get_database_path()

        # 프로덕션 DB가 없거나 비어있는 경우
        if not os.path.exists(current_db):
            return True

        # 프로덕션 DB가 비어있는지 확인
        try:
            conn = sqlite3.connect(current_db)
            cursor = conn.cursor()

            # logs 테이블의 데이터 확인
            cursor.execute("SELECT COUNT(*) FROM logs")
            log_count = cursor.fetchone()[0]

            # categories 테이블의 데이터 확인 (기본 카테고리 제외)
            cursor.execute("SELECT COUNT(*) FROM categories WHERE id > 1")
            category_count = cursor.fetchone()[0]

            conn.close()

            # 데이터가 거의 없으면 마이그레이션 필요
            return log_count == 0 and category_count == 0

        except Exception as e:
            self.logger.log_error(f"프로덕션 DB 확인 실패: {e}")
            return True

    def create_backup(self, file_path: str) -> str | None:
        """
        파일 백업을 생성합니다.
        
        Args:
            file_path: 백업할 파일 경로
            
        Returns:
            str: 백업 파일 경로 (실패 시 None)
        """
        if not os.path.exists(file_path):
            return None

        try:
            backup_dir = get_backup_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)

            backup_filename = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(backup_dir, backup_filename)

            shutil.copy2(file_path, backup_path)
            self.logger.log_system_event(f"백업 생성 완료: {backup_path}")

            return backup_path

        except Exception as e:
            self.logger.log_error(f"백업 생성 실패: {e}")
            return None

    def migrate_database(self, source_db: str) -> bool:
        """
        데이터베이스를 마이그레이션합니다.
        
        Args:
            source_db: 원본 데이터베이스 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            target_db = get_database_path()

            # 기존 프로덕션 DB 백업
            if os.path.exists(target_db):
                self.create_backup(target_db)

            # 데이터베이스 복사
            shutil.copy2(source_db, target_db)

            # 복사된 DB 검증
            conn = sqlite3.connect(target_db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM logs")
            log_count = cursor.fetchone()[0]
            conn.close()

            self.logger.log_system_event(f"데이터베이스 마이그레이션 완료: {log_count}개 로그 이전됨")
            return True

        except Exception as e:
            self.logger.log_error(f"데이터베이스 마이그레이션 실패: {e}")
            return False

    def migrate_config(self, source_config: str) -> bool:
        """
        설정 파일을 마이그레이션합니다.
        
        Args:
            source_config: 원본 설정 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            target_config = get_config_path()

            # 기존 설정 백업
            if os.path.exists(target_config):
                self.create_backup(target_config)

            # 설정 파일 복사
            shutil.copy2(source_config, target_config)

            # 복사된 설정 검증
            with open(target_config, encoding='utf-8') as f:
                config_data = json.load(f)

            self.logger.log_system_event(f"설정 파일 마이그레이션 완료: {len(config_data)}개 설정 이전됨")
            return True

        except Exception as e:
            self.logger.log_error(f"설정 파일 마이그레이션 실패: {e}")
            return False

    def perform_migration(self) -> dict[str, bool]:
        """
        전체 마이그레이션을 수행합니다.
        
        Returns:
            dict: 각 항목별 마이그레이션 결과
        """
        results = {
            'database': False,
            'config': False,
            'overall': False
        }

        # 기존 데이터 찾기
        legacy_data = self.find_legacy_data()

        if not legacy_data:
            self.logger.log_system_event("마이그레이션할 기존 데이터가 없습니다.")
            return results

        # 데이터 디렉토리 확인
        get_app_data_dir()  # 디렉토리 생성

        # 데이터베이스 마이그레이션
        if 'database' in legacy_data:
            results['database'] = self.migrate_database(legacy_data['database'])

        # 설정 파일 마이그레이션
        if 'config' in legacy_data:
            results['config'] = self.migrate_config(legacy_data['config'])

        # 전체 성공 여부
        results['overall'] = any(results[key] for key in ['database', 'config'])

        if results['overall']:
            self.logger.log_system_event("데이터 마이그레이션이 완료되었습니다.")
        else:
            self.logger.log_error("데이터 마이그레이션에 실패했습니다.")

        return results

