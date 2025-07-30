import polars as pl
from pathlib import Path
from .utils import read_file, write_file
import logging

logger = logging.getLogger(__name__)

def convert_file_format(
    input_file: Path,
    output_format: str,
    output_file: Path = None,
    no_drm: bool = False
):
    """파일 형식을 다른 형식으로 변환합니다."""
    if not input_file.exists():
        print(f"오류: 입력 파일 {input_file}을(를) 찾을 수 없습니다.")
        logger.error(f"입력 파일 없음: {input_file}")
        return

    if output_file is None:
        output_file = input_file.with_suffix(f".{output_format.lower()}")

    try:
        df = read_file(input_file, no_drm=no_drm)
        write_file(df, output_file, output_format)
    except Exception as e:
        print(f"파일 변환 중 오류가 발생했습니다: {e}")
        logger.error(f"{input_file} -> {output_file} ({output_format}) 변환 중 오류: {e}")