-- Stage 1 relational contract. Apply to a disposable PostgreSQL 17 database in W02.
-- This is a new-install schema, not a migration from the archived harness.
BEGIN;
CREATE TABLE projects (
 project_id uuid PRIMARY KEY, label text NOT NULL, storage_key text NOT NULL UNIQUE,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE snapshots (
 snapshot_id uuid PRIMARY KEY, project_id uuid NOT NULL REFERENCES projects,
 state text NOT NULL CHECK (state IN ('CAPTURING','FINALIZING','READY','FAILED')),
 generation bigint NOT NULL DEFAULT 1 CHECK (generation > 0),
 source_kind text NOT NULL CHECK (source_kind IN ('local','https')),
 source_locator text NOT NULL, requested_revision text, upstream_commit text,
 managed_commit text, tree_oid text, manifest jsonb NOT NULL DEFAULT '{}',
 manifest_digest text, created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 ready_at timestamptz,
 CHECK (state <> 'READY' OR (managed_commit IS NOT NULL AND tree_oid IS NOT NULL AND manifest_digest IS NOT NULL AND ready_at IS NOT NULL)),
 UNIQUE (project_id, snapshot_id)
);
CREATE TABLE files (
 file_id uuid PRIMARY KEY, snapshot_id uuid NOT NULL REFERENCES snapshots,
 path_bytes bytea NOT NULL, path_digest text NOT NULL, path_display text NOT NULL,
 path_prefix bytea NOT NULL, entry_type text NOT NULL CHECK (entry_type IN ('file','symlink')),
 git_mode integer NOT NULL CHECK (git_mode IN (33188,33261,40960)),
 blob_oid text NOT NULL, content_digest text NOT NULL,
 size_bytes bigint NOT NULL CHECK (size_bytes >= 0), encoding text,
 language text CHECK (language IN ('python','javascript','jsx','typescript','tsx','php','c','cpp','java','lua','bash','zsh')),
 classification_basis text NOT NULL, is_binary boolean NOT NULL,
 line_starts bigint[] NOT NULL DEFAULT '{}', bom_bytes smallint NOT NULL DEFAULT 0 CHECK (bom_bytes BETWEEN 0 AND 4),
 link_target bytea,
 UNIQUE(snapshot_id,path_digest), UNIQUE(snapshot_id,file_id),
 CHECK (octet_length(path_prefix) <= 512),
 CHECK ((entry_type='symlink') = (link_target IS NOT NULL))
);
CREATE INDEX files_order_prefix ON files(snapshot_id,path_prefix);
CREATE TABLE exclusions (
 exclusion_id uuid PRIMARY KEY, snapshot_id uuid NOT NULL REFERENCES snapshots,
 path_display text NOT NULL, reason text NOT NULL,
 provenance jsonb NOT NULL DEFAULT '{}'
);
CREATE INDEX exclusions_snapshot ON exclusions(snapshot_id,exclusion_id);
CREATE TABLE rule_manifests (
 manifest_id uuid PRIMARY KEY, digest text NOT NULL UNIQUE,
 mode text NOT NULL CHECK(mode IN ('combined','custom_only')),
 rules jsonb NOT NULL, sources jsonb NOT NULL, tool_profile jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 CHECK(jsonb_typeof(rules)='array'), CHECK(jsonb_typeof(sources)='array')
);
CREATE TABLE datasets (
 dataset_id uuid PRIMARY KEY, snapshot_id uuid NOT NULL REFERENCES snapshots,
 kind text NOT NULL CHECK(kind IN ('extraction','resolution','flagging')),
 fingerprint text NOT NULL, profile jsonb NOT NULL,
 input_extraction_id uuid,
 rule_manifest_id uuid REFERENCES rule_manifests,
 state text NOT NULL CHECK(state IN ('PLANNED','RUNNING','PAUSED','FAILED','SUCCEEDED')),
 plan_state text NOT NULL DEFAULT 'UNFROZEN' CHECK(plan_state IN ('UNFROZEN','FROZEN')),
 plan_digest text, plan_file_count bigint CHECK(plan_file_count>=0),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(), finished_at timestamptz,
 UNIQUE(snapshot_id,kind,fingerprint), UNIQUE(snapshot_id,dataset_id),
 UNIQUE(snapshot_id,dataset_id,input_extraction_id),
 FOREIGN KEY(snapshot_id,input_extraction_id) REFERENCES datasets(snapshot_id,dataset_id),
 CHECK ((kind='extraction') = (input_extraction_id IS NULL)),
 CHECK ((kind='flagging') = (rule_manifest_id IS NOT NULL)),
 CHECK ((plan_state='FROZEN' AND plan_digest IS NOT NULL AND plan_file_count IS NOT NULL)
     OR (plan_state='UNFROZEN' AND plan_digest IS NULL AND plan_file_count IS NULL)),
 CHECK (state <> 'SUCCEEDED' OR plan_state='FROZEN')
);
CREATE TABLE index_runs (
 index_run_id uuid PRIMARY KEY, snapshot_id uuid NOT NULL REFERENCES snapshots,
 extraction_id uuid NOT NULL, resolution_id uuid NOT NULL, flagging_id uuid NOT NULL,
 state text NOT NULL CHECK(state IN ('PLANNED','RUNNING','PAUSED','FAILED','SUCCEEDED')),
 control_intent text NOT NULL DEFAULT 'HOLD' CHECK(control_intent IN ('HOLD','RUN','PAUSE')),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(), finished_at timestamptz,
 FOREIGN KEY(snapshot_id,extraction_id) REFERENCES datasets(snapshot_id,dataset_id),
 FOREIGN KEY(snapshot_id,resolution_id) REFERENCES datasets(snapshot_id,dataset_id),
 FOREIGN KEY(snapshot_id,flagging_id) REFERENCES datasets(snapshot_id,dataset_id)
);
CREATE TABLE work_units (
 work_id uuid PRIMARY KEY, snapshot_id uuid NOT NULL,
 dataset_id uuid NOT NULL, file_id uuid NOT NULL,
 component text NOT NULL CHECK(component IN ('extract','resolve','name_flags','semgrep_flags','text_metadata')),
 state text NOT NULL CHECK(state IN ('PENDING','RUNNING','FAILED','SUCCEEDED')),
 generation bigint NOT NULL DEFAULT 0 CHECK(generation>=0),
 attempt_count integer NOT NULL DEFAULT 0 CHECK(attempt_count>=0),
 retry_cycle_attempt_count integer NOT NULL DEFAULT 0 CHECK(retry_cycle_attempt_count>=0),
 lease_token uuid, lease_expires_at timestamptz, next_attempt_at timestamptz,
 active_publication_id uuid, last_diagnostic_id uuid,
 UNIQUE(dataset_id,file_id,component),
 FOREIGN KEY(snapshot_id,dataset_id) REFERENCES datasets(snapshot_id,dataset_id),
 FOREIGN KEY(snapshot_id,file_id) REFERENCES files(snapshot_id,file_id),
 CHECK ((state='RUNNING' AND lease_token IS NOT NULL AND lease_expires_at IS NOT NULL) OR (state<>'RUNNING' AND lease_token IS NULL AND lease_expires_at IS NULL)),
 CHECK ((state='SUCCEEDED') = (active_publication_id IS NOT NULL))
);
CREATE INDEX work_claim ON work_units(dataset_id,component,state,next_attempt_at,file_id);
CREATE TABLE publications (
 publication_id uuid PRIMARY KEY, work_id uuid NOT NULL REFERENCES work_units,
 generation bigint NOT NULL, committed boolean NOT NULL DEFAULT false,
 result_count bigint CHECK(result_count>=0), result_digest text,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(), committed_at timestamptz,
 UNIQUE(work_id,generation),
 CHECK (NOT committed OR (result_count IS NOT NULL AND result_digest IS NOT NULL AND committed_at IS NOT NULL))
);
ALTER TABLE work_units ADD CONSTRAINT work_active_publication
 FOREIGN KEY(active_publication_id) REFERENCES publications DEFERRABLE INITIALLY DEFERRED;
CREATE VIEW visible_publications AS
 SELECT p.* FROM publications p JOIN work_units w ON w.active_publication_id=p.publication_id
 WHERE p.committed AND w.state='SUCCEEDED' AND w.work_id=p.work_id;
-- Capture-time file encoding/classification fields above are intake hints only.
-- Authoritative per-profile classification and positions are versioned with extraction.
CREATE TABLE file_metadata (
 publication_id uuid NOT NULL REFERENCES publications,
 file_id uuid NOT NULL REFERENCES files,
 encoding text, language text, classification_basis text NOT NULL,
 is_binary boolean NOT NULL, line_starts bigint[] NOT NULL DEFAULT '{}',
 bom_bytes smallint NOT NULL DEFAULT 0 CHECK(bom_bytes BETWEEN 0 AND 4),
 PRIMARY KEY(publication_id,file_id)
);
-- Frozen per-dataset census, including files with no applicable work.
-- Extraction text_metadata jobs bootstrap before this plan can be frozen.
CREATE TABLE dataset_plan_files (
 dataset_id uuid NOT NULL, snapshot_id uuid NOT NULL, file_id uuid NOT NULL,
 metadata_publication_id uuid NOT NULL,
 components text[] NOT NULL,
 treatment text NOT NULL CHECK(treatment IN ('source','text','binary','symlink','lfs_pointer')),
 reason text NOT NULL,
 PRIMARY KEY(dataset_id,file_id),
 FOREIGN KEY(snapshot_id,dataset_id) REFERENCES datasets(snapshot_id,dataset_id),
 FOREIGN KEY(snapshot_id,file_id) REFERENCES files(snapshot_id,file_id),
 FOREIGN KEY(metadata_publication_id,file_id) REFERENCES file_metadata(publication_id,file_id),
 CHECK(components <@ ARRAY['text_metadata','extract','resolve','name_flags','semgrep_flags']::text[])
);
CREATE TABLE scopes (
 publication_id uuid NOT NULL REFERENCES publications, scope_id uuid NOT NULL,
 file_id uuid NOT NULL REFERENCES files, parent_scope_id uuid, owner_symbol_id uuid,
 kind text NOT NULL CHECK(kind IN ('module','callable','type','block','comprehension','namespace')),
 start_byte bigint NOT NULL CHECK(start_byte>=0), end_byte bigint NOT NULL,
 PRIMARY KEY(publication_id,scope_id), CHECK(end_byte>=start_byte),
 FOREIGN KEY(publication_id,parent_scope_id) REFERENCES scopes(publication_id,scope_id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE symbols (
 publication_id uuid NOT NULL REFERENCES publications, symbol_id uuid NOT NULL,
 file_id uuid NOT NULL REFERENCES files, local_name text, qualified_name text NOT NULL,
 kind text NOT NULL CHECK(kind IN ('FUNCTION','METHOD','CONSTRUCTOR','DESTRUCTOR','LAMBDA','CLASS','INTERFACE','TYPE','MODULE','VARIABLE')),
 language text NOT NULL, owner_symbol_id uuid, owner_scope_id uuid NOT NULL, signature text,
 return_type jsonb NOT NULL,
 properties jsonb NOT NULL, provenance jsonb NOT NULL,
 PRIMARY KEY(publication_id,symbol_id),
 FOREIGN KEY(publication_id,owner_scope_id) REFERENCES scopes(publication_id,scope_id) DEFERRABLE INITIALLY DEFERRED
);
ALTER TABLE scopes ADD CONSTRAINT scope_owner
 FOREIGN KEY(publication_id,owner_symbol_id) REFERENCES symbols(publication_id,symbol_id) DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX symbols_name ON symbols(publication_id,md5(local_name));
CREATE TABLE occurrences (
 publication_id uuid NOT NULL REFERENCES publications, occurrence_id uuid NOT NULL,
 symbol_id uuid NOT NULL, file_id uuid NOT NULL REFERENCES files,
 role text NOT NULL CHECK(role IN ('definition','declaration')),
 start_byte bigint NOT NULL CHECK(start_byte>=0), end_byte bigint NOT NULL,
 start_line bigint NOT NULL CHECK(start_line>=1), end_line bigint NOT NULL,
 body_range jsonb, signature_range jsonb, name_range jsonb, parameters jsonb NOT NULL DEFAULT '[]',
 PRIMARY KEY(publication_id,occurrence_id),
 UNIQUE(publication_id,occurrence_id,symbol_id,file_id),
 FOREIGN KEY(publication_id,symbol_id) REFERENCES symbols(publication_id,symbol_id),
 CHECK(end_byte>=start_byte), CHECK(end_line>=start_line),
 CHECK(role <> 'declaration' OR body_range IS NULL)
);
CREATE INDEX occurrence_positions ON occurrences(publication_id,file_id,start_byte,occurrence_id);
CREATE TABLE reference_occurrences (
 publication_id uuid NOT NULL REFERENCES publications, reference_id uuid NOT NULL,
 file_id uuid NOT NULL REFERENCES files, owner_symbol_id uuid, scope_id uuid NOT NULL,
 usage text NOT NULL CHECK(usage IN ('CALL','CONSTRUCT','IMPORT','CALLBACK_ARGUMENT','SYMBOL_USE','SOURCE')),
 start_byte bigint NOT NULL CHECK(start_byte>=0), end_byte bigint NOT NULL,
 callee_range jsonb, receiver_range jsonb, spelling text NOT NULL, provenance jsonb NOT NULL,
 PRIMARY KEY(publication_id,reference_id), CHECK(end_byte>=start_byte),
 UNIQUE(publication_id,reference_id,file_id),
 FOREIGN KEY(publication_id,scope_id) REFERENCES scopes(publication_id,scope_id),
 FOREIGN KEY(publication_id,owner_symbol_id) REFERENCES symbols(publication_id,symbol_id)
);
CREATE INDEX reference_owner ON reference_occurrences(publication_id,owner_symbol_id,start_byte,reference_id);
CREATE TABLE imports (
 publication_id uuid NOT NULL, import_id uuid NOT NULL, reference_id uuid NOT NULL,
 scope_id uuid NOT NULL, kind text NOT NULL CHECK(kind IN ('import','export','require','include','source','dynamic')),
 module text, imported_name text, local_name text, exported_name text,
 relative_level bigint NOT NULL CHECK(relative_level>=0),
 start_byte bigint NOT NULL CHECK(start_byte>=0), end_byte bigint NOT NULL CHECK(end_byte>=start_byte),
 PRIMARY KEY(publication_id,import_id),
 FOREIGN KEY(publication_id,reference_id) REFERENCES reference_occurrences(publication_id,reference_id),
 FOREIGN KEY(publication_id,scope_id) REFERENCES scopes(publication_id,scope_id)
);
CREATE TABLE declarations (
 publication_id uuid NOT NULL, declaration_id uuid NOT NULL, scope_id uuid NOT NULL,
 name text NOT NULL, kind text NOT NULL CHECK(kind IN ('symbol','parameter','import','assignment','delete','global','nonlocal')),
 symbol_id uuid, import_id uuid,
 start_byte bigint NOT NULL CHECK(start_byte>=0), end_byte bigint NOT NULL CHECK(end_byte>=start_byte),
 visible_from bigint NOT NULL CHECK(visible_from>=0),
 visibility text NOT NULL CHECK(visibility IN ('whole_scope','after_declaration','tdz','dynamic')),
 namespace text NOT NULL CHECK(namespace IN ('value','type')),
 PRIMARY KEY(publication_id,declaration_id),
 FOREIGN KEY(publication_id,scope_id) REFERENCES scopes(publication_id,scope_id),
 FOREIGN KEY(publication_id,symbol_id) REFERENCES symbols(publication_id,symbol_id),
 FOREIGN KEY(publication_id,import_id) REFERENCES imports(publication_id,import_id)
);
CREATE INDEX declaration_lookup ON declarations(publication_id,scope_id,md5(name),visible_from);
CREATE TABLE arguments (
 publication_id uuid NOT NULL, reference_id uuid NOT NULL, ordinal integer NOT NULL CHECK(ordinal>=0),
 keyword text, spread boolean NOT NULL,
 start_byte bigint NOT NULL CHECK(start_byte>=0), end_byte bigint NOT NULL,
 PRIMARY KEY(publication_id,reference_id,ordinal),
 FOREIGN KEY(publication_id,reference_id) REFERENCES reference_occurrences(publication_id,reference_id),
 CHECK(end_byte>=start_byte)
);
CREATE TABLE bindings (
 publication_id uuid NOT NULL REFERENCES publications, binding_id uuid NOT NULL,
 reference_id uuid NOT NULL, extraction_id uuid NOT NULL REFERENCES datasets,
 outcome text NOT NULL CHECK(outcome IN ('RESOLVED','AMBIGUOUS','UNRESOLVED')),
 basis text NOT NULL, external_name text, provenance jsonb NOT NULL,
 PRIMARY KEY(publication_id,binding_id), UNIQUE(publication_id,reference_id)
);
CREATE INDEX binding_reference ON bindings(reference_id,outcome);
CREATE TABLE binding_targets (
 publication_id uuid NOT NULL, binding_id uuid NOT NULL, target_symbol_id uuid NOT NULL,
 PRIMARY KEY(publication_id,binding_id,target_symbol_id),
 FOREIGN KEY(publication_id,binding_id) REFERENCES bindings(publication_id,binding_id)
);
CREATE INDEX incoming_targets ON binding_targets(target_symbol_id,binding_id);
CREATE TABLE symbol_associations (
 publication_id uuid NOT NULL REFERENCES publications,
 left_symbol_id uuid NOT NULL, right_symbol_id uuid NOT NULL,
 extraction_id uuid NOT NULL REFERENCES datasets, basis text NOT NULL, evidence jsonb NOT NULL,
 PRIMARY KEY(publication_id,left_symbol_id,right_symbol_id), CHECK(left_symbol_id < right_symbol_id)
);
CREATE TABLE flags (
 publication_id uuid NOT NULL REFERENCES publications, flag_id uuid NOT NULL,
 file_id uuid NOT NULL REFERENCES files, owner_symbol_id uuid,
 start_byte bigint NOT NULL CHECK(start_byte>=0), end_byte bigint NOT NULL,
 category text NOT NULL CHECK(category ~ '^[a-z][a-z0-9_]{0,63}$'),
 signal_kind text NOT NULL CHECK(signal_kind IN ('INTERESTING_NAME','CODE_PATTERN')),
 engine text NOT NULL CHECK(engine IN ('name','semgrep')), rule_id text NOT NULL,
 manifest_id uuid NOT NULL REFERENCES rule_manifests, reason text NOT NULL, provenance jsonb NOT NULL,
 PRIMARY KEY(publication_id,flag_id), CHECK(end_byte>=start_byte)
);
CREATE INDEX flags_browse ON flags(publication_id,category,file_id,start_byte,flag_id);
CREATE TABLE flag_related_owners (
 publication_id uuid NOT NULL, flag_id uuid NOT NULL, symbol_id uuid NOT NULL,
 PRIMARY KEY(publication_id,flag_id,symbol_id),
 FOREIGN KEY(publication_id,flag_id) REFERENCES flags(publication_id,flag_id)
);
CREATE TABLE diagnostics (
 diagnostic_id uuid PRIMARY KEY, snapshot_id uuid REFERENCES snapshots, dataset_id uuid REFERENCES datasets,
 work_id uuid REFERENCES work_units, file_id uuid REFERENCES files,
 publication_id uuid REFERENCES publications,
 component text NOT NULL, code text NOT NULL, detail jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 CHECK(publication_id IS NULL OR (work_id IS NOT NULL AND dataset_id IS NOT NULL AND file_id IS NOT NULL))
);
CREATE INDEX diagnostic_dataset ON diagnostics(dataset_id,created_at,diagnostic_id);
CREATE INDEX diagnostic_publication ON diagnostics(publication_id,diagnostic_id) WHERE publication_id IS NOT NULL;
ALTER TABLE work_units ADD CONSTRAINT work_last_diagnostic FOREIGN KEY(last_diagnostic_id) REFERENCES diagnostics;

-- W09 compiler work belongs to resolution, but is not a file/component work unit.
-- Every resolution dataset has one plan, including an explicit zero-context plan.
-- input_digest is computed BEFORE resolution identity; reference_digest is a later
-- output prerequisite and MUST NOT feed extraction/resolution fingerprints.
CREATE TABLE compiler_context_plans (
 resolution_id uuid PRIMARY KEY, snapshot_id uuid NOT NULL, extraction_id uuid NOT NULL,
 profile_digest text NOT NULL, input_digest text NOT NULL,
 input_state text NOT NULL CHECK(input_state IN ('UNFROZEN','FROZEN')),
 context_count bigint NOT NULL CHECK(context_count>=0),
 reference_state text NOT NULL DEFAULT 'UNFROZEN' CHECK(reference_state IN ('UNFROZEN','FROZEN')),
 reference_count bigint CHECK(reference_count>=0), reference_digest text,
 expectation_rule text NOT NULL DEFAULT 'ALL_CPP_REFERENCES_X_CONTEXTS_V1'
   CHECK(expectation_rule='ALL_CPP_REFERENCES_X_CONTEXTS_V1'),
 UNIQUE(resolution_id,snapshot_id),
 FOREIGN KEY(snapshot_id,resolution_id,extraction_id)
   REFERENCES datasets(snapshot_id,dataset_id,input_extraction_id),
 CHECK((reference_state='FROZEN' AND reference_count IS NOT NULL AND reference_digest IS NOT NULL AND input_state='FROZEN')
    OR (reference_state='UNFROZEN' AND reference_count IS NULL AND reference_digest IS NULL))
);
CREATE TABLE compiler_contexts (
 context_id uuid PRIMARY KEY, resolution_id uuid NOT NULL, snapshot_id uuid NOT NULL,
 ordinal bigint NOT NULL CHECK(ordinal>=0),
 origin text NOT NULL CHECK(origin IN ('compilation_database','conservative')),
 entry_digest text NOT NULL, translation_unit_file_id uuid,
 effective_digest text, effective jsonb, rejection_code text,
 UNIQUE(resolution_id,ordinal), UNIQUE(resolution_id,context_id),
 FOREIGN KEY(resolution_id,snapshot_id) REFERENCES compiler_context_plans(resolution_id,snapshot_id),
 FOREIGN KEY(snapshot_id,translation_unit_file_id) REFERENCES files(snapshot_id,file_id),
 CHECK((rejection_code IS NULL AND translation_unit_file_id IS NOT NULL
        AND effective_digest IS NOT NULL AND effective IS NOT NULL AND jsonb_typeof(effective)='object')
    OR (rejection_code IS NOT NULL AND effective_digest IS NULL AND effective IS NULL))
);
CREATE TABLE compiler_reference_inventory (
 resolution_id uuid NOT NULL REFERENCES compiler_context_plans,
 reference_id uuid NOT NULL, extraction_publication_id uuid NOT NULL, file_id uuid NOT NULL,
 usage text NOT NULL CHECK(usage IN ('CALL','CONSTRUCT','IMPORT','CALLBACK_ARGUMENT','SYMBOL_USE','SOURCE')),
 start_byte bigint NOT NULL CHECK(start_byte>=0), end_byte bigint NOT NULL CHECK(end_byte>=start_byte),
 bytes_digest text NOT NULL,
 PRIMARY KEY(resolution_id,reference_id),
 FOREIGN KEY(extraction_publication_id,reference_id,file_id)
   REFERENCES reference_occurrences(publication_id,reference_id,file_id)
);
CREATE INDEX compiler_reference_file ON compiler_reference_inventory(resolution_id,file_id,reference_id);
CREATE TABLE compiler_context_work (
 work_id uuid PRIMARY KEY, resolution_id uuid NOT NULL, context_id uuid NOT NULL UNIQUE,
 state text NOT NULL CHECK(state IN ('PENDING','RUNNING','FAILED','SUCCEEDED')),
 generation bigint NOT NULL DEFAULT 0 CHECK(generation>=0),
 attempt_count bigint NOT NULL DEFAULT 0 CHECK(attempt_count>=0),
 retry_cycle_attempt_count bigint NOT NULL DEFAULT 0 CHECK(retry_cycle_attempt_count>=0 AND retry_cycle_attempt_count<=attempt_count),
 lease_token uuid, lease_expires_at timestamptz, next_attempt_at timestamptz,
 active_publication_id uuid, last_diagnostic_id uuid,
 UNIQUE(work_id,resolution_id,context_id),
 FOREIGN KEY(resolution_id,context_id) REFERENCES compiler_contexts(resolution_id,context_id),
 CHECK((state='RUNNING' AND generation>0 AND lease_token IS NOT NULL AND lease_expires_at IS NOT NULL)
    OR (state<>'RUNNING' AND lease_token IS NULL AND lease_expires_at IS NULL)),
 CHECK((state='SUCCEEDED')=(active_publication_id IS NOT NULL))
);
CREATE INDEX compiler_work_claim ON compiler_context_work(resolution_id,state,next_attempt_at,context_id);
CREATE TABLE compiler_publications (
 publication_id uuid PRIMARY KEY, work_id uuid NOT NULL,
 resolution_id uuid NOT NULL, context_id uuid NOT NULL,
 generation bigint NOT NULL CHECK(generation>0), committed boolean NOT NULL DEFAULT false,
 result_count bigint CHECK(result_count>=1), result_digest text,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(), committed_at timestamptz,
 UNIQUE(work_id,generation), UNIQUE(work_id,publication_id), UNIQUE(publication_id,resolution_id),
 FOREIGN KEY(work_id,resolution_id,context_id) REFERENCES compiler_context_work(work_id,resolution_id,context_id),
 CHECK(NOT committed OR (result_count IS NOT NULL AND result_digest IS NOT NULL AND committed_at IS NOT NULL))
);
ALTER TABLE compiler_context_work ADD CONSTRAINT compiler_active_publication
 FOREIGN KEY(work_id,active_publication_id) REFERENCES compiler_publications(work_id,publication_id)
 DEFERRABLE INITIALLY DEFERRED;
CREATE VIEW visible_compiler_publications AS
 SELECT p.* FROM compiler_publications p
 JOIN compiler_context_work w ON w.work_id=p.work_id AND w.active_publication_id=p.publication_id
 WHERE p.committed AND w.state='SUCCEEDED' AND p.generation=w.generation
   AND p.context_id=w.context_id AND p.resolution_id=w.resolution_id;

-- detail is the exact named compiler_records model JSON. Scalar key/detail
-- equality, valid/invalid output shape, exact source proof and selected active
-- extraction membership are publication-owner guards, not JSON CHECK claims.
CREATE TABLE compiler_context_results (
 publication_id uuid PRIMARY KEY REFERENCES compiler_publications,
 status text NOT NULL CHECK(status IN ('VALID','INVALID')),
 file_census_complete boolean NOT NULL, detail jsonb NOT NULL CHECK(jsonb_typeof(detail)='object'),
 CHECK((status='VALID')=file_census_complete)
);
CREATE TABLE compiler_file_visits (
 publication_id uuid NOT NULL REFERENCES compiler_publications, file_id uuid NOT NULL REFERENCES files,
 detail jsonb NOT NULL CHECK(jsonb_typeof(detail)='object'),
 PRIMARY KEY(publication_id,file_id)
);
CREATE TABLE compiler_entities (
 publication_id uuid NOT NULL REFERENCES compiler_publications, entity_id uuid NOT NULL,
 extraction_publication_id uuid NOT NULL, occurrence_id uuid NOT NULL,
 symbol_id uuid NOT NULL, file_id uuid NOT NULL, usr text NOT NULL CHECK(usr<>''),
 detail jsonb NOT NULL CHECK(jsonb_typeof(detail)='object'),
 PRIMARY KEY(publication_id,entity_id),
 FOREIGN KEY(extraction_publication_id,occurrence_id,symbol_id,file_id)
   REFERENCES occurrences(publication_id,occurrence_id,symbol_id,file_id),
 FOREIGN KEY(publication_id,file_id) REFERENCES compiler_file_visits(publication_id,file_id)
);
CREATE INDEX compiler_entity_usr ON compiler_entities(publication_id,md5(usr));
CREATE TABLE compiler_observations (
 publication_id uuid NOT NULL, resolution_id uuid NOT NULL, observation_id uuid NOT NULL,
 reference_id uuid NOT NULL, file_id uuid NOT NULL, target_entity_id uuid,
 detail jsonb NOT NULL CHECK(jsonb_typeof(detail)='object'),
 PRIMARY KEY(publication_id,observation_id), UNIQUE(publication_id,reference_id),
 FOREIGN KEY(publication_id,resolution_id) REFERENCES compiler_publications(publication_id,resolution_id),
 FOREIGN KEY(resolution_id,reference_id) REFERENCES compiler_reference_inventory(resolution_id,reference_id),
 FOREIGN KEY(publication_id,file_id) REFERENCES compiler_file_visits(publication_id,file_id),
 FOREIGN KEY(publication_id,target_entity_id) REFERENCES compiler_entities(publication_id,entity_id)
);
CREATE INDEX compiler_observation_reference ON compiler_observations(resolution_id,reference_id,publication_id);
CREATE TABLE compiler_output_diagnostics (
 publication_id uuid NOT NULL REFERENCES compiler_publications,
 diagnostic_key text NOT NULL, code text NOT NULL,
 detail jsonb NOT NULL CHECK(jsonb_typeof(detail)='object'),
 PRIMARY KEY(publication_id,diagnostic_key)
);
CREATE TABLE compiler_attempt_diagnostics (
 diagnostic_id uuid PRIMARY KEY, work_id uuid NOT NULL REFERENCES compiler_context_work,
 generation bigint NOT NULL CHECK(generation>0), code text NOT NULL,
 detail jsonb NOT NULL CHECK(jsonb_typeof(detail)='object'),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(), UNIQUE(work_id,diagnostic_id)
);
CREATE INDEX compiler_attempt_work ON compiler_attempt_diagnostics(work_id,generation,diagnostic_id);
ALTER TABLE compiler_context_work ADD CONSTRAINT compiler_last_diagnostic
 FOREIGN KEY(work_id,last_diagnostic_id) REFERENCES compiler_attempt_diagnostics(work_id,diagnostic_id);
COMMIT;
-- Publication owner MUST additionally validate cross-publication target identity,
-- file bounds, input dataset kinds, outcome/target cardinality and output manifests.
-- The task recipes require real PostgreSQL tests for those transaction guards.
