from . import get_cfg, default_cluster
from ....core.k8s.core import K8s
from ....utils.progress import FileProgressTqdm


def backup(namespace, name, dest, cluster=default_cluster, progress_cls=FileProgressTqdm):
    data = get_cfg(cluster).get()
    k8s = K8s.from_manual(data['host'], data['token'], data['port'])
    pod_name = next(k8s.list_pods_of_deploy(namespace, name)).metadata.name
    k8s.get_command_output(lambda: k8s.get_stream(namespace, pod_name), 'python manage.py backup')
    k8s.cp_dir_from_pod(namespace, pod_name, '.dbbackup', dest, progress_cls=progress_cls)


def restore(namespace, name, src, cluster=default_cluster, progress_cls=FileProgressTqdm):
    data = get_cfg(cluster).get()
    k8s = K8s.from_manual(data['host'], data['token'], data['port'])
    pod_name = next(k8s.list_pods_of_deploy(namespace, name)).metadata.name
    k8s.cp_dir_to_pod(namespace, pod_name, src, '.dbbackup', progress_cls=progress_cls)
    k8s.get_command_output(lambda: k8s.get_stream(namespace, pod_name), 'python manage.py restore')
