import os
import signal
import subprocess
import sys
import time


def execute(*commands):
    process = subprocess.Popen(" ".join(commands), cwd=os.getcwd(), shell=True)

    def sigterm_handler(sign, frame):
        process.terminate()
        process.wait()

    signal.signal(signal.SIGTERM, sigterm_handler)

    while process.poll() is None:
        time.sleep(1)
    return process.poll()


def shell(command: str) -> None:
    exit_code = execute(command)
    if exit_code != 0:
        sys.exit(exit_code)


if __name__ == "__main__":
    shell("black --check django_simple_api example")
    shell("mypy -p django_simple_api --ignore-missing-imports")
    shell("flake8 django_simple_api --ignore W503,E203,E501,E731")
    shell("pytest -o log_cli=true -o log_cli_level=DEBUG")
    shell("python manage.py test -v 2")
