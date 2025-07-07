# Uses typer docs utility to compile CLI documentation from Python files.
# Dumps the output into a markdown file append to the template file.

import os

TEMPLATE_FILE = "docs/cli.md.template"
OUTPUT_FILE = "docs/cli.md"


def get_all_cli_files(directory: str) -> list[str]:
    cli_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                cli_files.append(os.path.join(root, file))
    return cli_files


def generate_docs(file: str) -> str:
    filename = os.path.splitext(os.path.basename(file))[0]
    output = os.popen(f"typer {file} utils docs --name {filename.capitalize()}").read()
    return output


def downgrade_headings(docs: str) -> str:
    return "\n".join(
        f"#{line}" if line.startswith("#") else line for line in docs.splitlines()
    )


if __name__ == "__main__":
    files = ["svs_core/__main__.py"]

    files += get_all_cli_files("svs_core/cli")

    print(f"Discovered {files}")

    docs = ""
    for file in files:
        docs += generate_docs(file)

    docs = downgrade_headings(docs)

    with open(TEMPLATE_FILE, "r") as template_file:
        template_content = template_file.read()

    with open(OUTPUT_FILE, "a") as f:
        f.write(template_content)
        f.write("\n")
        f.write(docs)
