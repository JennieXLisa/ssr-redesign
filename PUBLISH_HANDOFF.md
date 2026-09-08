# Publish this documentation workspace

## Current state

The documentation tree was saved locally. No remote repository was created and no
GitHub commit or push occurred. The ChatGPT GitHub actions available in the saving
session were read-only, and no GitHub CLI was installed in that runtime. This is a
tool-capability limit, not a claim that the user's GitHub account lacks permission.

## Instructions for a developer session with GitHub write access

Confirm the repository owner, name, visibility, and initial branch with the user
before creating it; those values were not specified in the conversation. The local
package label `ssr-collaborative-review-design` is a suggested name, not a confirmed
remote. Recommend private visibility because the documents reference private code.
Do not make it public without explicit approval.

Check for an existing repository with the confirmed identity. If one exists,
report it and inspect its contents; do not overwrite it or silently choose a new
name. Use the user's authenticated tools; never ask for a token pasted into a
prompt or write credentials into the repository.

Publish only this documentation tree to the confirmed separate repository. Include
phase scope placeholders and Phase 1 feature records as supplied. Do not turn
pending sections into invented implementation plans. Do not copy raw implementation
source, live databases, transcripts, generated runtime artifacts, or credentials.

Do not modify `source-review-harness`, `ssr-control`, their specifications,
refactoring handoffs, release pins, or running services. Do not start implementing
features as part of publication.

After publication, verify the remote file tree and report the actual repository
URL, initial branch, commit ID, and visibility. Update the root publication status
only after successful verification. Do not report local files as remotely saved.
