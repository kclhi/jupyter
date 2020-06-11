FROM jupyter/datascience-notebook:76402a27fd13
MAINTAINER kclhi
USER $NB_UID
# Additional Python packages (covid analysis).
RUN conda install --quiet --yes \
    'numpy=1.18.*' \
    'matplotlib=3.2.*' \
    'scikit-learn=0.23.*' \
    'lifelines=0.24.*' \
    'tableone=0.7.*' \
    'graphviz=2.42.*' \
    'scipy=1.4.*' \
    'xgboost=1.0.*' \
    # Repeat above lines for additional Python packages.
    # Unavailable:
    # 'pyplot=1.5.*' \
    && \
    conda clean --all -f -y && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER
# Additional R packages (covid analysis).
# Through Conda
RUN conda install --quiet --yes \
    'r-gdata=2.18.*' \
    'r-openxlsx=4.1.*' \
    'r-ggfortify=0.4.*' \
    'r-gridextra=2.3' \
    'r-glue=1.4.1' \
    'r-ggalluvial=0.11.*' \
    'r-ggthemes=4.2.*' \
    'r-ggsci=2.9' \
    'r-coin=1.3*' \
    'r-sandwich=2.5*' \
    'r-ranger=0.12.*' \
    'r-partykit=1.2*' \
    'r-rgenoud=5.8_3.*' \
    'r-matching=4.9*' \
    'r-survminer=0.4.*' \
    'r-ggpubr=0.3.*' \
    'r-rms=6.0*' \
    'r-hmisc=4.4*' \
    'r-glmnet=2.0*' \
    'r-cmprsk=2.2*' \
    'r-pec=2019.11.03' \
    'r-survivalroc=1.0.*' \
    'r-randomforestsrc=2.9.*' \
    # Repeat above lines for additional R packages (conda install).
    # Listed, but unavailable:
    # 'r-matchit=3.0.2' \
    # 'r-optmatch=0.9_10' \
    && \
    conda clean --all -f -y && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER
# Native install
ENV CRAN https://cloud.r-project.org/
ENV R_QUIET TRUE
RUN R --quiet -e "install.packages(c('tableone', 'twang', 'rgenoud', 'optmatch'), repos='$CRAN', quiet=$R_QUIET)"
# Repeat above lines for additonal R packages (native install).
# Not available for current image R version (3.6.3):
# RUN R --quiet -e "install.packages(c('hrm', 'matchit'), repos='$CRAN', quiet=$R_QUIET)"
# Java is a dependency, skip for now:
# RUN R --quiet -e "install.packages(c('xlsx'), repos='$CRAN', quiet=$R_QUIET)"
# Provenance data grabs
COPY jupyter_notebook_config_hook.py /etc/jupyter/
RUN cat /etc/jupyter/jupyter_notebook_config_hook.py >> /etc/jupyter/jupyter_notebook_config.py
# Standalone notebook cell run data grab: COPY custom.js /opt/conda/lib/python3.7/site-packages/notebook/static/custom/
USER root
RUN echo 'echo "kclhi JupyterHub (kclhi.org). Please contact for services (e.g. package installation)."' >> ~/.bashrc
COPY plugin /etc/jupyter/plugin
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN jupyter labextension install /etc/jupyter/plugin --no-build && \
    jupyter lab build && \
    jupyter lab clean && \
    jlpm cache clean && \
    npm cache clean --force && \
    rm -rf $HOME/.node-gyp && \
    rm -rf $HOME/.local && \
    fix-permissions $CONDA_DIR $HOME
USER $NB_UID
