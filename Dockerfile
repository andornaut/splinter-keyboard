FROM node:24-alpine
RUN apk add --no-cache bash git
WORKDIR /app
RUN chown node:node /app
USER node

# Clone a pinned ergogen-gui and install deps. The repo's postinstall runs
# patch_ergogen.sh, which clones the @ceoloide and @infused-kim footprint
# libraries at HEAD and registers them in src/footprints/index.js. We leave
# that patch flow untouched and only add our own footprints on top.
RUN git clone --branch v20251103 --depth 1 https://github.com/ergogen/ergogen-gui.git . && \
    yarn install --frozen-lockfile

# Add our custom footprints (not part of any upstream library) so the GUI can
# render configs that use them.
COPY --chown=node:node ergogen/footprints/mcu_liatris.js ergogen/footprints/sod-123fl.js ergogen/footprints/sod-123w.js ergogen/footprints/r_0805.js node_modules/ergogen/src/footprints/

# Register our custom footprints; the grep fails the build if the sed no-ops
# (e.g. the index.js format changed upstream) instead of failing silently in the GUI.
RUN sed -i "s|^};|  'mcu_liatris': require('./mcu_liatris'),\n  'sod-123fl': require('./sod-123fl'),\n  'sod-123w': require('./sod-123w'),\n  'r_0805': require('./r_0805'),\n};|" \
        node_modules/ergogen/src/footprints/index.js && \
    grep -q "'r_0805'" node_modules/ergogen/src/footprints/index.js && \
    rm -rf node_modules/.cache

ENV HOST=0.0.0.0 PORT=80
EXPOSE 80
CMD ["yarn", "start"]
