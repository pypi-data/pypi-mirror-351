# fast-writer

`fast-writer`는 Polars 라이브러리를 기반으로 구축된 커맨드 라인 인터페이스(CLI) 도구로, 다양한 파일 형식(CSV, TSV, Excel, Parquet)을 빠르고 효율적으로 처리하도록 설계되었습니다. 파일 미리보기, 형식 변환, 여러 파일 병합 등의 기능을 제공합니다.

## 주요 기능

*   **파일 미리보기**: 파일의 처음(`head`) 또는 마지막(`tail`) 몇 줄을 빠르게 확인할 수 있습니다.
*   **파일 형식 변환**: CSV, TSV, Excel (.xlsx), Parquet 파일 간의 상호 변환을 지원합니다.
*   **파일 병합**: 여러 파일을 행(row) 기준으로 병합합니다. 특정 파일들을 지정하거나 폴더 내의 모든 파일을 병합할 수 있습니다.

## 설치

```
pip install fast-writer
```

```bash
git clone https://github.com/jinwook-chang/fast-writer
cd fast-writer
pip install .
```

## 사용법


```bash
fast-writer --help
```

### 파일 미리보기
```bash
# example.csv 파일의 처음 5줄 보기
fast-writer head output/iris.csv

# data.parquet 파일의 마지막 10줄 보기
fast-writer tail head output/iris.csv -n 10
```

### 파일 형식 변환
```bash
# input.csv를 output.parquet로 변환
fast-writer convert output/iris.csv parquet -o output/iris.parquet

# data.xlsx를 data.csv로 변환 (출력 파일명 자동 지정)
fast-writer convert output/iris.csv tsv

```

### 파일 병합
```bash
# file1.csv와 file2.csv를 merged.csv로 병합
fast-writer merge files output/iris.csv output/iris2.csv -o output/merged.csv

# 폴더 내의 모든 .csv 파일을 all_data.parquet로 병합
fast-writer merge folder ./output --pattern "*.csv" -o output/all_data.parquet
```
