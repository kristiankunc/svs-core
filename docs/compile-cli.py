# Uses typer docs utility to compile CLI documentation from Python files.
# Dumps the output into a markdown file append to the template file.

import os

TEMPLATE_FILE = "docs/cli.md.template"
OUTPUT_FILE = "docs/cli.md"


def generate_docs(file: str) -> str:
    output = (
        os.popen(f"typer {file} utils docs --name svs")
        .read()
        .replace("SVS CLI\n\n", "")
    )
    return output


def downgrade_headings(docs: str) -> str:
    return "\n".join(
        f"#{line}" if line.startswith("#") else line for line in docs.splitlines()
    )


if __name__ == "__main__":
    docs = generate_docs("svs_core/__main__.py")

    docs = downgrade_headings(docs)

    with open(TEMPLATE_FILE, "r") as template_file:
        template_content = template_file.read()

    with open(OUTPUT_FILE, "a") as f:
        f.write(template_content)
        f.write("\n")
        f.write(docs)
