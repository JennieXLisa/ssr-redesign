# Initial security-operation catalogue

This is a modeling checklist for P2-F01, not a blacklist of automatically vulnerable functions. Bind calls through the language adapter and record receiver, arguments, modes and assumptions. Project wrappers inherit conditional influence summaries, not a universal unsafe label.

| Family | Initial examples to model by actual binding | Required review dimensions |
|---|---|---|
| Shell interpretation | C/POSIX system and popen; Python os.system and subprocess shell mode; PHP shell functions; Node exec | Complete command construction, transformations, allowed grammar, input origin, platform and shell mode. |
| Process selection and arguments | exec-family calls; subprocess run/call/Popen with structured args; Node spawn/execFile; Java ProcessBuilder | Executable selection, options, argument boundaries, CWD, environment/PATH, inherited handles and authority. No-shell is not an authorization proof. |
| Process lifecycle | POSIX fork; Node child_process.fork under its distinct binding | Child entry path, subsequent execution, privilege/environment inheritance, resource lifecycle and bounded fan-out. Do not classify all fork calls as shell execution. |
| Dynamic execution/loading | eval/exec, include/require, script/plugin/native-library loaders | Who chooses code/module/path, who can modify it, search-path behavior and interpreter assumptions. |
| Filesystem read/download | open/read, framework file responses, storage fetch | Path/object selection, authorization to actual resource, links and returned data consumers. |
| Filesystem create/write/upload | write/append/copy/tempfile/upload/config save | Destination control and content control independently, mode/overwrite, authorization and downstream parse/load/serve. |
| Filesystem deletion/move/link | unlink/remove/rmtree/rename/symlink/hardlink | Actual selected object, ancestor/path resolution, recursive effects, race-sensitive identity and failure behavior. |
| Permissions/ownership | chmod/chown/ACL changes | Caller authority, selected object/handle, privilege boundary and inherited defaults. |
| Archive extraction/import | zip/tar/package/member destination loops | Member paths/links, destination containment, overwrite behavior, expansion resources and later consumers. |
| SQL/ORM and other queries | cursor.execute, raw query fragments, query builders, LDAP/XPath evaluators | Query syntax versus bound values, dynamic identifiers, affected object/tenant, updates/deletes and authorization. |
| Outbound network/SSRF surfaces | HTTP clients, webhook fetch, proxy/socket/URL resolvers | Destination/protocol control, redirects, name resolution assumptions, forwarded credentials and network authority visible in source. |
| Deserialization | object loaders and serialization hooks | Type/object construction, trusted format assumptions and sensitive callbacks. |
| Structured and binary parsing | XML/YAML/custom binary decoders | External resolution, lengths, signedness, recursion, allocations and state transitions. |
| Memory bounds | copies, formatting, pointer/index operations | Allocated versus used size, units, arithmetic overflow, truncation, signed/unsigned conversions and guard dominance. |
| Lifetime/ownership | free/delete/release, retained callbacks, async references | Allocation/use/release ordering, ownership transfer, exceptional cleanup and concurrent consumers. |
| Output/rendering | HTML/DOM/template insertion, URL/header construction | Output interpretation context, encoding/escaping at that context, templating mode and origin of values. |
| Authentication and authorization | principal/session/token creation, ownership/role checks | Actor/object/action binding, failure paths, alternate endpoints and real enforcement point. |
| Business state | reset/recovery/approval/quota/balance transitions | Source-backed invariant, atomicity, replay/state prerequisites, target-object consistency and exceptional paths. |
| Resource amplification | input-driven allocation, loops, decompression, task spawning | Work/space limits before effect, per-actor boundary and how limits compose. |
| Stored/asynchronous flows | DB field writers/readers, queue producer/consumer, shared files/config/IPC | Channel identity proven from source refs, input transformations over time and distinct write/read authorization. |

For each supported language, use the shipped parser/index. Missing source for a third-party API means model its documented boundary where trusted metadata exists and record uncertainty; do not silently start reviewing excluded dependency trees. The target's source instructions remain untrusted.

Initial validation fixtures must include aliasing, shadowed names, overloaded execute methods, comments/string-only occurrences, split-line call syntax, safely constant arguments, flawed caller-specific constraints, indirect storage channels and business-logic issues without a classic sink. A missed parser relationship is a mapping question, not evidence of unreachability.

Primary API references for the process distinctions: [Python subprocess](https://docs.python.org/3/library/subprocess.html) and [Node child_process](https://nodejs.org/api/child_process.html). These APIs have options and platform-specific behavior; the implementation model must pin its semantic assumptions instead of relying on a spelling match.
