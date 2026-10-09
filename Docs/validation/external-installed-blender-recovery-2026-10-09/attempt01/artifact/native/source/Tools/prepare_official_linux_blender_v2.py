"""Checksum-pinned official archive preparation; no scientific experiment."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import time
import urllib.request
import urllib.error


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(2**20):
            value.update(chunk)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    profile = json.loads(args.profile.read_bytes())
    args.directory.mkdir(exist_ok=False)
    spec = profile['official_blender']; archive = args.directory / 'official.tar.xz'
    started = time.monotonic(); count = 0
    attempts = []; received = False
    for url in spec['transport_urls']:
        request = urllib.request.Request(url, headers={'User-Agent': spec['user_agent']})
        attempt_start = time.monotonic(); count = 0
        try:
            with urllib.request.urlopen(request, timeout=60) as response, archive.open('wb') as stream:
                while chunk := response.read(2**20):
                    count += len(chunk)
                    if count > profile['limits']['archive_mib'] * 2**20 or time.monotonic() - started > profile['limits']['preparation_seconds']:
                        raise ValueError('Official download exceeds declared envelope')
                    stream.write(chunk)
            attempts.append({'url': url, 'received_bytes': count, 'seconds': time.monotonic() - attempt_start, 'download_completed': True})
            received = True; break
        except urllib.error.URLError as exc:
            attempts.append({'url': url, 'received_bytes': count, 'seconds': time.monotonic() - attempt_start, 'download_completed': False, 'failure_type': type(exc).__name__, 'http_status': getattr(exc, 'code', None)})
        args.receipt.write_bytes((json.dumps({'download_attempts': attempts, 'scientific_worker_executed': False}, indent=2) + '\n').encode())
    if not received:
        raise ValueError('All prospectively declared TLS transports failed')
    if digest(archive) != spec['archive_sha256'] or count != spec['archive_bytes']:
        raise ValueError('Official archive checksum or size mismatch')
    with tarfile.open(archive, 'r:xz') as source:
        # Python's data filter rejects absolute paths, outside links and special files.
        source.extractall(args.directory, filter='data')
    executable = args.directory / spec['binary_member']
    if digest(executable) != spec['binary_sha256']:
        raise ValueError('Official executable checksum mismatch')
    version = subprocess.run([str(executable), '--version'], capture_output=True, text=True, timeout=30)
    report = {'archive_url': spec['archive_url'], 'actual_transport_url': url, 'download_attempts': attempts, 'archive_sha256': spec['archive_sha256'],
              'archive_bytes': count, 'binary_sha256': spec['binary_sha256'],
              'executable': str(executable.resolve()), 'version_exit_code': version.returncode,
              'version_stdout': version.stdout, 'version_stderr': version.stderr,
              'seconds': time.monotonic() - started, 'tls_verified': True,
              'scientific_worker_executed': False}
    args.receipt.write_bytes((json.dumps(report, indent=2) + '\n').encode())
    if version.returncode:
        raise ValueError('Official native executable environment preflight failed')
    print(json.dumps({'prepared': True, 'seconds': report['seconds']}), flush=True)


if __name__ == '__main__':
    main()
