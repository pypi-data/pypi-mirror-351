import polars as pl
from pathlib import Path
from typing import List
from .utils import read_file, write_file
import logging

logger = logging.getLogger(__name__)

def merge_list_of_files(
    file_paths: List[Path],
    output_file: Path,
    no_drm: bool = False
):
    """지정된 파일 목록을 행 기준으로 병합합니다."""
    if not file_paths:
        print("오류: 병합할 파일이 제공되지 않았습니다.")
        logger.warning("병합할 파일 목록이 비어있습니다.")
        return

    dataframes_to_merge = []
    for file_path in file_paths:
        if not file_path.exists():
            print(f"경고: {file_path} 파일을 찾을 수 없습니다. 건너<0xEB><0><0x84>니다.")
            logger.warning(f"병합 중 파일 없음: {file_path}. 건너<0xEB><0><0x84>니다.")
            continue
        try:
            dataframes_to_merge.append(read_file(file_path, no_drm=no_drm))
        except Exception as e:
            print(f"경고: {file_path} 파일을 읽는 중 오류 발생. 건너<0xEB><0><0x84>니다. 오류: {e}")
            logger.warning(f"{file_path} 읽기 오류로 병합에서 제외: {e}")

    if not dataframes_to_merge:
        print("오류: 병합을 위해 읽을 수 있는 유효한 파일이 없습니다.")
        logger.error("병합할 유효한 DataFrame이 없습니다.")
        return

    try:
        # how="diagonal"은 스키마가 다른 경우에도 열을 합치고 없는 값은 null로 채웁니다.
        merged_df = pl.concat(dataframes_to_merge, how="diagonal")
        write_file(merged_df, output_file) # output_file의 확장자에 따라 형식이 결정됩니다.
    except Exception as e:
        print(f"파일 병합 또는 출력 파일 저장 중 오류 발생: {e}")
        logger.error(f"파일 병합/저장 중 오류 ({output_file}): {e}")

def merge_files_in_folder(
    folder_path: Path,
    output_file: Path,
    pattern: str = "*.*",
    no_drm: bool = False
):
    """폴더 내에서 패턴과 일치하는 모든 파일을 행 기준으로 병합합니다."""
    if not folder_path.is_dir():
        print(f"오류: {folder_path} 폴더를 찾을 수 없거나 디렉토리가 아닙니다.")
        logger.error(f"잘못된 폴더 경로: {folder_path}")
        return

    file_paths = [f for f in folder_path.glob(pattern) if f.is_file()]

    if not file_paths:
        print(f"{folder_path} 폴더에서 '{pattern}' 패턴과 일치하는 파일을 찾을 수 없습니다.")
        logger.info(f"'{pattern}' 패턴에 일치하는 파일 없음: {folder_path}")
        return

    print(f"병합할 파일 목록 ({len(file_paths)}개): {[fp.name for fp in file_paths]}")
    logger.info(f"폴더에서 병합할 파일: {[str(fp) for fp in file_paths]}")
    merge_list_of_files(file_paths, output_file, no_drm=no_drm)