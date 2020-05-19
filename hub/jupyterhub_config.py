import os, sys

## Generic
c.JupyterHub.base_url = "/jupyter";
c.JupyterHub.trusted_alt_names = ["localhost", "kclhi.org"];

## Authenticator
c.JupyterHub.authenticator_class = "ldapauthenticator.LDAPAuthenticator";
c.LDAPAuthenticator.server_address = "covid-2_openldap_1";
c.LDAPAuthenticator.bind_dn_template = ["uid={username},dc=kclhi,dc=org"];
c.LDAPAuthenticator.use_ssl = True;
c.Authenticator.admin_users = {os.environ.get("ADMIN_USERS")}
c.JupyterHub.admin_access = True;

## Docker spawner
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner";
c.DockerSpawner.image = os.environ["DOCKER_JUPYTER_CONTAINER"];
c.DockerSpawner.network_name = os.environ["DOCKER_NETWORK_NAME"];
# See https://github.com/jupyterhub/dockerspawner/blob/master/examples/oauth/jupyterhub_config.py
c.JupyterHub.hub_ip = os.environ["HUB_IP"];
c.JupyterHub.logo_file = '/srv/jupyterhub/logo.png'

# user data persistence
# see https://github.com/jupyterhub/dockerspawner#data-persistence-and-dockerspawner
notebook_dir = os.environ.get("DOCKER_NOTEBOOK_DIR") or "/home/jovyan";
c.DockerSpawner.notebook_dir = notebook_dir;
c.DockerSpawner.volumes = { "jupyterhub-user-{username}": notebook_dir };

# db
c.JupyterHub.db_url = "mysql+mysqlconnector://{}:{}@{}/{}{}".format(os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD"),"mariadb", os.getenv("MYSQL_DATABASE"), "");

# Spawner
c.Spawner.cpu_limit = 1;
c.Spawner.mem_limit = "10G";
c.Spawner.default_url = "/lab";

# Set the log level by value or name.
c.JupyterHub.log_level = 'DEBUG';

## Services
c.JupyterHub.services = [{'name': 'cull-idle', 'admin': True, 'command': [sys.executable, 'cull_idle_servers.py', '--timeout=3600']}];
