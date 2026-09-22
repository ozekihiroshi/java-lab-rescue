"""Local Java Lab. Use the separate public configuration for HTTPS deployment."""
import os

c = get_config()
c.JupyterHub.bind_url = "http://0.0.0.0:8000"
c.JupyterHub.hub_bind_url = "http://0.0.0.0:8081"
c.JupyterHub.hub_connect_url = "http://jupyterhub:8081"
c.JupyterHub.cookie_secret_file = "/srv/jupyterhub/data/cookie_secret"
c.JupyterHub.db_url = "sqlite:////srv/jupyterhub/data/hub.sqlite"
c.JupyterHub.authenticator_class = "ltiauthenticator.lti13.auth.LTI13Authenticator"
c.Authenticator.allow_all = True
c.LTI13Authenticator.issuer = os.environ.get("MOODLE_ORIGIN", "http://localhost:8083")
c.LTI13Authenticator.client_id = [os.environ["LTI_CLIENT_ID"]]
c.LTI13Authenticator.authorize_url = c.LTI13Authenticator.issuer + "/mod/lti/auth.php"
c.LTI13Authenticator.jwks_endpoint = "http://jwks:8000/jwks"
c.LTI13Authenticator.username_key = "sub"
c.LTI13Authenticator.uri_scheme = "http"
c.LTI13Authenticator.tool_name = "Java Lab"
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"
c.DockerSpawner.image = os.environ.get("JAVA_SINGLEUSER_IMAGE", "java-lab-rescue-singleuser:local")
c.DockerSpawner.cmd = ["start-singleuser.py"]
c.DockerSpawner.name_template = os.environ.get("JAVA_CONTAINER_PREFIX", "java-lab-rescue") + "-{username}"
c.DockerSpawner.network_name = os.environ.get("JAVA_LEARNER_NETWORK", "java-lab-rescue-learners")
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.notebook_dir = "/home/jovyan/work"
c.DockerSpawner.volumes = {os.environ.get("JAVA_USER_VOLUME_PREFIX", "java-lab-rescue-user") + "-{username}": "/home/jovyan/work"}
c.DockerSpawner.remove = True
c.DockerSpawner.extra_host_config = {
    "cap_drop": ["ALL"], "security_opt": ["no-new-privileges"], "pids_limit": 256,
}
c.Spawner.default_url = "/ide/"
c.Spawner.mem_limit = "3G"
c.Spawner.cpu_limit = 1.0
c.Spawner.start_timeout = 180
c.Spawner.http_timeout = 60
c.JupyterHub.shutdown_on_logout = False
