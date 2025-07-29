# Spreadsheet Splitter

`spreadsheet_splitter` is a Python command-line tool designed to split large Excel files (`.xls` or `.xlsx`) into smaller, manageable parts. It supports processing large files iteratively with low memory usage, making it ideal for handling files that exceed available RAM (e.g., >4 GB). The tool preserves specified title rows, logs processing details (including file profiling and memory usage), and supports resuming interrupted tasks.

## Features
- Split `.xls` and `.xlsx` files into two equal parts or smaller chunks.
- Process large files iteratively with configurable rows per iteration.
- Preserve title rows in non-large mode.
- Validate column counts and profile data types for `.xlsx` files.
- Monitor memory usage during processing.
- Resume processing from the last checkpoint using a log file.
- Built with `xlrd`, `xlwt`, `openpyxl`, `pandas`, `pyexcelerate`, and `psutil`.

## Prerequisites
To build and run `spreadsheet_splitter` locally, ensure you have:
- **Python**: Version 3.13 or higher.
- **uv**: A Python package manager for managing dependencies and virtual environments. Install it with:
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
    
  
  <<https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1>>

  ```powershell
  # Windows
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ````

  
  <<https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2>>
  
- **Git**: To clone the repository.
- An Excel file (`.xls` or `.xlsx`) to process.

## Building from Source
Follow these steps to build `spreadsheet_splitter` from source:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/parsaloi/spreadsheet_splitter.git
   cd spreadsheet_splitter
   ````

2. **Set Up a Virtual Environment**
   Create and activate a virtual environment using `uv`:
   ```bash
   uv venv
   source .venv/bin/activate  # On Linux/macOS
   .venv\Scripts\activate     # On Windows
   ```

3. **Install Dependencies**
   Install the required dependencies specified in `pyproject.toml`:
   ```bash
   uv sync
   ```

4. **Verify Setup**
   Check that the `spreadsheet-splitter` command is available:
   ```bash
   uv run spreadsheet-splitter --help
   ```
   This should display the CLI help message with available arguments.

## Running the Tool
The `spreadsheet_splitter` tool provides two modes:
- **Default Mode**: Splits an Excel file into two equal parts, preserving title rows.
- **Large Mode**: Splits large files into smaller chunks with a specified number of rows per iteration, ideal for low-memory environments.

### Example Commands
1. **Split a File into Two Parts**
   ```bash
   uv run spreadsheet-splitter /path/to/file.xlsx --output-dir split_files --title-rows 1
   ```
   - Splits `file.xlsx` into `split_files/file_part1.xlsx` and `split_files/file_part2.xlsx`.
   - Preserves 1 title row in each output file.

2. **Split a Large File Iteratively**
   ```bash
   uv run spreadsheet-splitter /path/to/very_large_file.xlsx --large --output-dir split_files --rows-per-iteration 500 --max-iterations 5 --columns 22
   ```
   - Processes `very_large_file.xlsx` in chunks of 500 rows, up to 5 iterations (2500 rows total).
   - Reads only the first 22 columns.
   - Outputs files like `split_files/very_large_file_part001.xlsx`, `split_files/very_large_file_part002.xlsx`, etc.
   - Logs progress to `split_log.json`.

3. **Resume Processing**
   ```bash
   uv run spreadsheet-splitter /path/to/very_large_file.xlsx --large --resume --output-dir split_files --rows-per-iteration 500 --max-iterations 5 --columns 22
   ```
   - Resumes from the last processed row recorded in `split_log.json`.

### Command-Line Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `input_file` | Path to the input `.xls` or `.xlsx` file | Required |
| `-o, --output-dir` | Directory to save output files | `output` |
| `-t, --title-rows` | Number of top rows to treat as title rows (ignored in `--large` mode) | 1 |
| `--large` | Process large files iteratively with limited rows per iteration | False |
| `--rows-per-iteration` | Number of data rows to process per iteration | 500 |
| `--max-iterations` | Maximum number of iterations to process | 10 |
| `--resume` | Resume processing from the last row in the log file | False |
| `--log-file` | Path to the log file for tracking processed rows | `split_log.json` |
| `--columns` | Number of columns to process | All columns |

### Log File
The tool generates a `split_log.json` file to track processing details, including:
- **Input and Output**: Input file path and output directory.
- **Processed Ranges**: Start and end rows for each output file.
- **File Profile**: Total rows, columns, and data types (for `.xlsx`).
- **Memory Usage**: Memory before and after reading each chunk (for `.xlsx`).
- **Timestamp**: When the log was last updated.

Example `split_log.json`:
```json
{
  "input_path": "/path/to/very_large_file.xlsx",
  "output_dir": "split_files",
  "rows_per_iteration": 500,
  "processed_ranges": [
    {
      "file": "split_files/very_large_file_part001.xlsx",
      "start_row": 1,
      "end_row": 500,
      "iteration": 1
    }
  ],
  "last_row_processed": 499,
  "timestamp": "2025-05-27T11:12:46.172255",
  "columns": 22,
  "file_profile": {
    "total_rows": 1,
    "total_columns": 22,
    "data_types": {
      "ZONE": "float64",
      "SITE": "object",
      ...
    }
  },
  "memory_usage": [
    {
      "iteration": 1,
      "memory_before_mb": 256.55078125,
      "memory_after_mb": 259.6328125
    }
  ]
}
```

## Troubleshooting
- **Column Count Error**: If you see `Specified columns (N) exceeds actual columns (M)`, verify the column count:
  ```python
  import pandas as pd
  df = pd.read_excel("/path/to/very_large_file.xlsx", nrows=1, engine='openpyxl')
  print(df.shape[1], "columns")
  ```
  Use the correct number with `--columns`.

- **Empty File Warning**: If the tool warns that the input file has no rows, check the file content:
  ```python
  import pandas as pd
  df = pd.read_excel("/path/to/very_large_file.xlsx", nrows=10, engine='openpyxl')
  print(df.shape[0], "rows")
  ```

- **Memory Issues**: If memory usage is high, reduce `--rows-per-iteration` (e.g., to 100). Check `split_log.json` for memory usage details.

- **Slow Processing**: Ensure the input file is on a fast local drive (e.g., SSD). For `.xlsx` files with many unique strings, consider converting to `.csv` first:
  ```python
  import pandas as pd
  df = pd.read_excel("/path/to/very_large_file.xlsx", engine='openpyxl')
  df.to_csv("very_large_file.csv", index=False)
  ```

## Future Work
- Package the tool for PyPI with cross-platform installation instructions.
- Add support for `.csv` input files.
- Enhance profiling with more detailed statistics (e.g., unique values per column).

## License
MIT License
