FROM httpd:latest
COPY httpd.conf /usr/local/apache2/conf/httpd.conf
COPY sites /usr/local/apache2/conf/sites
COPY htmlfiles /usr/local/apache2/htmlfiles
COPY certs/jupyter.crt /var/www/localhost/ssl/jupyter.crt
COPY certs/jupyter.key /var/www/localhost/ssl/jupyter.key
EXPOSE 80
CMD ["httpd", "-D", "FOREGROUND"]
