# Hitlog Processing

A production-ready Python application for analyzing user journey data to identify influential articles that lead to user registrations. 

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Approaches](#approaches)
  - [Timestamp-Based Approach](#timestamp-based-approach)
  - [Graph-Based Approach](#graph-based-approach)
- [Data](#data)
- [Notebooks](#notebooks)
- [Development](#development)
- [Testing](#testing)
- [Results](#results)

## Overview

This project analyzes hitlog data (user page views and registration events) to determine which articles are most influential in driving user registrations. The system tracks user journeys through a website and counts how many unique users viewed each article before registering.

**Key Features:**
- Two distinct algorithmic approaches (timestamp-based and graph-based)
- Robust CSV I/O with proper error handling
- Comprehensive test suite
- CLI tool for production use
- Jupyter notebooks for exploratory data analysis
- Automated code quality checks (ruff linting and formatting)

## Project Structure

```
hitlog_processing/
├── data/
│   ├── data_gen.py              # Synthetic data generator
│   ├── logs/                    # Input CSV files
│   │   └── hitlog_2025-10-27.csv
│   └── outputs/                 # Generated results
│       ├── influence_timestamp.csv
│       ├── influence_graph.csv
│       └── top_influential_articles_2025-10-27.csv
├── notebooks/
│   ├── data_exploration.ipynb   # EDA and journey signature analysis
│   └── solutions/
│       ├── Freq_count_solution.ipynb
│       ├── Directed_graph_with_variable_weights.ipynb
│       └── Graph_with_frozen_weights.ipynb
├── src/
│   └── telegraph_ranker/
│       ├── __init__.py
│       ├── cli.py               # Command-line interface
│       ├── domain.py            # Type definitions
│       ├── io_utils.py          # CSV reading/writing
│       ├── approaches/
│       │   ├── timestamp_based.py
│       │   └── graph_based.py
│       └── models/
│           └── node.py          # Graph node representation
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   └── test_cli.py              # Integration tests
├── Makefile                     # Development automation
├── pyproject.toml               # Project configuration
├── requirements.txt             # Pinned dependencies (generated from pyproject)
├── uv.lock                      # Lockfile (uv)
├── Sample_hitlog.csv            # Example input CSV
└── README.md
```

## Installation

### Prerequisites
- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Pulkit12dhingra/Hitlog_Processing.git
   cd hitlog_processing
   ```

2. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv pip install -e .
   
   # Or using pip
   pip install -e .
   ```


## Usage

### Command Line Interface

The primary way to use this tool is through the CLI:

```bash
python -m telegraph_ranker.cli \
  --input data/logs/hitlog_2025-10-27.csv \
  --output data/outputs/top_influential.csv \
  --approach timestamp
```

**Arguments:**
- `--input`: Path to input hitlog CSV file (required)
- `--output`: Path for output CSV file (required)
- `--approach`: Ranking algorithm to use: `timestamp` (default) or `graph`

**Example outputs:**

```bash
# Timestamp-based approach
python -m telegraph_ranker.cli \
  --input data/logs/hitlog_2025-10-27.csv \
  --output data/outputs/influence_timestamp.csv \
  --approach timestamp

# Graph-based approach
python -m telegraph_ranker.cli \
  --input data/logs/hitlog_2025-10-27.csv \
  --output data/outputs/influence_graph.csv \
  --approach graph
```

## Approaches

Both approaches solve the same problem but with different implementation strategies.

### Timestamp-Based Approach

**File:** `src/telegraph_ranker/approaches/timestamp_based.py`

**Algorithm:**
1. Process each user's events in chronological order (sorted by timestamp)
2. Maintain a set of unique articles seen in the current "journey"
3. When a `/register` event is encountered:
   - Increment the count for each article in the journey set by 1
   - Clear the journey set for the next registration cycle
4. Articles viewed after registration or without subsequent registration are not counted

**Characteristics:**
- Simple, direct implementation
- Easy to reason about and debug
- Efficient memory usage
- Deterministic results

**Complexity:** O(n) where n is total number of events

### Graph-Based Approach

**File:** `src/telegraph_ranker/approaches/graph_based.py`

**Algorithm:**
1. Build a directed graph where:
   - Nodes represent pages (articles, registration page, etc.)
   - Edges connect consecutive page views for each user
2. Apply the same journey-based counting logic as timestamp approach
3. Store metadata (article name, weight) in Node objects

**Characteristics:**
- Extensible architecture for future graph-based metrics
- Can support additional analyses (PageRank, centrality, etc.)
- Higher memory overhead (stores graph structure)
- More complex implementation

**Complexity:** O(n + e) where n = events, e = edges in graph

### Comparison

Both approaches produce **identical results** for the influence ranking problem. The test suite (`tests/test_cli.py`) verifies this equivalence.

**When to use each:**
- **Timestamp-based**: Default choice, simpler, lower overhead
- **Graph-based**: When you need graph structure for additional analysis (e.g., discovering common paths, calculating graph metrics)

## Data

### Input Format

CSV files with the following schema:

| Column      | Type     | Description                          |
|-------------|----------|--------------------------------------|
| page_name   | string   | Human-readable page title            |
| page_url    | string   | URL path (e.g., `/articles/foo`)     |
| user_id     | string   | Anonymous user identifier            |
| timestamp   | datetime | ISO 8601 timestamp of page view      |

**Example:**
```csv
page_name,page_url,user_id,timestamp
Article Title,/articles/example-slug,u001,2025-10-27 10:30:00
Register,/register,u001,2025-10-27 10:35:00
```

### Output Format

CSV with article influence rankings:

| Column      | Type   | Description                                |
|-------------|--------|--------------------------------------------|
| page_name   | string | Article title                              |
| page_url    | string | Article URL                                |
| total       | int    | Number of unique users who registered after viewing |

**Sorted by:** `total` (descending), then `page_url` (ascending)

### Sample Data Generator

Generate synthetic test data:

```bash
python data/data_gen.py
```

This creates `data/logs/hitlog_<date>.csv` with realistic user journeys including:
- Multiple user sessions per day
- Varied article browsing patterns
- Edge cases (no registration, multiple registrations, etc.)

## Notebooks

### Folder structure

```
notebooks/
  data_exploration.ipynb
  solutions/
    Freq_count_solution.ipynb
    Directed_graph_with_variable_weights.ipynb
    Graph_with_frozen_weights.ipynb
```

### `notebooks/data_exploration.ipynb`

Comprehensive exploratory data analysis covering:

1. **Data Loading & Cleaning**
   - CSV reading with pandas
   - Timestamp parsing and validation
   - Missing data handling

2. **Visual Analysis**
   - User journey classification
   - Journey graph visualization using NetworkX
   - Case distribution charts

3. **Journey Signature Analysis**
   - Compute per-user journey signatures up to first registration
   - Summarize unique signatures with user counts
   - Classify journeys into requested and other informative cases

4. **Edge Case Exploration**
   - Users with cycles (revisiting articles)
   - Multiple registrations
   - Mixed page types
   - Direct registration (no articles viewed)

### Solution notebooks (algorithm explorations)

- `notebooks/solutions/Freq_count_solution.ipynb` — Frequency-count baseline for influence ranking.
- `notebooks/solutions/Directed_graph_with_variable_weights.ipynb` — Directed graph approach with variable/dynamic edge weights.
- `notebooks/solutions/Graph_with_frozen_weights.ipynb` — Graph approach with fixed/frozen weights for reproducibility and comparison.

**To run any notebook:**
```bash
# Launch Jupyter in the notebooks folder and open the desired file
jupyter notebook notebooks/

# Or open a specific notebook directly
jupyter notebook notebooks/data_exploration.ipynb
jupyter notebook notebooks/solutions/Freq_count_solution.ipynb
```

## Development

### Code Quality Tools

The project uses automated tools for code quality:

```bash
# Format code with ruff
make format

# Run linters
make lint

# Run tests
make test

# Generate requirements.txt
make requirements

# Full CI pipeline (format + lint + test + commit)
make commit
```

### Makefile Targets

| Target        | Description                                    |
|---------------|------------------------------------------------|
| `format`      | Auto-format code with ruff                     |
| `requirements`| Generate requirements.txt from pyproject.toml  |
| `lint`        | Run ruff linter (excludes notebooks)           |
| `test`        | Run pytest suite                               |
| `commit`      | Run all checks + git commit with validation    |
| `push`        | Run lint + test + git commit/push (for contributing) |

### Code Style

- **Formatter:** ruff (PEP 8 compliant)
- **Linter:** ruff with strict type checking
- **Type hints:** Enforced with `from __future__ import annotations`
- **Line length:** 100 characters

## Testing

Comprehensive test suite with pytest:

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# With coverage report
pytest --cov=src/telegraph_ranker --cov-report=html
```

### Test Coverage

- CLI integration tests
- Both timestamp and graph approaches
- Idempotency verification
- Result equivalence between approaches

**Key test files:**
- `tests/conftest.py`: Pytest fixtures for test data
- `tests/test_cli.py`: End-to-end CLI tests

## Results

### Reproducing Results

1. **Generate synthetic data:**
   ```bash
   python data/data_gen.py
   ```

2. **Run timestamp-based approach:**
   ```bash
   python -m telegraph_ranker.cli \
     --input data/logs/hitlog_2025-10-27.csv \
     --output data/outputs/influence_timestamp.csv \
     --approach timestamp
   ```

3. **Run graph-based approach:**
   ```bash
   python -m telegraph_ranker.cli \
     --input data/logs/hitlog_2025-10-27.csv \
     --output data/outputs/influence_graph.csv \
     --approach graph
   ```

4. **Compare results:**
   ```bash
   diff data/outputs/influence_timestamp.csv data/outputs/influence_graph.csv
   # Should show no differences (except possibly sorting of ties)
   ```

### Expected Output Structure

The top influential articles will be ranked by the number of unique users who:
1. Viewed the article
2. Subsequently registered (first registration only)


## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and run quality checks: `make commit`
4. Open a Pull Request

## License

This project is part of the Telegraph Data Engineering exercise.

## Author

**Pulkit Dhingra**
- GitHub: [@Pulkit12dhingra](https://github.com/Pulkit12dhingra)
- Repository: [Hitlog_Processing](https://github.com/Pulkit12dhingra/Hitlog_Processing)

---

**Built with:** Python 3.13 • pandas • NetworkX • pytest • ruff
