import json


def define_env(env):  # noqa: D103
    @env.macro
    def format_table(path: str) -> str:
        """Reads a JSON file and returns its content formatted as a table."""

        with open(path, "r") as file:
            data = json.load(file)

        if not data:
            return ""

        table = "\n\n### Overview\n\n"
        table += "| Property | Value |\n"
        table += "| --- | --- |\n"

        data.pop("$schema", None)

        ordered_keys = ["name", "description", "type"]
        for key in ordered_keys:
            if key in data and isinstance(data[key], str):
                table += f"| {key} | {data[key]} |\n"

        for key, value in data.items():
            if (
                isinstance(value, str)
                and key not in ordered_keys
                and key != "dockerfile"
            ):
                table += f"| {key} | {value} |\n"

        if "dockerfile" in data and data["dockerfile"]:
            table += '\n??? note "Dockerfile"\n'
            table += f"    ```dockerfile\n"
            # Indent each line of the dockerfile
            for line in data["dockerfile"].split("\n"):
                table += f"    {line}\n"
            table += "    ```\n"

        table += "\n### Configuration\n\n"
        table += "| Property | Value |\n"
        table += "| --- | --- |\n"

        display_order = ["type", "image", "start_cmd", "args"]

        for key in display_order:
            if key in data and not isinstance(data[key], str):
                value = data[key]
                formatted_value = _format_value(value)
                table += f"| {key} | {formatted_value} |\n"

        if "default_ports" in data and data["default_ports"]:
            table += "\n### Ports\n\n"
            table += "| Container | Host |\n"
            table += "| --- | --- |\n"
            for port in data["default_ports"]:
                container = port.get("container", "N/A")
                host = port.get("host", "Auto-assigned")
                table += f"| {container} | {host} |\n"

        if "default_volumes" in data and data["default_volumes"]:
            table += "\n### Volumes\n\n"
            table += "| Container Path | Host Path |\n"
            table += "| --- | --- |\n"
            for volume in data["default_volumes"]:
                container = volume.get("container", "N/A")
                host = volume.get("host", "Auto-assigned")
                table += f"| {container} | {host} |\n"

        if "default_env" in data and data["default_env"]:
            table += "\n### Environment Variables\n\n"
            table += "| Variable | Value |\n"
            table += "| --- | --- |\n"
            for env_var in data["default_env"]:
                name = env_var.get("name", "N/A")
                value = env_var.get("value", "")
                table += f"| {name} | {value} |\n"

        if "healthcheck" in data and data["healthcheck"]:
            table += "\n### Healthcheck\n\n"
            table += "| Property | Value |\n"
            table += "| --- | --- |\n"
            for key, value in data["healthcheck"].items():
                formatted_value = _format_value(value)
                table += f"| {key} | {formatted_value} |\n"

        return table


def _format_value(value):
    """Format a value for display in the table."""
    if value is None:
        return "Not set"
    elif isinstance(value, bool):
        return "Yes" if value else "No"
    elif isinstance(value, list):
        if len(value) == 0:
            return "Empty"
        return ", ".join(str(item) for item in value)
    elif isinstance(value, dict):
        return json.dumps(value, indent=2)
    else:
        return str(value)
