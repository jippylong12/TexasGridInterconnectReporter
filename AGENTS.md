# AGENTS.md - Project Directives

## 🎯 Mission Objective

To process monthly ERCOT generator connection status reports (Excel files) and generate structured, organized, and documented reports, following all best practices for modular Python development.

## 📦 Data Inputs (Excel Sheets)

The raw input Excel files are expected to contain, at a minimum, the following sheets. All data extraction logic must be robust to read these specific sheet names.

* `Disclaimer and References`
* `Acronyms`
* `Summary`
* `Project Details - Large Gen`
* `Project Details - Small Gen`
* `GIM Trends`
* `Commissioning Update`
* `Inactive Projects`
* `Cancellation Update`

## 💻 Python Conventions & Paradigms

All code must adhere strictly to modern Python best practices.

* **Style Guide:** Adhere to **PEP 8** for all code formatting. Use tools like `flake8` or `ruff` for linting and **Black** for uncompromising code formatting.
* **Modularity:** Code must be organized into small, focused functions and classes. **Avoid long, monolithic scripts.**
    * **Single Responsibility Principle (SRP):** Each module (`.py` file), class, or function should have one clearly defined job (e.g., `ercot_reader.py` only reads, `cleaner.py` only cleans).
    * **Data Flow:** The pipeline should follow a clear ETL/ELT pattern: **Ingestion** (read raw data) -> **Processing** (clean/transform) -> **Generation** (create final reports).
* **Dependencies:** Use `pandas` for data manipulation. All dependencies must be tracked in `requirements.txt`.
* **Typing:** Use Python **type hints** for all function arguments and return values.

## 🛠️ Build & Test Commands

* **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
* **Run Tests:**
    ```bash
    pytest tests/
    ```
* **Run Linter (Flake8/Ruff):**
    ```bash
    ruff check src/
    ```
* **Auto-Format Code (Black):**
    ```bash
    black src/
    ```
* **Execute Pipeline:**
    ```bash
    python src/main.py --input-file data/raw/ERCOT_Report_YYYY-MM.xlsx
    ```

## 📝 Report Generation and Documentation

For every new report generated:

1.  The final report file (e.g., a CSV or Excel) must be saved into a dedicated, organized subdirectory within the `reports/` folder (e.g., `reports/report_name/`).
2.  The `reports/README.md` file **must be updated** to include:
    * A concise **description** of the new report.
    * The **data sources** used from the input Excel sheets.
    * An explanation of the key **calculations or transformations** performed to generate the report.
    * The **expected output format** (e.g., columns, file type).