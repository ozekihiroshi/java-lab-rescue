FROM eclipse-temurin:21-jdk-jammy@sha256:c7d5863b5dd8f26b90c64f1d80cc2b0e5a5e4642f8db9955a370d348edd8f438 AS jdk
FROM quay.io/jupyter/minimal-notebook:2026-07-28@sha256:230b7474518c193143d253822fd86fa0a850aa31e18a74952d940782157d373d
USER root
COPY --from=jdk /opt/java/openjdk /opt/java/openjdk
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="/opt/java/openjdk/bin:${PATH}"
RUN apt-get update && apt-get install -y --no-install-recommends maven && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir jupyterhub==5.5.0 jupyter-server-proxy==4.4.0
ARG CODE_SERVER_VERSION=4.137.0
ARG CODE_SERVER_SHA256=9303165b7fd43532091922f77e2f119ff2fa109c6b6f1c3c966fb02f3d6d9c8b
RUN curl -fSL --connect-timeout 20 --max-time 600 --retry 3 --speed-limit 1024 --speed-time 30 "https://github.com/coder/code-server/releases/download/v${CODE_SERVER_VERSION}/code-server-${CODE_SERVER_VERSION}-linux-amd64.tar.gz" -o /tmp/code-server.tgz \
    && echo "${CODE_SERVER_SHA256}  /tmp/code-server.tgz" | sha256sum -c - \
    && mkdir -p /opt/code-server && tar -xzf /tmp/code-server.tgz --strip-components=1 -C /opt/code-server \
    && ln -s /opt/code-server/bin/code-server /usr/local/bin/code-server && rm /tmp/code-server.tgz
COPY singleuser/jupyter_server_config.py /etc/jupyter/jupyter_server_config.py
COPY singleuser/10-java-materials.py /usr/local/bin/java-materials.py
COPY singleuser/10-java-materials.sh /usr/local/bin/start-notebook.d/10-java-materials.sh
COPY materials/ /opt/java-course/materials/
COPY checks/maven-smoke/ /opt/java-course/maven-smoke/
RUN chmod -R a-w /opt/java-course/materials && chmod 0755 /usr/local/bin/start-notebook.d/10-java-materials.sh \
    && chmod 0644 /usr/local/bin/java-materials.py \
    && mkdir -p /opt/java-extensions /opt/maven-cache && chown -R ${NB_UID}:${NB_GID} /opt/java-extensions /opt/maven-cache /opt/java-course/maven-smoke
USER ${NB_UID}
RUN code-server --extensions-dir /opt/java-extensions --install-extension redhat.java@1.56.0
RUN mvn -B -f /opt/java-course/maven-smoke/pom.xml -Dmaven.repo.local=/opt/maven-cache test
WORKDIR /home/jovyan/work
COPY singleuser/maven-settings.xml /opt/java-course/maven-settings.xml
# JDK indexing shares a single CPU with the notebook health probe.
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 CMD /etc/jupyter/docker_healthcheck.py || exit 1
