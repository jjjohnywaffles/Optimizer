# Python Code Optimizer
## Author: Jonathan Hu

## 📜 Project Overview

The Python Code Optimizer is a tool designed to analyze, refactor, and optimize Python scripts by applying various transformations, such as:

- **Static Analysis**: Detect potential inefficiencies (e.g., high-iteration loops, repeated computations).
- **Dynamic Profiling**: Measure runtime and memory usage to identify bottlenecks.
- **Refactoring**: Automatically apply transformations like:
  - Flattening nested loops.
  - Replacing loops with **vectorized operations** using NumPy.
  - Adding caching for repeated computations.
  - Partial vectorization for loops with multiple statements.
- **Code Reporting**: Generate a detailed report in HTML format, summarizing optimization suggestions.

This project is designed to help developers improve code performance and readability.

---

## 🚀 Features

- **Nested Loop Flattening**:
  Replaces nested loops with `itertools.product` for better readability and efficiency.
- **Vectorization**:
  Converts standard loops operating on lists into **NumPy vectorized operations** for faster execution.
- **Caching**:
  Automatically caches repeated computations to avoid redundant operations.
- **Dynamic Analysis**:
  Uses memory and runtime profiling to evaluate the efficiency of the code.
- **Comprehensive HTML Report**:
  Generates a detailed report highlighting optimization suggestions and profiling results.

---

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/python-code-optimizer.git
   cd python-code-optimizer
   ```
   
2. Install dependencies:

    pip install -r requirements.txt

3. Verify installation by running tests:

    pytest tests/
    
---

## 🖥️ Usage

- **Run the Optimizer**:  
  Pass your Python script to the optimizer.
  ```bash
  python optimizer.py <path-to-script>


- **Example**:

    python optimizer.py example_script.py

- **View the Report**:

    After running the optimizer, an HTML report (report.html) will be generated in the root directory. Open it in any web browser to review optimization suggestions and profiling results.

- **View Optimized Code**:

    The transformed Python script will be saved in the optimized_code/ directory with the same filename as the input script.
    
---

## 📂 Project Structure

    .
    ├── optimizer.py               # Main entry point for the optimizer
    ├── requirements.txt           # Dependencies for the project
    ├── README.md                  # Project documentation
    ├── optimized_code/            # Directory for saving optimized scripts
    ├── templates/                 # HTML template for the report
    │   └── report_template.html
    ├── utils/                     # Utility modules
    │   ├── refactoring_engine.py  # AST-based refactoring logic
    │   ├── static_analysis.py     # Static analysis tools
    │   ├── dynamic_profiler.py    # Runtime and memory profiling tools
    ├── tests/                     # Unit tests
    │   ├── test_static_analysis.py
    │   ├── test_refactoring_engine.py
    
