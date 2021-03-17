import os
from pathlib import Path
from subprocess import check_output as shell

commit_id = shell("git rev-parse HEAD").decode("utf8").strip()
site = Path("site").absolute()

shell(f"mkdocs build --clean --site-dir {site}")

os.chdir(site)
cname = site / "CNAME"
cname.touch()
cname.write_text("django-simple-api.aber.sh")

shell("git init -q")
shell("git add . ")
shell(f'git commit -m "Build by {commit_id}"')
shell(
    "git remote add origin https://github.com/Django-Simple-API/django-simple-api.github.io"
)
shell("git push --force origin master")
