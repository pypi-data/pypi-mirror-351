import os
import sys
import time
import shlex
import urllib3
from threading import Thread
from kubernetes.stream import stream
from kubernetes import client, config
from dektools.file import sure_dir, remove_path, iter_relative_path_complete


class K8s:
    apps_cls = client.AppsV1Api
    core_cls = client.CoreV1Api

    def __init__(self, api_client: client.ApiClient = None):
        self.apps = self.apps_cls(api_client)
        self.core = self.core_cls(api_client)

    @classmethod
    def from_env(cls):
        config.load_kube_config()
        return cls(None)

    @classmethod
    def from_manual(cls, host, token, port=6443):
        configuration = client.Configuration()
        configuration.verify_ssl = False
        configuration.debug = False
        urllib3.disable_warnings()
        # configuration.ssl_ca_cert =
        configuration.api_key['authorization'] = token
        configuration.api_key_prefix['authorization'] = 'Bearer'
        configuration.host = f"https://{host}:{port}"
        return cls(client.ApiClient(configuration))

    def list_namespaces(self):
        for namespace in self.core.list_namespace().items:
            yield namespace.metadata.name

    def list_pods_of_deploy(self, namespace, name):
        rs_name = None
        for rs in self.apps.list_namespaced_replica_set(namespace).items:
            for owner in rs.metadata.owner_references:
                if owner.name == name:
                    rs_name = rs.metadata.name
                    break
        for pod in self.core.list_namespaced_pod(namespace).items:
            for owner in pod.metadata.owner_references:
                if owner.name == rs_name:
                    yield pod

    def get_stream(self, namespace, name, shell=None, tty=False):
        return stream(
            self.core.connect_get_namespaced_pod_exec,
            name,
            namespace,
            command=shlex.split(shell or 'sh'),
            stderr=True, stdin=True,
            stdout=True, tty=tty,
            _preload_content=False)

    def enter_pod(self, namespace, name, commands=None, shell=None):
        resp = self.get_stream(namespace, name, shell, True)

        def read():
            while resp.is_open():
                try:
                    char = sys.stdin.read(1)
                except UnicodeDecodeError:
                    return
                resp.update()
                if resp.is_open():
                    resp.write_stdin(char)

        Thread(target=read, args=[]).start()
        if commands:
            for command in commands:
                resp.write_stdin(command + '\n')
        while resp.is_open():
            data = resp.read_stdout(1)
            if resp.is_open():
                if len(data or "") > 0:
                    sys.stdout.write(data)
                    sys.stdout.flush()

    @staticmethod
    def _get_command_output(resp, command, timeout=None):
        lock = False
        size_total = None
        time_expected = 0
        output = ''
        while resp.is_open():
            if resp.peek_stderr():
                print('STDERR: {0}'.format(resp.read_stderr()))
                break
            if resp.peek_stdout():
                result = resp.read_stdout()
                if size_total is None:
                    s, result = result.split(' ', 1)
                    size_total = int(s)
                    output += result
                else:
                    output += result
                if len(output) >= size_total:
                    return output
            if not lock:
                resp.write_stdin(f"""sh -c 'OUTPUT="$({command})" && echo $(expr length + "$OUTPUT")" ""$OUTPUT"'\n""")
                lock = True
                time_expected = time.time()
            else:
                if timeout is not None and time_expected > 0 and time.time() - time_expected > timeout:
                    return False

    @classmethod
    def get_command_output(cls, get_resp, command, timeout=None):
        while True:
            resp = get_resp()
            result = cls._get_command_output(resp, command, timeout)
            if result is None:
                resp.close()
                raise IOError(f"Running command failed: {command}")
            elif result is False:
                resp.close()
                continue
            else:
                resp.close()
                return result

    def list_dir_in_pod(self, namespace, name, path):
        path_glob = f"{path}/*" if path else '*'
        items = self.get_command_output(
            lambda: self.get_stream(namespace, name),
            f"""stat -c "%f %n" -- {path_glob} 2> /dev/null || true""",
            1
        )
        items = items.strip()
        if items:
            for item in items.splitlines():
                typed, file = item.split(' ', 1)
                file = os.path.basename(file.strip())
                p = f"{path}/{file}" if path else file
                if typed == '81a4':
                    yield p, True
                elif typed == '41ed':
                    yield from self.list_dir_in_pod(namespace, name, p)
        else:
            yield path, False

    def cp_dir_to_pod(self, namespace, name, src, dest, **kwargs):
        for item, fp, is_file in iter_relative_path_complete(src):
            if is_file:
                with open(fp, 'rb') as f:
                    self.cp_file_to_pod(namespace, name, f, f"{dest}/{item}", **kwargs)
            else:
                self.get_command_output(
                    lambda: self.get_stream(namespace, name),
                    f"""mkdir -p {dest}/{item}""",
                    1
                )

    def cp_dir_from_pod(self, namespace, name, src, dest, **kwargs):
        for file, is_file in self.list_dir_in_pod(namespace, name, src):
            path = f"{dest}/{file[len(src) + 1:]}"
            if is_file:
                self.cp_file_from_pod(namespace, name, file, path, **kwargs)
            else:
                sure_dir(path)

    def cp_file_to_pod(self, namespace, name, file, path, block_size=None, progress_cls=None):
        block_size = block_size or 64 * 2 ** 10
        resp = self.get_stream(namespace, name)

        prepare = False

        file.seek(0, os.SEEK_END)
        size_total = file.tell()
        file.seek(0)

        size_send = 0

        progress = progress_cls(path, size_total) if progress_cls else None
        while resp.is_open():
            if resp.peek_stderr():
                print('STDERR: {0}'.format(resp.read_stderr()))
                break
            if not prepare:
                path_dir = os.path.dirname(path)
                if path_dir:
                    resp.write_stdin(f'mkdir -p "{path_dir}"\n')
                resp.write_stdin(f'rm -rf "{path}" && touch {path} \n')
                prepare = True
            bs = file.read(block_size)
            if bs:
                if progress:
                    progress.update(len(bs))
                ss = "".join(["\\%03o" % b for b in bs])
                resp.write_stdin(f"""printf "%b" '{ss}' >> {path}\n""")
            else:
                break
            size_send += block_size
            time.sleep(0)
        resp.close()
        if progress:
            progress.close()

    def cp_file_from_pod(self, namespace, name, src, dest, block_size=None, timeout=None, progress_cls=None):
        block_size = block_size or 64 * 2 ** 10
        timeout = timeout or 1.0
        size_total = None
        size_received = 0
        size_expected = 0
        size_expected_time = 0

        size_prepare = False
        size_get = False

        progress = None
        path_dir = os.path.dirname(dest)
        if path_dir:
            sure_dir(path_dir)
        remove_path(dest)
        with open(dest, 'wb') as file:
            while size_total is None or size_received < size_total:
                resp = self.get_stream(namespace, name)
                while resp.is_open():
                    if resp.peek_stderr():
                        print('STDERR: {0}'.format(resp.read_stderr()))
                        break
                    if not size_prepare:
                        resp.write_stdin(f'wc -c < "{src}"\n')
                        size_prepare = True
                        size_get = True
                    if resp.peek_stdout():
                        ss = resp.read_stdout()
                        if size_get:
                            size_total = int(ss)
                            progress = progress_cls(src, size_total) if progress_cls else None
                            size_get = False
                        else:
                            bs = bytes.fromhex(ss)
                            file.write(bs)
                            if progress:
                                progress.update(len(bs))
                            size_received += len(bs)

                    if size_total is not None:
                        if size_received >= size_total:
                            break
                        if size_received >= size_expected:
                            resp.write_stdin(
                                """od -An -v --format=x1 -j %d -N %d "%s" | tr -d '\\r\\n '\n""" % (
                                    size_received, block_size, src
                                )
                            )
                            size_expected = size_received + block_size
                            size_expected_time = time.time()
                        else:
                            if size_expected_time > 0 and time.time() - size_expected_time > timeout:
                                size_expected_time = 0
                                size_expected = size_received
                                resp.close()
                                break
                    time.sleep(0)
                resp.close()
            if progress:
                progress.close()
