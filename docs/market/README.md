# Marketplace listing

DeepSeek Harness has no first-party plugin registry. Plugins are discovered through
the community index [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin),
which is what `dshmarket` (and the Discover tab once its index source is configured)
reads. Listing therefore takes two independent steps; either order works.

## 1. Publish the plugin package on npm (optional, recommended)

```sh
cd plugins/dsh-macos-share
npm login        # once, with the account that owns the package
npm publish --access public
```

- The name is `dsh-macos-share` because `dsh-share` is already taken by an unrelated plugin.
- `repository` in `package.json` must keep pointing at this repository, or npm and the list
  will not be linked (download counts are read from the registry automatically).
- After publishing, `dsh plugin add dsh-macos-share` installs the receiving plugin directly.
  The native share target (`DSHShare.app`) still has to be installed separately.
- Source installs stay supported: `dsh plugin add file:$PWD/plugins/dsh-macos-share`.

## 2. Add the entry to awesome-dsh-plugin

The list is data-driven: every plugin is one YAML file under `data/plugins/`. The READMEs are
generated, so never edit them by hand.

1. Copy `docs/market/awesome-dsh-plugin.yml` to
   `data/plugins/bakkhos8__dsh-macos-share--plugins-dsh-macos-share.yml`.
2. Open a pull request that adds only that file (at most 3 entries per PR).
3. CI checks, in order: entry count, a `dsh.bundle` manifest in the target `package.json`,
   a repository at least one day old, then `awesome-lint` and the site build.
4. A maintainer reads the repository against the description before merging. The description
   above deliberately states the macOS-only requirement and the app dependency; keep it that
   way — an overstated claim is the usual reason an otherwise good plugin is sent back.

Requirements already satisfied by this repository:

- `plugins/dsh-macos-share/package.json` declares `dsh.bundle.patch` plus a `cordis.patch.yml`.
- The subpackage sits under `plugins/`, one of the subpackage locations the CI reads.
- The repository carries the `dsh-plugin` topic (already applied here; add it if you fork).
- `plugins/dsh-macos-share/icon.png` is a 256x256 PNG served from GitHub.

After the merge the list rebuilds `https://awesome-dsh-plugin.com/plugins.json`, which is what
`dshmarket` consumes, so the plugin appears in that market automatically. Users on the built-in
Discover tab add the index source themselves (Settings → Plugins → Discover → index sources):
`https://cdn.jsdelivr.net/npm/dsh-plugin-catalog/index.json`.

## Screenshots (optional)

Screenshots are optional. When `plugins/dsh-macos-share/screenshots.json` exists, storefronts show
App Store style images listed there (1-8 relative paths, resolved from that file). Without it the
market falls back to images found in the plugin README.
