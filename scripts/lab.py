#!/usr/bin/env python3
"""Local Java Lab lifecycle. No AWS operations or volume deletion."""
import argparse
import fcntl
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ['docker', 'compose', '--project-directory', str(ROOT), '--env-file', str(ROOT / '.env'), '-f', str(ROOT / 'compose.yml')]


def output(cmd):
    return subprocess.check_output(cmd, text=True)


def model():
    if not Path(COMPOSE[COMPOSE.index('--env-file') + 1]).is_file():
        raise RuntimeError('Copy .env.example to .env and configure Moodle first')
    value = json.loads(output(COMPOSE + ['config', '--format', 'json']))
    client = value['services']['jupyterhub']['environment']['LTI_CLIENT_ID']
    if not client or 'REPLACE' in client:
        raise RuntimeError('Configure the Moodle LTI client ID in .env')
    return value


def inventory():
    ids = output(['docker', 'ps', '-aq']).split()
    return json.loads(output(['docker', 'inspect', *ids])) if ids else []


def selected(config, items):
    settings = config['services']['jupyterhub']['environment']
    network = settings.get('JAVA_LEARNER_NETWORK', 'java-lab-public-learners')
    prefix = settings.get('JAVA_USER_VOLUME_PREFIX', 'java-lab-public-user') + '-'
    hubs, learners = [], []
    for item in items:
        labels = item['Config'].get('Labels') or {}
        # DockerSpawner inherits image-build Compose labels. Identify learners
        # by BOTH their private network and their persistent workspace volume.
        is_learner = network in item['NetworkSettings']['Networks'] and any(
            m.get('Name', '').startswith(prefix) and m['Destination'] == '/home/jovyan/work'
            for m in item['Mounts'])
        if is_learner:
            learners.append(item)
        elif labels.get('com.docker.compose.project') == config['name'] and labels.get('com.docker.compose.service') in ('jwks', 'jupyterhub'):
            hubs.append(item)
    return hubs, learners


def wait_healthy(config):
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        hubs, _ = selected(config, inventory())
        good = {i['Config']['Labels'].get('com.docker.compose.service') for i in hubs
                if i['State']['Running'] and i['State'].get('Health', {}).get('Status') == 'healthy'}
        if ({'jwks', 'jupyterhub'} & set(config['services'])) <= good:
            print('PASS: configured services are healthy', flush=True)
            return
        time.sleep(2)
    raise RuntimeError('Health timeout; inspect status and logs')


def main():
    global COMPOSE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'up', 'start', 'stop', 'status', 'logs', 'check'])
    parser.add_argument('--public', action='store_true', help='Explicitly select the separate public environment')
    parser.add_argument('--tail', type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.tail <= 500:
        parser.error('--tail must be 1..500')
    if args.public:
        COMPOSE = ['docker', 'compose', '--env-file', str(ROOT / 'public/.env.production'), '-f', str(ROOT / 'public/compose.yml')]
        if args.action == 'build':
            parser.error('Public images must be built and pinned separately')
        if args.action in ('up', 'start'):
            subprocess.run(['python3', str(ROOT / 'public/verify.py')], check=True)
    config = model()
    services = [name for name in ('jwks', 'jupyterhub') if name in config['services']]
    runtime = ROOT / 'runtime'
    runtime.mkdir(exist_ok=True)
    with (runtime / 'operation.lock').open('w') as lock:
        if args.action in ('build', 'up', 'start', 'stop'):
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        hubs, learners = selected(config, inventory())
        print('Project: ' + config['name'], flush=True)
        if args.action == 'build':
            subprocess.run(COMPOSE + ['build', 'singleuser-image', 'jupyterhub'], check=True)
        elif args.action in ('up', 'start'):
            for network in config['networks'].values():
                if network.get('external'):
                    subprocess.run(['docker', 'network', 'inspect', network['name']], check=True, stdout=subprocess.DEVNULL)
            command = ['up', '-d', '--no-build', '--pull', 'never'] if args.action == 'up' else ['start']
            subprocess.run(COMPOSE + command + services, check=True)
            wait_healthy(config)
        elif args.action == 'stop':
            active = [i['Id'] for i in learners if i['State']['Running']]
            if active:
                subprocess.run(['docker', 'stop', '--time', '30', *active], check=True)
            subprocess.run(COMPOSE + ['stop', '--timeout', '30'] + list(reversed(services)), check=True)
            print('Stopped; saved volumes retained')
        elif args.action == 'status':
            for item in hubs + learners:
                print(item['Name'].lstrip('/'), item['State']['Status'], item['State'].get('Health', {}).get('Status', ''))
            if not hubs:
                print('Not created yet; use up after build')
        elif args.action == 'logs':
            subprocess.run(COMPOSE + ['logs', '--tail', str(args.tail)] + services, check=True)
        else:
            print('PASS: explicit local Compose configuration')


if __name__ == '__main__':
    main()
