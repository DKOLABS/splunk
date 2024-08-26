import jinja2
import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

# Function to render a Jinja2 template with the given context
def render_template(template_path, context):
    template_loader = jinja2.FileSystemLoader(searchpath=template_path.parent)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_path.name)
    return template.render(context)


def normalize_json(input_data):
    output_data = dict()

    # API Data
    if 1 == 1:
        output_data["name"] = input_data["name"]
        output_data["id"] = input_data["id"]
        output_data["author"] = input_data["author"]
        output_data["updated"] = input_data["updated"]
        output_data["disabled"] = input_data["content"]["disabled"]
        output_data["app"] = input_data["acl"]["app"]
        output_data["type"] = "report" if input_data["content"]["alert_type"] == "always" else "alert"
        output_data["description"] = input_data["content"]["description"]
        output_data["search"] = input_data["content"]["search"].replace("\n", "\n  ")
        output_data["cron_schedule"] = input_data["content"]["cron_schedule"]
        output_data["earliest_time"] = input_data["content"]["dispatch.earliest_time"]
        output_data["latest_time"] = input_data["content"]["dispatch.latest_time"]
    # Manual Data
    else:
        pass

    return output_data


if __name__ == "__main__":
    
    # Paths to Jinja2 templates
    saved_search_template = ROOT_DIR / "templates/saved_search.yaml"

    # Working Directories
    raw_data_dir = ROOT_DIR / "raw_data"
    parsed_data_dir = ROOT_DIR / "parsed_data"

    # Processing
    for file in raw_data_dir.iterdir():
        if file.is_file() and file.suffix == ".json":
            with open(file, "r") as f:
                file_data = json.load(f)

            normalized_data = normalize_json(file_data)
            output = render_template(saved_search_template, normalized_data)

            out_dir = parsed_data_dir / normalized_data["app"]
            if not out_dir.exists():
                out_dir.mkdir(parents=True, exist_ok=True)

            out_file = out_dir / f"{file.stem}.yaml"

            with open(out_file, "w") as f:
                f.write(output)
            