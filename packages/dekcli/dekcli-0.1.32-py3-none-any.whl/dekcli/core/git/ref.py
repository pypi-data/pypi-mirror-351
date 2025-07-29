def ref_short_name(ref):
    return ref.path.split('/', 2)[-1]


def get_refs_name(origin):
    result = []
    for ref in origin.refs:
        result.append(ref.name[len(origin.name) + 1:])
    return result
