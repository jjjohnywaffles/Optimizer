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
    ├── optimizer.py                       # Main entry point for the optimizer
    ├── requirements.txt                   # Dependencies for the project
    ├── README.md                          # Project documentation
    ├── optimized_code/                    # Directory for saving optimized scripts
    ├── templates/                         # HTML template for the report
    │   └── report_template.html
    ├── utils/                             # Utility modules
    │   ├── refactoring_engine.py          # AST-based refactoring logic
    │   ├── static_analysis.py             # Static analysis tools
    │   ├── dynamic_profiler.py            # Runtime and memory profiling tools
    │   ├── project_analyzer.py            # Recursively analyze a project directory to identify all Python files
    │   ├── VectorizationTransformer.py    # Replaces inefficient loops with vectorized NumPy operations
    ├── tests/                             # Unit tests
    │   ├── test_static_analysis.py
    │   ├── test_refactoring_engine.py
    
---

## ⚙️ Utilities in the `utils` Directory

Below is a summary of what each file in the `utils` directory does:

### `__init__.py`
- Marks the `utils` folder as a Python package.
- Allows other parts of the project to import the modules in this directory.

### `dynamic_profiler.py`
- Handles runtime and memory profiling of Python scripts.
- Uses `cProfile` for execution time profiling and `memory_profiler` for tracking memory usage.
- Provides methods like `profile_runtime` and `profile_memory` to gather and return profiling data.

### `project_analyzer.py`
- Analyzes a project directory for Python scripts.
- Recursively scans the directory to collect `.py` files.

### `refactoring_engine.py`
- Responsible for refactoring Python code based on analysis results.
- Works with the Abstract Syntax Tree (AST) to perform transformations like replacing loops with vectorized operations or optimizing repeated calculations.
- Implements methods to modify and optimize Python code programmatically.

### `report_generator.py`
- Generates an HTML report summarizing the results of the analysis and profiling.
- Utilizes Jinja2 templates to create the report, which includes details like static analysis results, profiling metrics, and suggestions for optimization.

### `static_analysis.py`
- Performs static analysis on Python scripts.
- Identifies inefficiencies such as:
  - High-iteration loops.
  - Nested loops.
  - Repeated computations.
- Helps detect optimization opportunities without executing the code.

### `VectorizationTransformer.py`
- Focuses on transforming Python code to leverage vectorized operations using libraries like NumPy.
- Replaces traditional Python loops with vectorized equivalents to improve performance.
- Analyzes code and identifies areas that could benefit from vectorization.

---

### Differences Achieved by the Optimizer

The optimizer transforms the original code to make it more efficient by introducing vectorized operations and flattening nested loops. Here's a breakdown of the differences:

#### Original `basic_loop`:

    def basic_loop():
        arr = [1, 2, 3, 4, 5]
        c = 10
        for i in range(len(arr)):
            arr[i] += c
        print(arr)

#### Optimized `basic_loop`:

    def basic_loop():
        arr = [1, 2, 3, 4, 5]
        c = 10
        arr = np.array(arr) + c
        print(arr)
        
#### Optimization Explanation:
    
The loop that iteratively updates elements in arr is replaced with a NumPy vectorized operation, which is more concise and faster. This eliminates the need for the explicit for loop.
    
    
#### Original `nested_loop`:

    def nested_loop():
        matrix = [[i * j for j in range(5)] for i in range(5)]
        result = 0
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                result += matrix[i][j]
        print(result)
    
#### Optimized `nested_loop`:

    def nested_loop():
        matrix = [[(i * j) for j in range(5)] for i in range(5)]
        result = 0
        for i, j in itertools.product(range(len(matrix)), range(len(matrix[i]))):
            result += matrix[i][j]
        print(result)
        
#### Optimization Explanation:

The nested for loops are replaced with a flattened loop using itertools.product. This flattens the two nested loops into a single iterable, reducing complexity and potentially improving readability and performance.
    
