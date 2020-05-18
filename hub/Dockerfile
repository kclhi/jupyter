FROM jupyterhub/jupyterhub:1.2
RUN pip install \
    dockerspawner==0.11.1 \
    jupyterhub-ldapauthenticator==1.2.2 \
    mysql-connector==2.2.9
COPY jupyterhub_config.py .
COPY cull_idle_servers.py .
COPY logo.png .
