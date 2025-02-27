# utils/logger.py
import os
import logging
import logging.handlers
from datetime import datetime

def setup_logger():
    """애플리케이션 로깅 설정"""
    # 로그 디렉토리 생성
    log_dir = os.path.join(os.path.expanduser('~'), '.pacekeeper', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 로그 파일 경로 설정
    log_file = os.path.join(log_dir, f'pacekeeper_{datetime.now().strftime("%Y%m%d")}.log')
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 파일 핸들러 설정
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, 
        maxBytes=1024*1024*5,  # 5MB
        backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger 