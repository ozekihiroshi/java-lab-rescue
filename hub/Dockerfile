FROM jupyterhub/jupyterhub:5.5.0@sha256:f91ed45a0d2333de2ed9f5d708ad6f18a2fb79547526fbaaa19e88fd44fcab71
RUN python -m pip install --no-cache-dir dockerspawner==14.0.0 jupyterhub-ltiauthenticator==1.6.3
COPY hub/ /srv/jupyterhub/
WORKDIR /srv/jupyterhub
CMD ["jupyterhub", "-f", "jupyterhub_config.py"]
