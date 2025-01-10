import os
import sqlite3
import shutil
from datetime import datetime

def migrate_database():
    """데이터베이스 마이그레이션"""
    # 백업 생성
    backup_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # DB 파일 백업
    if os.path.exists('break_log.db'):
        shutil.copy2('break_log.db', f'break_log.db.backup_{backup_suffix}')
        
        # 데이터 마이그레이션
        old_conn = sqlite3.connect('break_log.db')
        new_conn = sqlite3.connect('pace_log.db')
        
        try:
            # 새 테이블 생성
            new_conn.execute('''
                CREATE TABLE IF NOT EXISTS pace_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_date TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    message TEXT NOT NULL,
                    tags TEXT
                )
            ''')
            
            # 데이터 복사
            old_cursor = old_conn.cursor()
            old_cursor.execute('SELECT * FROM break_logs')
            rows = old_cursor.fetchall()
            
            new_cursor = new_conn.cursor()
            new_cursor.executemany(
                'INSERT INTO pace_logs (id, created_date, timestamp, message, tags) VALUES (?, ?, ?, ?, ?)',
                rows
            )
            
            new_conn.commit()
            print("데이터베이스 마이그레이션 완료")
            
        except Exception as e:
            print(f"마이그레이션 중 오류 발생: {e}")
            if os.path.exists('pace_log.db'):
                os.remove('pace_log.db')
            
        finally:
            old_conn.close()
            new_conn.close()
    
    # 로그 파일 백업
    if os.path.exists('break_log.txt'):
        shutil.copy2('break_log.txt', f'break_log.txt.backup_{backup_suffix}')
        os.rename('break_log.txt', 'pace_log.txt')

if __name__ == '__main__':
    migrate_database()
