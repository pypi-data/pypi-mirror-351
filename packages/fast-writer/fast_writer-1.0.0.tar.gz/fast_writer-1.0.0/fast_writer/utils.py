import polars as pl
from pathlib import Path
from typing import Union, Optional
import logging
import pandas as pd
import xlwings as xw

logger = logging.getLogger(__name__)

# 기본 로깅 설정 (애플리케이션의 main.py 또는 별도 설정 모듈에서 수행 가능)
# logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

def read_file(file_path: Union[str, Path], no_drm: bool = False) -> pl.DataFrame:
    """
    파일 확장자를 기반으로 파일을 Polars DataFrame으로 읽습니다.
    no_drm: True일 경우 Excel 파일 읽기 시 xlwings를 사용하지 않고 polars.read_excel을 직접 사용합니다.
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    logger.info(f"파일 읽기 시도: {file_path} (확장자: {suffix})")

    try:
        if suffix == ".csv":
            return pl.read_csv(file_path)
        elif suffix == ".tsv":
            return pl.read_csv(file_path, separator="\t")
        elif suffix in [".xls", ".xlsx"]:
            if no_drm:
                logger.info(f"--no-drm 옵션 활성화. Polars로 Excel 파일 ({file_path}) 직접 읽기 시도.")
                return pl.read_excel(file_path)
            else:
                logger.info(f"Excel 파일 ({file_path}) 읽기 시도. DRM 가능성으로 xlwings 우선 사용.")
                try:
                    # xlwings를 사용하여 Excel 파일 열기 (DRM 우회 시도)
                    # Excel 애플리케이션을 보이지 않게 실행
                    app = xw.App(visible=False)
                    wb = None
                    try:
                        wb = app.books.open(str(file_path))
                        sheet = wb.sheets[0]  # 첫 번째 시트를 읽습니다.
                        
                        # 시트의 사용된 범위를 pandas DataFrame으로 읽기
                        # header=True로 설정하여 첫 행을 헤더로 사용
                        pandas_df = sheet.used_range.options(pd.DataFrame, index=False, header=True).value

                        if pandas_df is None: # 시트가 비어있거나 읽기 실패
                            logger.warning(f"xlwings가 {file_path}에서 데이터를 읽지 못했습니다 (결과가 None). 빈 시트일 수 있습니다.")
                            polars_df = pl.DataFrame()
                        elif pandas_df.empty:
                            logger.warning(f"xlwings가 {file_path}에서 빈 DataFrame을 읽었습니다.")
                            polars_df = pl.DataFrame() # 빈 Polars DataFrame 생성
                        else:
                            polars_df = pl.from_pandas(pandas_df)

                        return polars_df
                    finally:
                        if wb is not None:
                            wb.close()
                        app.quit() # Excel 애플리케이션 종료
                except Exception as e_xw:
                    logger.warning(f"xlwings로 Excel 파일 ({file_path}) 읽기 실패: {e_xw}. Polars 기본 읽기로 폴백합니다.")
                    # xlwings 실패 시 Polars의 기본 read_excel 시도
                    return pl.read_excel(file_path)
        elif suffix == ".parquet":
            return pl.read_parquet(file_path)
        else:
            msg = f"지원하지 않는 파일 형식입니다: {suffix} ({file_path})"
            logger.error(msg)
            raise ValueError(msg)
    except Exception as e:
        logger.error(f"파일 읽기 오류 {file_path}: {e}")
        raise

def write_file(df: pl.DataFrame, output_path: Union[str, Path], output_format: Optional[str] = None):
    """Polars DataFrame을 파일로 씁니다."""
    output_path = Path(output_path)
    effective_output_format = output_format or output_path.suffix.lower().replace(".", "")

    logger.info(f"DataFrame을 {output_path} 경로에 {effective_output_format} 형식으로 저장 시도")
    output_path.parent.mkdir(parents=True, exist_ok=True) # 출력 디렉토리 생성

    try:
        if effective_output_format == "csv":
            df.write_csv(output_path)
        elif effective_output_format == "tsv":
            df.write_csv(output_path, separator="\t")
        elif effective_output_format == "xlsx":
            df.write_excel(output_path) # openpyxl 필요
        elif effective_output_format == "parquet":
            df.write_parquet(output_path)
        else:
            msg = f"지원하지 않는 출력 파일 형식입니다: {effective_output_format} ({output_path})"
            logger.error(msg)
            raise ValueError(msg)
        logger.info(f"파일이 성공적으로 {output_path}에 저장되었습니다.")
        print(f"파일이 성공적으로 {output_path}에 저장되었습니다.") # 사용자 피드백
    except Exception as e:
        logger.error(f"파일 쓰기 오류 {output_path}: {e}")
        print(f"파일 쓰기 오류 {output_path}: {e}") # 사용자 피드백
        raise