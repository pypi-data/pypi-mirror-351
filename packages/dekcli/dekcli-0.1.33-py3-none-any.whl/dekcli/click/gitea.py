import os
import time
import git
import typer
from dektools.cfg import ObjectCfg
from dektools.file import sure_dir, normal_path
from dektools.serializer.yaml import yaml
from dektools.version import version_is_valid, version_cmp_key
from deksecrets.core import gitea
from deksecrets.tools.gitea import get_gitea_auth_info, get_gitea_ins
from ..core.git.repo import list_repos

default_name = 'index'

app = typer.Typer(add_completion=False)


def get_cfg(name):
    return ObjectCfg(__name__, 'gitea', name, module=True)


def get_ins(name):
    data = get_cfg(name).get()
    auth = data['auth']
    return get_gitea_ins(data['url'], auth['token'], auth['username'], auth['password'])


@app.command()
def login(url, token=None, username=None, password=None, name=default_name):  # url: {schema}://{host}{port}
    token, username, password = get_gitea_auth_info(token, username, password)
    get_cfg(name).update(dict(url=url.rstrip('/ '), auth=dict(token=token, username=username, password=password)))


@app.command()
def logout(name=default_name):
    get_cfg(name).update({})


@app.command()
def pull(path, name=default_name):
    path = normal_path(path)
    sure_dir(path)
    ins = get_ins(name)
    for org in gitea.get_orgs(ins):
        for repo in org.get_repositories():
            path_repo = os.path.join(path, repo.get_full_name())
            sure_dir(path_repo)
            git.Repo.clone_from(repo.ssh_url, path_repo)


@app.command()
def init(path, name=default_name):
    ins = get_ins(name)
    ors = gitea.OrgRepoSure(ins)

    path_index = os.path.join(path, 'index.yaml')
    if os.path.isfile(path_index):
        data_index = yaml.load(path_index)
    else:
        data_index = {}

    for org_name, org_data in data_index.get('orgs', {}).items():
        print(f"org: {org_name}", flush=True)
        org, _ = ors.get_org_repos(org_name)
        gitea.patch_org(ins, org.name, org_data or {})

    for orn, url in data_index.get('mirrors', {}).items():
        org_name, repo_name = orn.split('/')
        print(f"mirror: {url}", flush=True)
        ors.get_or_mirror(org_name, repo_name, url)

    tokens = {}
    for name, scopes in data_index.get('tokens', {}).items():
        gitea.delete_token(ins, name)
        tokens[name] = gitea.create_token(ins, name, scopes)

    def get_value(v):
        token_marker = 'tokens.'
        if v.startswith(token_marker):
            return tokens[v[len(token_marker):]]
        return v

    for key, variable_value in data_index.get('variables', {}).items():
        org_name, variable_name = key.split('/')
        print(f"variable: {org_name} {variable_name}", flush=True)
        ors.get_org_repos(org_name)
        gitea.org_delete_variable(ins, org_name, variable_name)
        gitea.org_create_variable(ins, org_name, variable_name, get_value(variable_value))

    for key, secret_value in data_index.get('secrets', {}).items():
        org_name, secret_name = key.split('/')
        print(f"secret: {org_name} {secret_name}", flush=True)
        ors.get_org_repos(org_name)
        gitea.org_create_or_update_secret(ins, org_name, secret_name, get_value(secret_value))


@app.command()
def push(path, name=default_name):
    ins = get_ins(name)
    ors = gitea.OrgRepoSure(ins)
    for org_name, org_data in list_repos(path).items():
        for repo_name, repo_data in org_data.items():
            mirror = repo_data['mirror']
            branches = repo_data['branches']
            if mirror:
                print(f"mirror: {mirror}", flush=True)
                ors.get_or_mirror(org_name, repo_name, mirror)
            elif branches:
                print(f"enter: {repo_data['path']}", flush=True)
                repo = ors.get_or_create(org_name, repo_name, branches[0])
                git_repo = git.Repo(repo_data['path'])
                origin = git_repo.create_remote('origin', repo.ssh_url)
                print(f"pushing: {repo.ssh_url}", flush=True)
                for name in branches:
                    origin.push(refspec=f"{name}:{name}")
                tags = repo_data['tags']
                tags_versions = []
                tags_others = []
                for tag in tags:
                    if tag.startswith('v') and version_is_valid(tag[1:]):
                        tags_versions.append(tag)
                    else:
                        tags_others.append(tag)
                gitea.patch_repo(ins, org_name, repo_name, dict(has_actions=False))
                time.sleep(0.5)
                tags_versions = sorted(tags_versions, key=version_cmp_key(lambda x: x[1:]))
                push_tag_count = 2
                for tag in tags_others + tags_versions[:-push_tag_count]:
                    origin.push(tag)
                if tags_versions:
                    time.sleep(1)
                    gitea.patch_repo(ins, org_name, repo_name, dict(has_actions=True))
                    time.sleep(0.5)
                for tag in tags_versions[-push_tag_count:]:
                    origin.push(tag)
