FROM nginx:alpine

COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY index.html /usr/share/nginx/html/index.html

CMD sh -c "envsubst '\$PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && exec nginx -g 'daemon off;'"
