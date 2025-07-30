import polars as pl
from pathlib import Path
from .utils import read_file
import logging

logger = logging.getLogger(__name__)

def show_head(file_path: Path, n: int = 5, no_drm: bool = False):
    """파일의 처음 N개 행을 표시합니다."""
    try:
        # 파일 전체를 읽습니다.
        df = read_file(file_path, no_drm=no_drm)
        print(f"--- {file_path.name}의 처음 {n}개 행 ---")
        print(df.head(n)) # 읽은 DataFrame에서 head(n)을 적용합니다.
    except Exception as e:
        logger.error(f"{file_path} 파일의 head 표시 중 오류: {e}")
        print(f"{file_path.name} 파일 미리보기 중 오류가 발생했습니다: {e}")

def show_tail(file_path: Path, n: int = 5, no_drm: bool = False):
    """파일의 마지막 N개 행을 표시합니다."""
    try:
        # tail의 경우, 일반적으로 파일의 더 많은 부분을 읽어야 합니다.
        df = read_file(file_path, no_drm=no_drm) # 전체 파일 읽기
        print(f"--- {file_path.name}의 마지막 {n}개 행 ---")
        print(df.tail(n))
    except Exception as e:
        logger.error(f"{file_path} 파일의 tail 표시 중 오류: {e}")
        print(f"{file_path.name} 파일 미리보기 중 오류가 발생했습니다: {e}")