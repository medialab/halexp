FROM nginx:1.23-alpine

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/

CMD ["nginx", "-g", "daemon off;"]
