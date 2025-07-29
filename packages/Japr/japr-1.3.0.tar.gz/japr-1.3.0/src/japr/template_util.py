from git import InvalidGitRepositoryError, Repo
from git.util import expand_path
from jinja2 import Environment, PackageLoader
import os
import re


def _convert_ssh_to_http(url):
    if "@" in url:
        return re.sub(r"^.+@(.+):(.+?)(\.git)?$", r"https://\1/\2", url)
    return url


def template(template_file, directory):
    env = Environment(
        loader=PackageLoader("japr"),
    )
    template = env.get_template(template_file)

    try:
        github_remote_url = Repo(directory).remote("origin").url

        github_remote_url = _convert_ssh_to_http(github_remote_url)

        if not github_remote_url.endswith("/"):
            github_remote_url[:-1]
    except InvalidGitRepositoryError:
        github_remote_url = None

    vars = {
        "project_name": os.path.split(directory)[1]
        .title()
        .replace("-", " ")
        .replace("_", " "),
        "github_remote_url": github_remote_url,
    }

    return template.render(vars)
