import os
import git
from dektools.file import read_text
from .ref import ref_short_name


def list_repos(path_dir):
    result = {}
    for org_name in os.listdir(path_dir):
        path_org = os.path.join(path_dir, org_name)
        if not os.path.isdir(path_org):
            continue
        for repo_name in os.listdir(path_org):
            path_repo = os.path.join(path_org, repo_name)
            if not os.path.isdir(path_repo):
                continue
            path_mark_git = os.path.join(path_repo, '.git')
            if os.path.exists(path_mark_git):
                data_org = result.setdefault(org_name, {})
                data_repo = data_org.setdefault(repo_name, {})
                data_repo['path'] = path_repo
                mirror = read_text(path_mark_git).strip() if os.path.isfile(path_mark_git) else None
                data_repo['mirror'] = mirror
                if not mirror:
                    git_repo = git.Repo(path_repo)
                    for remote in git_repo.remotes:
                        git_repo.delete_remote(remote)
                    ref_list = [ref_short_name(ref) for ref in git_repo.references]
                    tag_list = [ref_short_name(ref) for ref in git_repo.tags]
                    branch_list = sorted(set(ref_list) - set(tag_list))
                    data_repo.update(dict(
                        refs=ref_list,
                        tags=tag_list,
                        branches=branch_list
                    ))
    return result
