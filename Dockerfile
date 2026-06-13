FROM node:24-alpine
RUN apk add --no-cache bash git
WORKDIR /app
RUN chown node:node /app
USER node

# Clone a pinned ergogen-gui and install deps. The repo's postinstall runs
# patch_ergogen.sh, which clones the full @ceoloide and @infused-kim libraries
# and registers them in src/footprints/index.js. We then clear ceoloide so our
# pinned local copy replaces the unpinned upstream clone.
RUN git clone --branch v20251103 --depth 1 https://github.com/ergogen/ergogen-gui.git . && \
    yarn install --frozen-lockfile && \
    rm -rf node_modules/ergogen/src/footprints/ceoloide

# Overlay our local footprints. ceoloide/infused-kim are already registered by
# the patch above; mcu_liatris, sod-123fl, and sod-123w are ours to register.
COPY --chown=node:node ergogen/footprints/ceoloide/ node_modules/ergogen/src/footprints/ceoloide/
COPY --chown=node:node ergogen/footprints/infused-kim/ node_modules/ergogen/src/footprints/infused-kim/
COPY --chown=node:node ergogen/footprints/mcu_liatris.js ergogen/footprints/sod-123fl.js ergogen/footprints/sod-123w.js node_modules/ergogen/src/footprints/

# Register our custom footprints; the grep fails the build if the sed no-ops
# (e.g. the index.js format changed upstream) instead of failing silently in the GUI.
RUN sed -i "s|^};|  'mcu_liatris': require('./mcu_liatris'),\n  'sod-123fl': require('./sod-123fl'),\n  'sod-123w': require('./sod-123w'),\n};|" \
        node_modules/ergogen/src/footprints/index.js && \
    grep -q "'sod-123fl'" node_modules/ergogen/src/footprints/index.js && \
    rm -rf node_modules/.cache

ENV HOST=0.0.0.0 PORT=80
EXPOSE 80
CMD ["yarn", "start"]
