FROM nginx
RUN mkdir /etc/nginx/ssl
COPY ./certs/jupyter.crt /etc/nginx/ssl/jupyter.crt
COPY ./certs/jupyter.key /etc/nginx/ssl/jupyter.key
COPY nginx.conf /etc/nginx/nginx.conf
COPY ./locations/* /etc/nginx/locations/
CMD ["nginx", "-g", "daemon off;"]
