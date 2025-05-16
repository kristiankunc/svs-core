# conftest.py
import subprocess


def pytest_sessionstart(session):
    subprocess.run(["pip", "install", "-e", "."], check=True)
