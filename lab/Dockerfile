FROM jupyter/r-notebook:3b1f4f5e6cc1
USER root
RUN echo '[ ! -z "$TERM" -a -r /etc/motd ] && cat /etc/issue && cat /etc/motd' \
    >> /etc/bash.bashrc \
    ; echo "\
===================================================================\n\
= KCLHI JUPYTERHUB (kclhi.org)                                    =\n\
===================================================================\n\
\n\
Please contact for services (e.g. package installation).\n"\
    > /etc/motd
USER $NB_UID
RUN R -e "install.packages(c('tableone'), repos='https://cloud.r-project.org/')"
