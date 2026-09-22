#!/usr/bin/env python3
"""Validate the explicit public configuration without starting a service."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def verify(model):
    if model.get('name') != 'java-lab-public' or set(model['services']) != {'jupyterhub'}:
        raise ValueError('Unexpected public project or services')
    hub = model['services']['jupyterhub']
    if hub.get('ports') or 'build' in hub:
        raise ValueError('Public Hub must not publish ports or build implicitly')
    for image in (hub['image'], hub['environment']['JAVA_SINGLEUSER_IMAGE']):
        if not re.fullmatch(r'[^\s]+@sha256:[0-9a-f]{64}', image):
            raise ValueError('Both images must be pinned by registry digest')
    if not model['networks']['learners'].get('internal'):
        raise ValueError('Learner network must be internal')
    if model['networks']['learners']['name'] != 'java-lab-public-learners':
        raise ValueError('Unexpected learner network')
    labels = hub['labels']
    if labels.get('traefik.http.routers.java-lab-public.tls') != 'true':
        raise ValueError('HTTPS is required')
    if any('prototype' in v.get('source', '') for v in hub['volumes'] if v['type'] == 'volume'):
        raise ValueError('Do not reuse local prototype volumes')
    return hub


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, default=ROOT / '.env.production')
    args = parser.parse_args()
    if not args.env_file.is_file():
        raise ValueError('Copy .env.production.example and configure the deployment first')
    result = subprocess.run(['docker', 'compose', '--env-file', str(args.env_file.resolve()),
                             '-f', str(ROOT / 'compose.yml'), 'config', '--format', 'json'],
                            capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise ValueError('Compose configuration failed; check required settings')
    hub = verify(json.loads(result.stdout))
    # Use the exact locally available release image; never pull or mount Docker/data.
    cmd = ['docker', 'run', '--rm', '--pull=never', '--network', 'none', '--read-only',
           '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--memory', '512m',
           '--cpus', '1', '--pids-limit', '64', '--tmpfs', '/tmp',
           '--tmpfs', '/srv/jupyterhub/data',
           '-v', f'{ROOT}:/srv/public:ro']
    for key, value in hub['environment'].items():
        cmd += ['-e', f'{key}={value}']
    cmd += ['--entrypoint', 'jupyterhub', hub['image'], '-f', '/srv/public/jupyterhub_config.py', '--show-config']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    if result.returncode or 'not recognized' in result.stderr:
        raise ValueError('Hub configuration validation failed; verify image availability and public settings')
    print('OK: Compose topology and pinned Hub configuration. No public services started.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
