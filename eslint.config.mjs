import js from "@eslint/js";
import globals from "globals";

export default [
  {
    // The submodules under ergogen/footprints/ are upstream's, and
    // v4/ergogen/ reaches them again through symlinks.
    ignores: [
      "node_modules/**",
      "dist/**",
      "ergogen/footprints/ceoloide/**",
      "ergogen/footprints/infused-kim/**",
      "ergogen/kb_ergogen_helper/**",
      "v4/ergogen/**",
    ],
  },
  js.configs.recommended,
  // The footprints written here rather than vendored. ergogen `require`s each
  // one and calls `body` with a point, so they are CommonJS and their only
  // reader is a build that fails late: a typo surfaces as a missing pad on a
  // board that has already been ordered.
  //
  // No column limit, unlike the Python beside them. Almost every line is KiCad
  // s-expression inside a template literal, and a break there is a newline in
  // the footprint the build emits rather than a wrapped source line.
  {
    files: ["ergogen/footprints/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      globals: {
        ...globals.node,
      },
      sourceType: "commonjs",
    },
  },
];
