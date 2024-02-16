FROM nginx:1.23-alpine

ENV BACKEND_PORT=5000
ENV BACKEND_HOST=halexp

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/nginx-conf.template

COPY docker-entrypoint.sh /

RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]
