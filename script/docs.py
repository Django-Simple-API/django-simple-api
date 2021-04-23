import os
from pathlib import Path
from subprocess import check_output as shell

commit_id = shell("git rev-parse HEAD", shell=True).decode("utf8").strip()
site = Path("site").absolute()

shell(f"mkdocs build --clean --site-dir {site}", shell=True)

os.chdir(site)
cname = site / "CNAME"
cname.touch()
cname.write_text("django-simple-api.aber.sh")

shell("git init -q", shell=True)
shell("git add . ", shell=True)
shell(f'git commit -m "Build by {commit_id}"', shell=True)
shell(
    "git remote add origin https://github.com/Django-Simple-API/django-simple-api.github.io", shell=True)
shell("git push --force origin master", shell=True)
