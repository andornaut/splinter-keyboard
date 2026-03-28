FROM node:20-alpine
WORKDIR /app
RUN apk add --no-cache bash git && \
    git clone --depth 1 https://github.com/ergogen/ergogen-gui.git . && \
    yarn install
ENV HOST=0.0.0.0
ENV ERGOGEN_PORT=80
EXPOSE ${ERGOGEN_PORT}
CMD ["yarn", "start"]
