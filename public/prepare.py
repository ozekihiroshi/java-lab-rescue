#!/usr/bin/env python3
"""Import an HTTPS Moodle registration without starting or pulling any containers."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
ASSIGNMENT = re.compile(r'^\s*(?:export\s+)?([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$')


def validate(document):
    if not isinstance(document, dict) or document.get('schema_version') != 1 or document.get('kind') != 'java':
        raise ValueError('Expected Java Lab connection schema version 1')
    platform, tool = document['platform'], document['tool']
    issuer, base = platform['issuer'], tool['base_url']
    for origin in (issuer, base):
        u = urlsplit(origin)
        if (u.scheme != 'https' or not u.hostname or u.hostname in ('localhost', '127.0.0.1')
                or u.path or u.query or u.fragment or u.username or u.port is not None
                or not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', u.hostname)):
            raise ValueError('Expected an HTTPS hostname origin on port 443, without path or credentials')
    if urlsplit(issuer).hostname == urlsplit(base).hostname:
        raise ValueError('Moodle and Java Lab require separate hostnames')
    for key, suffix in [('authorize_url', '/mod/lti/auth.php'), ('jwks_url', '/mod/lti/certs.php')]:
        if platform[key] != issuer + suffix:
            raise ValueError('Moodle endpoint mismatch')
    for key, suffix in [('login_url', '/hub/lti13/oauth_login'), ('callback_url', '/hub/lti13/oauth_callback'),
                        ('target_url', '/hub/user-redirect/ide/')]:
        if tool[key] != base + suffix:
            raise ValueError('Java endpoint mismatch')
    client, deployment = platform['client_id'], str(platform['deployment_id'])
    if not isinstance(client, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', client) or not re.fullmatch(r'[1-9][0-9]*', deployment):
        raise ValueError('Invalid registration identifiers')
    return {'JAVA_LAB_HOST': urlsplit(base).hostname, 'MOODLE_ORIGIN': issuer,
            'LTI_CLIENT_ID': client, 'LTI_DEPLOYMENT_IDS': deployment}


def merge(text, updates):
    seen = set(); result = []
    for line in text.splitlines():
        m = ASSIGNMENT.fullmatch(line)
        if m and m[1] in updates:
            key = m[1]
            if key in seen:
                raise ValueError('Duplicate setting: ' + key)
            seen.add(key)
            tokens = shlex.split(m[2], comments=True)
            if len(tokens) > 1:
                raise ValueError('Expected literal setting: ' + key)
            old = tokens[0] if tokens else ''
            if old and old != updates[key] and not old.startswith('REPLACE_') and old not in ('java.example.org', 'https://moodle.example.org'):
                raise ValueError('Refusing to rebind existing environment: ' + key)
            line = key + '=' + updates[key]
        result.append(line)
    result.extend(k + '=' + v for k, v in updates.items() if k not in seen)
    return '\n'.join(result) + '\n'


def write_private(path, text):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as f:
        temporary = Path(f.name)
        f.write(text)
    try:
        temporary.chmod(0o600)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def prepare(connection, target):
    updates = validate(json.loads(connection.read_text(encoding='utf-8')))
    original = target.read_text(encoding='utf-8') if target.exists() else None
    template = (ROOT / '.env.production.example').read_text(encoding='utf-8')
    # A new installation starts with a single-learner pilot setting, not a capacity claim.
    template = template.replace('JAVA_ACTIVE_SERVER_LIMIT=2', 'JAVA_ACTIVE_SERVER_LIMIT=1')
    merged = merge(original if original is not None else template, updates)
    backup = target.with_name(target.name + '.before-connect')
    if original is not None and not backup.exists():
        write_private(backup, original)
    write_private(target, merged)
    print('HTTPS connection prepared. Existing images, capacity and storage settings retained.')
    print('No Docker commands executed. Image digests and host capacity still require verification.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('connection', type=Path)
    parser.add_argument('--env-file', type=Path, default=ROOT / '.env.production')
    args = parser.parse_args()
    try:
        prepare(args.connection, args.env_file)
    except (ValueError, KeyError, TypeError, OSError) as e:
        parser.exit(1, str(e) + '\n')
