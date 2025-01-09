from jinja2 import Template

def generate_html_report(static_analysis, nested_loops, dynamic_analysis):
    template_path = "templates/report_template.html"
    with open(template_path, "r") as file:
        template = Template(file.read())
    return template.render(static_analysis=static_analysis, nested_loops=nested_loops, dynamic_analysis=dynamic_analysis)