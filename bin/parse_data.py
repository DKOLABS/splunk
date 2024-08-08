import json
import yaml
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()


# Custom SafeDumper to preserve order
class OrderedDumper(yaml.SafeDumper):
    pass


def _dict_representer(dumper, data):
    return dumper.represent_dict(data.items())


OrderedDumper.add_representer(OrderedDict, _dict_representer)


def convert(file_name, in_data):

    out_dir = ROOT / "parsed_data" / in_data["acl"]["app"]
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / file_name

    ordered_data = OrderedDict(
        [
            ("name", in_data["name"]),
            ("id", in_data["id"]),
            ("author", in_data["author"]),
            ("updated", in_data["updated"]),
            ("app", in_data["acl"]["app"]),
        ]
    )

    search_lines = in_data["content"]["search"].split("\n")
    formatted_lines = ["  " + line for line in search_lines]
    formatted_search = "\n".join(formatted_lines)

    yaml_data = yaml.dump(
        ordered_data, Dumper=OrderedDumper, default_flow_style=False
    ).rstrip()

    with open(out_dir / file_name, "w", encoding="utf-8") as out_file:
        out_file.write(yaml_data)
        out_file.write("\nsearch: |\n")
        out_file.write(formatted_search)


if __name__ == "__main__":
    raw_data_dir = ROOT / "raw_data"

    for file in raw_data_dir.iterdir():
        if file.is_file() and file.suffix == ".json":
            with open(file, "r") as f:
                data = json.load(f)
            convert(file.stem + ".yaml", data)
