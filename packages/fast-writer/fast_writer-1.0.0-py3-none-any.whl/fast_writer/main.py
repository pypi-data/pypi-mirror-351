import typer
from typing_extensions import Annotated
from pathlib import Path
import logging
from typing import List

from fast_writer import preview, converter, merger
from fast_writer import __version__

# 로깅 설정
logging.basicConfig(
    level=logging.WARNING, # 기본 로그 레벨. --verbose 플래그로 INFO로 변경 가능.
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()] # 콘솔 출력 핸들러
)
# 파일 핸들러를 추가하여 로그 파일에 기록할 수도 있습니다.
# file_handler = logging.FileHandler("fast_writer.log")
# file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
# logging.getLogger().addHandler(file_handler)

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="fast-writer",
    help="Polars를 사용한 빠른 파일 처리 CLI 도구입니다.",
    add_completion=False)

def version_callback(value: bool):
    if value:
        print(f"fast-writer version: {__version__}")
        raise typer.Exit()

@app.callback()
def main_options(
    version: Annotated[
        bool, typer.Option("--version", callback=version_callback, is_eager=True, help="버전 정보를 출력하고 종료합니다.")
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="자세한 로그(INFO 레벨)를 출력합니다.")
    ] = False,
):
    """
    fast-writer: 다양한 파일 작업을 빠르게 수행하는 CLI 도구.
    각 명령어에 대한 도움말은 `fast-writer [COMMAND] --help`로 확인하세요.
    """
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
        logger.info("상세 로깅이 활성화되었습니다 (INFO 레벨).")

no_drm_option = Annotated[
    bool,
    typer.Option("--no-drm", help="Excel 파일을 Polars로 직접 읽습니다 (xlwings를 사용한 DRM 처리 시도 안 함).")
]

merge_app = typer.Typer(name="merge", help="여러 파일을 병합합니다.")
app.add_typer(merge_app)

# --- 미리보기 명령어 ---
@app.command("head")
def preview_head_cmd(
    file_path: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, help="미리볼 파일의 경로입니다.")],
    n: Annotated[int, typer.Option("--lines", "-n", help="표시할 행의 수입니다.", min=1)] = 5,
    no_drm: no_drm_option = False,
):
    """파일의 처음 N개 행을 표시합니다."""
    logger.info(f"Executing: preview head - 파일: {file_path}, 행 수: {n}")
    preview.show_head(file_path, n, no_drm=no_drm)

@app.command("tail")
def preview_tail_cmd(
    file_path: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, help="미리볼 파일의 경로입니다.")],
    n: Annotated[int, typer.Option("--lines", "-n", help="표시할 행의 수입니다.", min=1)] = 5,
    no_drm: no_drm_option = False,
):
    """파일의 마지막 N개 행을 표시합니다."""
    logger.info(f"Executing: preview tail - 파일: {file_path}, 행 수: {n}")
    preview.show_tail(file_path, n, no_drm=no_drm)

# --- 변환 명령어 ---
SUPPORTED_FORMATS = ["csv", "tsv", "xlsx", "parquet"]
@app.command("convert")
def convert_ext_cmd(
    input_file: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, help="변환할 입력 파일의 경로입니다.")],
    output_format: Annotated[str, typer.Argument(help=f"변환할 대상 파일 형식입니다. 지원 형식: {', '.join(SUPPORTED_FORMATS)}", case_sensitive=False)],
    output_file: Annotated[Path, typer.Option("--out", "-o", help="출력 파일 경로입니다. 지정하지 않으면 입력 파일명에 새 확장자를 사용합니다.", resolve_path=True)] = None,
    no_drm: no_drm_option = False,
):
    """파일을 다른 형식으로 변환합니다."""
    logger.info(f"Executing: convert ext - 입력: {input_file}, 출력 형식: {output_format}, 출력 파일: {output_file or '자동'}")
    if output_format.lower() not in SUPPORTED_FORMATS:
        print(f"오류: 지원하지 않는 출력 형식 '{output_format}'. 지원 형식: {', '.join(SUPPORTED_FORMATS)}")
        raise typer.Exit(code=1)
    converter.convert_file_format(input_file, output_format.lower(), output_file, no_drm=no_drm)

# --- 병합 명령어 ---
@merge_app.command("files")
def merge_files_cmd(
    file_paths: Annotated[List[Path], typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, help="병합할 파일 경로 목록입니다.")],
    output_file: Annotated[Path, typer.Option("--out", "-o", help="병합된 출력 파일 경로입니다. 확장자로 형식이 결정됩니다 (예: .parquet, .csv). 기본값: merged_output.parquet", resolve_path=True)] = Path("merged_output.parquet"),
    no_drm: no_drm_option = False,
):
    """지정된 여러 파일을 행 기준으로 병합합니다."""
    logger.info(f"Executing: merge files - 입력 파일 수: {len(file_paths)}, 출력: {output_file}")
    if not file_paths:
        print("오류: 하나 이상의 입력 파일을 지정해야 합니다.")
        raise typer.Exit(code=1)
    merger.merge_list_of_files(file_paths, output_file, no_drm=no_drm)

@merge_app.command("folder")
def merge_folder_cmd(
    folder_path: Annotated[Path, typer.Argument(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True, help="병합할 파일이 있는 폴더 경로입니다.")],
    output_file: Annotated[Path, typer.Option("--out", "-o", help="병합된 출력 파일 경로입니다. 확장자로 형식이 결정됩니다. 기본값: merged_output.parquet", resolve_path=True)] = Path("merged_output.parquet"),
    pattern: Annotated[str, typer.Option("--pattern", "-p", help="폴더 내에서 파일을 찾을 때 사용할 Glob 패턴입니다 (예: '*.csv', '*.parquet'). 기본값: '*.*' (모든 파일).")] = "*.*",
    no_drm: no_drm_option = False,
):
    """폴더 내의 지정된 패턴과 일치하는 모든 파일을 행 기준으로 병합합니다."""
    logger.info(f"Executing: merge folder - 폴더: {folder_path}, 패턴: {pattern}, 출력: {output_file}")
    merger.merge_files_in_folder(folder_path, output_file, pattern, no_drm=no_drm)

if __name__ == "__main__":
    app() # Typer 앱 실행