# ⚡ ERCOT Generator Interconnection Report Generator

## 💡 Project Overview

This project is a modular, factorable **Python data pipeline** designed to process and analyze monthly **ERCOT Generator Interconnection Status Reports**.

The primary goal is to **ingest** data from various sheets within the provided Excel reports, **transform** and clean the raw data, and **generate** several distinct, structured output reports for analysis and tracking of large and small-scale power generation projects connecting to the Texas grid.



[Image of a data processing pipeline]


## 🛠️ Key Features

* **Modular Architecture:** Built using small, focused components following PEP 8 and Python paradigms for maintainability and scalability.
* **Data Ingestion:** Reads structured data from specific sheets within the raw ERCOT Excel files.
* **Report Generation:** Creates multiple organized reports based on different business requirements.
* **Documentation:** Automatically updates the `reports/README.md` file whenever a new report is generated or updated.

## 🚀 Getting Started

The main execution script is located at `src/main.py`. Consult the `AGENTS.md` file for architectural guidelines and development conventions.