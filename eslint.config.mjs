import js from "@eslint/js";
import globals from "globals";

import { plugins, toolingRules } from "./eslint.config.base.mjs";

export default [
  {
    // The submodules under ergogen/footprints/ are upstream's, and the
    // versioned ergogen directory reaches them again through symlinks.
    ignores: [
      "node_modules/**",
      "dist/**",
      "ergogen/footprints/ceoloide/**",
      "ergogen/footprints/infused-kim/**",
      "ergogen/kb_ergogen_helper/**",
      "v*/ergogen/**",
    ],
  },
  js.configs.recommended,
  // The footprints written here rather than vendored. ergogen `require`s each
  // one and calls `body` with a point, so they are CommonJS and their only
  // reader is a build that fails late: a typo surfaces as a missing pad on a
  // board that has already been ordered.
  //
  // toolingRules rather than sourceRules, and max-len off on top: a footprint is
  // one KiCad s-expression inside a template literal, so a wrapped line is a
  // newline in the emitted footprint, and its keys are pad and parameter order,
  // which is the board's order rather than the alphabet's.
  {
    files: ["ergogen/footprints/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      globals: {
        ...globals.node,
      },
      sourceType: "commonjs",
    },
    plugins,
    rules: {
      ...toolingRules,
      "max-len": "off",
    },
  },
];
