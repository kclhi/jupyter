FROM jupyter/r-notebook:3b1f4f5e6cc1
USER root
RUN echo 'echo "kclhi JupyterHub (kclhi.org). Please contact for services (e.g. package installation)."' >> ~/.bashrc
USER $NB_UID
RUN R -e "install.packages(c('tableone'), repos='https://cloud.r-project.org/')"
# Repeat above line for additonal R packages. 
