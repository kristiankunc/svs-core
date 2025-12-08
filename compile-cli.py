# Uses typer docs utility to compile CLI documentation from Python files.
# Dumps the output into a markdown file append to the template file.

import os
import re

TEMPLATE_FILE = "docs/cli.md.template"
OUTPUT_FILE = "docs/cli.md"

os.environ["DATABASE_URL"] = "sqlite:///./svs_core.db"


def generate_docs(file: str) -> str:
    """Generates CLI documentation using typer's built-in docs utility."""
    stream = os.popen(f"typer {file} utils docs --name svs")
    output = stream.read()
    exit_code = stream.close()

    if exit_code is not None:
        print(f"Error: Failed to generate docs for {file}.")
        exit(1)

    output = output.replace("SVS CLI\n\n", "")
    output = re.sub(
        r".*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}: \[[A-Z]+\].*\n?", "", output
    )
    return output


def downgrade_headings(docs: str) -> str:
    """Downgrades headings by one level and comments out top-level headings."""
    return "\n".join(
        f"#{line}" if line.startswith("#") else line for line in docs.splitlines()
    )


if __name__ == "__main__":
    docs = generate_docs("svs_core/__main__.py")

    docs = downgrade_headings(docs)

    with open(TEMPLATE_FILE, "r") as template_file:
        template_content = template_file.read()

    with open(OUTPUT_FILE, "w") as f:
        f.write(template_content)
        f.write("\n")
        f.write(docs)
