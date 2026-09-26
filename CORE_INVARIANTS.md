# CORE INVARIANTS: tool-release-forge

1. Semantic Integrity Invariance:
   - Commits MUST be categorized strictly according to Conventional Commits standards without loss of breaking change notices.

2. Checksum Cryptographic Invariance:
   - All release assets MUST have SHA-256 hashes generated into a standard `SHA256SUMS` file with format: `<hash>  <filename>`.

3. Hermetic Offline Packaging Invariance:
   - Changelog drafting, compression archiving, and checksum calculation execute 100% offline without remote network dependencies.
