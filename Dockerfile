FROM node:20-alpine
WORKDIR /app
RUN apk add --no-cache bash git && \
    git clone --depth 1 https://github.com/ergogen/ergogen-gui.git . && \
    yarn install
# Override bundled ceoloide footprints with our local versions to keep them in sync
RUN rm -rf node_modules/ergogen/src/footprints/ceoloide
COPY ergogen/footprints/ceoloide/ node_modules/ergogen/src/footprints/ceoloide/
# Copy custom footprints and register them in ergogen's index
COPY v4/ergogen/footprints/mcu_liatris.js node_modules/ergogen/src/footprints/mcu_liatris.js
RUN sed -i "s|^};|  'mcu_liatris': require('./mcu_liatris'),\n};|" \
    node_modules/ergogen/src/footprints/index.js && \
    rm -rf node_modules/.cache
ENV HOST=0.0.0.0
ENV PORT=80
EXPOSE 80
CMD ["yarn", "start"]
