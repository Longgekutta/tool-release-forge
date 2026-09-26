# INTENT EVOLUTION: tool-release-forge

## Initial State
- Tagging and publishing a GitHub Release requires manual changelog copywriting, manual file compression, and manual checksum calculation.

## Transduced Invariants
1. Automated commit extraction and structured categorization (Features, Fixes, Performance, Docs, Refactoring).
2. Direct generation of distributable tar.gz and zip archives.
3. Cryptographic SHA-256 digest creation for tamper-proof binary distribution.
4. Seamless integration with GitHub CLI (`gh release create`).
