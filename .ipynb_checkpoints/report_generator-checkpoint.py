from jinja2 import Template

def generate_html_report(static_analysis, dynamic_analysis):
    # Path to the template file
    template_path = "templates/report_template.html"

    # Load the template
    with open(template_path, "r") as file:
        template = Template(file.read())

    # Render the HTML report
    return template.render(static_analysis=static_analysis, dynamic_analysis=dynamic_analysis)
