from dektools.cfg import ObjectCfg

default_cluster = 'default'


def get_cfg(cluster):
    return ObjectCfg(__name__, 'k8s', cluster, module=True)

