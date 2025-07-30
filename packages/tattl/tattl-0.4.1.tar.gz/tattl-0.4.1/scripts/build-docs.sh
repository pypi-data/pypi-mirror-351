#!/bin/sh
set -eu

LATEST_VERSION="$(git tag -l --sort=version:refname | tail -n 1)"
DOCS_SOURCE="docs"
DOCS_DEST="docs/_build"


printf "Building documentation for all versions of tattl. Latest version detected as %s.\n" "${LATEST_VERSION}"

rm -rf "${DOCS_DEST}"

uv run sphinx-multiversion -D "smv_latest_version=${LATEST_VERSION}" "${DOCS_SOURCE}" "${DOCS_DEST}"

touch "${DOCS_DEST}/.nojekyll"
cp "${DOCS_SOURCE}/index-redirect.html" "${DOCS_DEST}/index.html"
ln -srf "${DOCS_DEST}/${LATEST_VERSION}" "${DOCS_DEST}/latest"
