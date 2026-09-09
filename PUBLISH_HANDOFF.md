# Publication and validation provenance

This documentation repository is `JennieXLisa/ssr-redesign`, branch main. It is already published; the prior v2 “not uploaded” status is historical and retained under history/pre-hardening-metadata. Subsequent hardening corrections are committed to this same repository, not only distributed as a ZIP.

The authoritative publication identity is the actual Git commit and tree returned by GitHub. A document cannot contain its own final commit hash without changing that hash; therefore no self-referential “current commit” field is embedded in MANIFEST.json. The manifest covers the content set and explicitly excludes its own bytes and named generated validation outputs.

The Validate design contracts workflow checks the exact pushed commit, runs structural/schema/reference validation, and stores commit.txt, tree.txt, the exact git archive and validator results as its artifact. Successful Git publication and CI checks do not claim harness/controller application tests, live migration or provider execution. Check the actual Actions run status; do not infer success from a file named validation-results.json.

Future publication must preserve unrelated changes, use non-force updates and verify the remote branch after writing. Rebuild manifest and traceability when source documents change, run validators from the full checkout, and report exact failed/unrun gates. The developer starts at CODEX_HANDOFF.md; implementation instructions are already in the repository.
