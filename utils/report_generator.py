from jinja2 import Template

def generate_html_report(static_analysis, nested_loops, dynamic_analysis):
    
    """
    Generate an HTML report using the provided analysis data and a Jinja2 template.

    Args:
        static_analysis (list): A list of static analysis suggestions or results.
        nested_loops (list): Information about nested loops, including line numbers and nesting levels.
        dynamic_analysis (str): A string containing dynamic profiling data, such as runtime and memory usage.

    Returns:
        str: The rendered HTML report as a string.

    Raises:
        FileNotFoundError: If the report template file is not found at the specified path.
        jinja2.TemplateError: If there are issues rendering the Jinja2 template.
    
    Example:
        static_analysis = ["Line 10: Optimize loop range(1000)."]
        nested_loops = [{"line": 15, "level": 2, "suggestion": "Reduce nesting."}]
        dynamic_analysis = "Runtime: 2.5s, Peak memory: 50MB"

        html_report = generate_html_report(static_analysis, nested_loops, dynamic_analysis)
        print(html_report)  # Outputs the complete HTML string.
    """
    
    template_path = "templates/report_template.html"
    with open(template_path, "r") as file:
        template = Template(file.read())
    return template.render(static_analysis=static_analysis, nested_loops=nested_loops, dynamic_analysis=dynamic_analysis)