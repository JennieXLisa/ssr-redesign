# Reference schemas and semantic validation

`tool-inputs.schema.json` covers strict structural input variants for the navigation, checkpoint, lead, context, yield and grouped-read tools. `examples/validation-cases.json` supplies positive and negative structural cases. These are specification artifacts, not an installed harness implementation.

Host semantic validation must additionally enforce current execution/review/snapshot access, actual ID/ref resolution, original-byte ranges, unique batch keys, contextual request compatibility, cursor HMAC/policy/matcher digests, zero-length regex behavior, scan/resource budgets, source-free prose, candidate gates and exact role contracts. JSON Schema alone cannot establish those properties. Size in UTF-8 bytes is enforced by the host even when JSON Schema maxLength constrains Unicode characters.

Legacy existing tools and full role-specific result schemas remain in their original owning implementation. Apply ROLE_PROJECTIONS.md to remove only approved mechanical identity fields; preserve every required analytical field. Do not claim this reference schema replaces all existing result contracts or validates analytical truth.
