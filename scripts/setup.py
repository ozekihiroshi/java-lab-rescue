#!/usr/bin/env python3
"""Configure local standalone access or import a Moodle LTI connection document."""
import argparse
import json
from pathlib import Path
import re
import secrets
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def validate(document):
    if document.get('schema_version') != 1 or document.get('kind') != 'java':
        raise ValueError('Expected Java Lab connection schema version 1')
    platform, tool = document['platform'], document['tool']
    issuer, base = platform['issuer'], tool['base_url']
    for value in (issuer, base):
        u = urlsplit(value)
        if u.scheme != 'http' or u.hostname not in ('localhost', '127.0.0.1') or u.path or u.query or u.fragment or u.username:
            raise ValueError('This importer is for local HTTP loopback connections; use public configuration for HTTPS')
    if platform['authorize_url'] != issuer+'/mod/lti/auth.php' or platform['jwks_url'] != issuer+'/mod/lti/certs.php':
        raise ValueError('Moodle endpoint mismatch')
    for key, suffix in [('login_url','/hub/lti13/oauth_login'), ('callback_url','/hub/lti13/oauth_callback')]:
        if tool[key] != base+suffix:
            raise ValueError('Tool endpoint mismatch')
    client = platform['client_id']
    if not re.fullmatch(r'[A-Za-z0-9_-]+', client) or not str(platform['deployment_id']).isdigit():
        raise ValueError('Invalid registration identifiers')
    return {'LTI_CLIENT_ID':client, 'MOODLE_ORIGIN':issuer, 'JAVA_LAB_PORT':str(urlsplit(base).port or 80)}


def merge_env(text, updates):
    result=[]
    remaining=dict(updates)
    for line in text.splitlines():
        key, sep, old = line.partition('=')
        if sep and key in updates:
            result.append(key+'='+updates[key]); remaining.pop(key,None)
        else:
            result.append(line)
    result.extend(key+'='+value for key,value in remaining.items())
    return '\n'.join(result)+'\n'


def connect(path):
    document=json.loads(path.read_text())
    updates=validate(document)
    target=ROOT/'.env'
    text=target.read_text() if target.exists() else (ROOT/'.env.example').read_text()
    old=dict(line.split('=',1) for line in text.splitlines() if '=' in line and not line.startswith('#'))
    if target.exists():
        for key in updates:
            value=old.get(key,'')
            if value and 'REPLACE' not in value and value != updates[key]:
                raise ValueError(f'{key} differs from the existing environment. Use a separate checkout/environment; refusing to rebind saved users.')
    runtime=ROOT/'runtime'; runtime.mkdir(exist_ok=True)
    if target.exists() and not (runtime/'env-before-connect').exists():
        (runtime/'env-before-connect').write_text(text); (runtime/'env-before-connect').chmod(0o600)
    target.write_text(merge_env(text,updates)); target.chmod(0o600)
    (runtime/'lti-connection.json').write_text(json.dumps(document,indent=2)+'\n')
    (runtime/'lti-connection.json').chmod(0o600)
    print('Connection imported; storage identities preserved. Run scripts/lab.py check, then up.')
    print('Activity URL: '+document['tool']['target_url'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('standalone')
    link=sub.add_parser('connect'); link.add_argument('connection',type=Path)
    args=parser.parse_args()
    if args.action=='standalone':
        target=ROOT/'.env.standalone'
        if target.exists():
            print('Existing standalone settings retained: '+str(target)); return
        with target.open('x') as handle:
            handle.write('JAVA_STANDALONE_PORT=8088\nJAVA_LOCAL_PASSWORD='+secrets.token_urlsafe(32)+'\n')
        target.chmod(0o600)
        print('Created '+str(target)+'; username: learner. Read the password locally from that file.')
    else:
        connect(args.connection)


if __name__=='__main__':
    main()
