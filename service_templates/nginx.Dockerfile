# NAME=nginx
# DESCRIPTION=nginx web server
# PROXY_PORTS=80

FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY public/ /usr/share/nginx/html/

EXPOSE 80
