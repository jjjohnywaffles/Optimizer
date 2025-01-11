import os

def analyze_project(directory):
    
    """
    Recursively analyze a project directory to identify all Python files.

    Args:
        directory (str): The root directory to analyze.

    Returns:
        list: A list of file paths for all Python files (.py) found within 
              the specified directory and its subdirectories.

    Example:
        Given a directory structure:
        - project/
          - main.py
          - utils/
            - helper.py
          - README.md

        Calling analyze_project("project") would return:
        [
            "project/main.py",
            "project/utils/helper.py"
        ]
    """
    
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(os.path.join(root, filename))
    return files
