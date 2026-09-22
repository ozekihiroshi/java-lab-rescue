"""Single-Moodle, registered-user HTTPS pilot; separate from local prototype."""
import os
import re
from urllib.parse import urlsplit
from tornado.web import HTTPError


def required(name):
    value = os.environ.get(name, '').strip()
    if not value or 'REPLACE' in value:
        raise ValueError(f'{name} must be configured')
    return value


def hostname(value):
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', value) or '.' not in value:
        raise ValueError('A DNS hostname without scheme, port or path is required')
    if value == 'localhost' or value.endswith(('.localhost', '.example.org', '.example.com')):
        raise ValueError('Configure the actual public hostname')
    return value


def settings():
    host = hostname(required('JAVA_LAB_HOST'))
    origin = required('MOODLE_ORIGIN')
    parsed = urlsplit(origin)
    if parsed.scheme != 'https' or parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment or parsed.path:
        raise ValueError('MOODLE_ORIGIN must be an HTTPS origin without trailing slash')
    hostname(parsed.hostname or '')
    if parsed.hostname == host:
        raise ValueError('Use a separate hostname for Java Lab')
    image = required('JAVA_SINGLEUSER_IMAGE')
    if not re.fullmatch(r'[^\s]+@sha256:[0-9a-f]{64}', image):
        raise ValueError('JAVA_SINGLEUSER_IMAGE must be pinned by registry digest')
    limit = int(required('JAVA_ACTIVE_SERVER_LIMIT'))
    if limit < 1:
        raise ValueError('JAVA_ACTIVE_SERVER_LIMIT must be positive')
    client = required('LTI_CLIENT_ID')
    deployments = {item.strip() for item in required('LTI_DEPLOYMENT_IDS').split(',') if item.strip()}
    if not deployments:
        raise ValueError('At least one deployment ID is required')
    return host, origin, image, limit, client, deployments


host, origin, image, limit, client, deployments = settings()


async def restrict_deployment(authenticator, handler, authentication):
    claims = authentication.get('auth_state') or {}
    deployment = claims.get('https://purl.imsglobal.org/spec/lti/claim/deployment_id')
    roles = claims.get('https://purl.imsglobal.org/spec/lti/claim/roles', [])
    allowed_roles = {
        'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner',
        'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor',
        'http://purl.imsglobal.org/vocab/lis/v2/membership#TeachingAssistant',
    }
    if deployment not in deployments or not allowed_roles.intersection(roles):
        raise HTTPError(403, 'This Moodle deployment or role is not enabled for Java Lab')
    return authentication


c = get_config()
c.JupyterHub.bind_url = 'http://0.0.0.0:8000'
c.JupyterHub.hub_bind_url = 'http://0.0.0.0:8081'
c.JupyterHub.hub_connect_url = 'http://jupyterhub:8081'
c.JupyterHub.cookie_secret_file = '/srv/jupyterhub/data/cookie_secret'
c.JupyterHub.db_url = 'sqlite:////srv/jupyterhub/data/hub.sqlite'
c.JupyterHub.authenticator_class = 'ltiauthenticator.lti13.auth.LTI13Authenticator'
c.Authenticator.allow_all = True  # Only after signed LTI validation and hook below.
c.Authenticator.post_auth_hook = restrict_deployment
c.LTI13Authenticator.issuer = origin
c.LTI13Authenticator.client_id = [client]
c.LTI13Authenticator.authorize_url = origin + '/mod/lti/auth.php'
c.LTI13Authenticator.jwks_endpoint = origin + '/mod/lti/certs.php'
c.LTI13Authenticator.username_key = 'sub'
c.LTI13Authenticator.uri_scheme = 'https'
c.LTI13Authenticator.tool_name = 'Java Lab'
c.JupyterHub.tornado_settings = {'cookie_options': {'secure': True, 'httponly': True}}
c.JupyterHub.active_server_limit = limit
c.JupyterHub.concurrent_spawn_limit = 1
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = image
c.DockerSpawner.cmd = ['start-singleuser.py']
c.DockerSpawner.name_template = 'java-lab-public-{username}'
c.DockerSpawner.network_name = 'java-lab-public-learners'
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.notebook_dir = '/home/jovyan/work'
c.DockerSpawner.volumes = {'java-lab-public-user-{username}': '/home/jovyan/work'}
c.DockerSpawner.remove = True
c.DockerSpawner.extra_host_config = {
    'cap_drop': ['ALL'], 'security_opt': ['no-new-privileges'], 'pids_limit': 256,
    'log_config': {'type': 'json-file', 'config': {'max-size': '10m', 'max-file': '3'}},
}
c.Spawner.default_url = '/ide/'
c.Spawner.mem_limit = '3G'
c.Spawner.cpu_limit = 1.0
c.Spawner.start_timeout = 180
c.Spawner.http_timeout = 60
c.JupyterHub.shutdown_on_logout = True
