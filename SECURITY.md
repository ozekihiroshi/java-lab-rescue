# Security and deployment boundary

Local Compose binds only to 127.0.0.1 and uses HTTP for the local Moodle LTI exchange. Do not expose it on the internet. The separate public Compose is an HTTPS configuration candidate for registered, trusted learners; AWS deployment and public acceptance are deferred.

JupyterHub has access to the Docker socket. Learners do not. This is not a hardened sandbox for arbitrary hostile users. Use a dedicated host for public code execution. CPU, memory and process limits do not limit persistent disk usage.

Keep .env, runtime data, Hub cookies/DB, user volumes, credentials and logs out of Git. Preserve all user volumes and the stopped Hub DB when backing up. Do not use down -v for routine shutdown. Logs may contain personal or authentication data; review before sharing.

The source pins major build inputs but some OS/Python dependencies are resolved at build time. Publish and deploy reviewed immutable image digests; keep third-party notices when distributing images. The code-server artifact in this version is linux-amd64.
