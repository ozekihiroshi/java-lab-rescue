#!/usr/bin/env python3
"""Repeatable offline configuration tests using an existing local Hub image."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
from verify import verify

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hub-image', default='java-lab-rescue-hub:local')
    args = parser.parse_args()
    values = {
        'JAVA_LAB_HOST': 'java.school.test', 'MOODLE_ORIGIN': 'https://moodle.school.test',
        'JAVA_HUB_IMAGE': 'registry.school.test/hub@sha256:' + 'a' * 64,
        'JAVA_SINGLEUSER_IMAGE': 'registry.school.test/user@sha256:' + 'b' * 64,
        'LTI_CLIENT_ID': 'test-client', 'LTI_DEPLOYMENT_IDS': 'test-deployment',
        'JAVA_ACTIVE_SERVER_LIMIT': '2',
    }
    with tempfile.NamedTemporaryFile(mode='w') as settings:
        settings.write('\n'.join(k + '=' + v for k, v in values.items()))
        settings.flush()
        result = subprocess.run(['docker', 'compose', '--env-file', settings.name,
                                 '-f', str(ROOT / 'compose.yml'), 'config', '--format', 'json'],
                                check=True, capture_output=True, text=True, timeout=30)
    model = json.loads(result.stdout)
    hub = verify(model)
    for kind in ('ports', 'image', 'network'):
        invalid = json.loads(result.stdout)
        if kind == 'ports':
            invalid['services']['jupyterhub']['ports'] = [{'published': '8000'}]
        elif kind == 'image':
            invalid['services']['jupyterhub']['image'] = 'hub:latest'
        else:
            invalid['networks']['learners']['internal'] = False
        try:
            verify(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError('Unsafe topology accepted: ' + kind)
    cmd = ['docker', 'run', '--rm', '--pull=never', '--network', 'none', '--read-only',
           '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
           '--memory', '512m', '--cpus', '1', '--pids-limit', '64',
           '--tmpfs', '/tmp', '--tmpfs', '/srv/jupyterhub/data',
           '-v', str(ROOT) + ':/srv/public:ro']
    for key, value in hub['environment'].items():
        cmd += ['-e', key + '=' + value]
    subprocess.run(cmd + ['--entrypoint', 'python', args.hub_image, '/srv/public/test_config.py'],
                   check=True, timeout=60)
    result = subprocess.run(cmd + ['--entrypoint', 'jupyterhub', args.hub_image,
                                   '-f', '/srv/public/jupyterhub_config.py', '--show-config'],
                            capture_output=True, text=True, timeout=60)
    if result.returncode or 'not recognized' in result.stderr:
        raise RuntimeError('Hub configuration load failed: ' + result.stderr)
    print('PASS: topology, unsafe configuration rejection, LTI access hook, installed Hub config load')
    print('No network, Docker socket, persistent user data, registry push or deployment used.')


if __name__ == '__main__':
    main()
