"""Adversarial tests of the public pure compiler-context sanitizer.

Inventories are disposable data, not paths consulted on the developer's host.
These checks do not replace W09's real libclang/sandbox and W12 navigation gates.
"""
import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reference_compiler import CompilerProfile, InvalidContext, Root, sanitize, tokenize_command


def fixture_profile():
    return CompilerProfile(
        snapshot=Root("snapshot", "/work/project", "/managed/snapshot",
            frozenset(("src/main.cpp", "src/main.c", "src/other.cpp", "src/猫.cpp",
                       "src/name space.cpp", "include/test.hpp", "include space/test.hpp",
                       "Frameworks/Kit.framework/Headers/test.h")),
            symlinks=frozenset(("escape", "internal_alias", "cycle_a", "cycle_b"))),
        resources=(Root("sdk", "/installed/sdk", "/managed/sdk",
            frozenset(("include/stddef.h", "cxx/vector", "Frameworks/Kit.framework/Headers/base.h")),
            symlinks=frozenset(("external_link",))),),
        snapshot_id="snapshot-tree-v1", toolchain_id="pinned-clang-and-sdk-v1",
        default_target="x86_64-unknown-linux-gnu",
        allowed_targets=frozenset(("x86_64-unknown-linux-gnu", "aarch64-apple-darwin")),
        system_includes=("/installed/sdk/include",),
    )


def entry(*options, source="src/main.cpp", directory="/work/project", driver="clang++"):
    return {"directory": directory, "file": source,
            "arguments": [driver, *options, source]}


class CompilerProfileTests(unittest.TestCase):
    def setUp(self):
        self.profile = fixture_profile()

    def check_invalid(self, value, expected=None, **kwargs):
        with self.assertRaises(InvalidContext) as caught:
            sanitize(value, self.profile, **kwargs)
        self.assertEqual(caught.exception.basis, "MISSING_BUILD_CONTEXT")
        if expected:
            self.assertEqual(caught.exception.code, expected)
        self.assertFalse(hasattr(caught.exception, "flags"))
        return caught.exception

    def test_minimal_entry_has_exact_source_and_explicit_effective_profile(self):
        result = sanitize(entry(), self.profile)
        self.assertEqual(result.source, "/managed/snapshot/src/main.cpp")
        self.assertEqual(result.source_identity, "snapshot:/src/main.cpp")
        self.assertEqual(result.flags, ("-nostdinc", "-nostdinc++", "-fno-modules",
            "-fno-implicit-modules", "-x", "c++", "-std=c++20",
            "--target=x86_64-unknown-linux-gnu", "-isystem", "/managed/sdk/include"))
        self.assertEqual(result.provenance, ("ARGV0_DISCARDED", "SOURCE_PASSED_SEPARATELY",
            "LANGUAGE_FROM_SUFFIX", "DEFAULT_STANDARD", "DEFAULT_TARGET"))
        self.assertEqual(len(result.fingerprint), 64)

    def test_c_default_is_c17(self):
        result = sanitize(entry(source="src/main.c", driver="clang"), self.profile)
        self.assertEqual(result.flags[4:7], ("-x", "c", "-std=c17"))

    def test_all_path_option_joined_and_separate_forms(self):
        for option in ("-I", "-isystem", "-iquote", "-idirafter", "-F", "-iframework"):
            for path, mapped in (("include", "/managed/snapshot/include"),
                                 ("/installed/sdk/include", "/managed/sdk/include")):
                with self.subTest(option=option, path=path):
                    separate = sanitize(entry(option, path), self.profile)
                    joined = sanitize(entry(option + path), self.profile)
                    self.assertEqual(separate.flags, joined.flags)
                    self.assertEqual(separate.fingerprint, joined.fingerprint)
                    self.assertEqual(separate.flags[8:10], (option, mapped))

    def test_define_undefine_order_spaces_and_literal_option_text_preserved(self):
        result = sanitize(entry("-D", 'TEXT="hello world"', "-UOLD", "-D", "EMPTY=",
            "-DEMPTY", "-U", "EMPTY", "-DTEXT=hello -fplugin=/untrusted/plugin"), self.profile)
        self.assertEqual(result.flags[8:-2], ('-DTEXT="hello world"', "-UOLD", "-DEMPTY=",
            "-DEMPTY", "-UEMPTY", "-DTEXT=hello -fplugin=/untrusted/plugin"))

    def test_language_and_target_forms_are_equivalent(self):
        first = sanitize(entry("-x", "c++", "-target", "aarch64-apple-darwin"), self.profile)
        second = sanitize(entry("-xc++", "--target=aarch64-apple-darwin"), self.profile)
        self.assertEqual(first.flags, second.flags)
        self.assertEqual(first.fingerprint, second.fingerprint)

    def test_explicit_language_allows_captured_header_context(self):
        self.check_invalid(entry(source="include/test.hpp"), "UNSUPPORTED_LANGUAGE")
        result = sanitize(entry("-xc++", source="include/test.hpp"), self.profile)
        self.assertEqual(result.source_identity, "snapshot:/include/test.hpp")

    def test_standards_language_compatibility_and_unlisted_forms(self):
        for language, standard in (("c", "c89"), ("c", "gnu17"), ("c++", "c++98"), ("c++", "gnu++20")):
            with self.subTest(language=language, standard=standard):
                result = sanitize(entry("-x", language, "-std=" + standard), self.profile)
                self.assertIn("-std=" + standard, result.flags)
        for options in (("-xc", "-std=c++20"), ("-std=c17",), ("-std=c++23",),
                        ("-xobjective-c++",), ("-x", "none"), ("--std=c++20",),
                        ("-std", "c++20"), ("--target", "aarch64-apple-darwin")):
            with self.subTest(options=options):
                self.check_invalid(entry(*options))

    def test_singletons_cannot_repeat_even_with_identical_values(self):
        for options in (("-xc++", "-x", "c++"), ("-std=c++20", "-std=c++20"),
                        ("-target", "aarch64-apple-darwin", "--target=aarch64-apple-darwin")):
            with self.subTest(options=options):
                self.check_invalid(entry(*options), "DUPLICATE_OPTION")

    def test_target_must_be_exactly_registered(self):
        for target in ("x86_64", "x86_64-unknown-linux-gnu-malicious", "aarch64-apple-darwin24", "native"):
            with self.subTest(target=target):
                self.check_invalid(entry("--target=" + target), "UNAPPROVED_TARGET")

    def test_arguments_preferred_and_never_unquoted(self):
        value = entry('-DTEXT="hello world"')
        value["command"] = "sh -c 'malicious $(command)'"
        result = sanitize(value, self.profile)
        self.assertIn('-DTEXT="hello world"', result.flags)
        self.assertIn("COMMAND_IGNORED_ARGUMENTS_PREFERRED", result.provenance)
        value["arguments"] = None
        self.check_invalid(value, "INVALID_ARGUMENT_ARRAY")

    def test_output_metadata_is_not_a_write_or_argument(self):
        value = entry()
        value["output"] = "/outside/source/never-created.o"
        result = sanitize(value, self.profile)
        self.assertIn("OUTPUT_METADATA_IGNORED", result.provenance)
        self.assertNotIn(value["output"], result.flags)

    def test_command_quoting_keeps_macro_quotes_and_escaped_spaces(self):
        value = {"directory": "/work/project", "file": "src/main.cpp",
            "command": "clang++ '-DTEXT=\"hello world\"' -Iinclude\\ space src/main.cpp"}
        result = sanitize(value, self.profile)
        expected = sanitize(entry('-DTEXT="hello world"', "-I", "include space"), self.profile)
        self.assertEqual(result.flags, expected.flags)
        self.assertEqual(result.fingerprint, expected.fingerprint)
        self.assertIn("POSIX_COMMAND_TOKENIZED", result.provenance)

    def test_command_tabs_are_separators_but_not_embedded_token_controls(self):
        value = {"directory": "/work/project", "file": "src/main.cpp",
            "command": "clang++\t-DN=1\tsrc/main.cpp"}
        self.assertIn("-DN=1", sanitize(value, self.profile).flags)
        value["command"] = "clang++ '-DN=a\tb' src/main.cpp"
        self.check_invalid(value, "CONTROL_CHARACTER")

    def test_posix_quoted_macro_punctuation_is_literal_data(self):
        value = {"directory": "/work/project", "file": "src/main.cpp",
            "command": "clang++ '-DEXPR=(a;b)' src/main.cpp"}
        self.assertIn("-DEXPR=(a;b)", sanitize(value, self.profile).flags)

    def test_command_shell_syntax_and_substitutions_are_rejected(self):
        attacks = (
            "clang++ src/main.cpp; touch out", "clang++ src/main.cpp && touch out",
            "clang++ src/main.cpp || touch out", "clang++ src/main.cpp | cat",
            "clang++ src/main.cpp &", "clang++ src/main.cpp >out",
            "clang++ src/main.cpp 2>>out", "clang++ src/main.cpp <input",
            "clang++ src/main.cpp <<EOF", "(clang++ src/main.cpp)",
            "clang++ -I<(id) src/main.cpp", "clang++ -I>(id) src/main.cpp",
            "clang++ -DN=$(id) src/main.cpp", 'clang++ "-DN=$(id)" src/main.cpp',
            "clang++ '-DN=$(id)' src/main.cpp", "clang++ -DN=\\$(id) src/main.cpp",
            "clang++ -DN=$((1+2)) src/main.cpp", "clang++ -DN=${HOME} src/main.cpp",
            "clang++ -DN=$HOME src/main.cpp", "clang++ -DN=`id` src/main.cpp",
            "clang++ '-DN=`id`' src/main.cpp", "clang++ *.cpp", "clang++ src/?.cpp",
            "clang++ src/[a].cpp", "clang++ src/{main,other}.cpp",
            "clang++ -I~/include src/main.cpp", "clang++ src/main.cpp # discarded",
            "! clang++ src/main.cpp", "clang++ -DN=(1+2) src/main.cpp",
        )
        for command in attacks:
            with self.subTest(command=command):
                self.check_invalid({"directory": "/work/project", "file": "src/main.cpp",
                                    "command": command}, "SHELL_SYNTAX")

    def test_unmatched_quotes_and_trailing_escape_are_invalid(self):
        for command in ("clang++ 'src/main.cpp", 'clang++ "src/main.cpp', "clang++ src/main.cpp\\"):
            with self.subTest(command=command):
                self.check_invalid({"directory": "/work/project", "file": "src/main.cpp",
                                    "command": command}, "INVALID_COMMAND_QUOTING")

    def test_command_dialects_are_not_guessed(self):
        for platform in ("windows", "cmd", "powershell", "auto"):
            with self.subTest(platform=platform):
                self.check_invalid({"directory": "/work/project", "file": "src/main.cpp",
                    "command": "clang++ src/main.cpp"}, "UNSUPPORTED_COMMAND_PLATFORM",
                    command_platform=platform)

    def test_no_shell_operator_or_response_token_even_in_arrays(self):
        for token in (";", "&", "&&", "|", "||", "<", ">", ">>", "<<", "(", ")", "$(id)", "`id`"):
            with self.subTest(token=token):
                self.check_invalid(entry(token), "SHELL_SYNTAX")
        for options in (("@options.rsp",), ("-I", "@options.rsp"), ("-I@options.rsp",),
                        ("-D", "@options.rsp"), ("-x", "@options.rsp")):
            with self.subTest(options=options):
                self.check_invalid(entry(*options), "RESPONSE_FILE")

    def test_plugins_actions_outputs_forwarding_and_unknown_options_rejected(self):
        options = ("-c", "-S", "-E", "-fsyntax-only", "-o", "-oevil.o", "--output=evil.o",
            "-M", "-MD", "-MMD", "-MF", "-MJout.json", "-save-temps", "--analyze",
            "-Xclang", "-Xclang=-load", "-Xpreprocessor", "-Wp,-include,evil", "-Wl,-plugin,evil",
            "-load", "-fplugin=evil.so", "-fpass-plugin=evil.so", "-B/evil", "--config=evil",
            "-include", "-includeevil.h", "-imacros", "-include-pch", "-fmodules",
            "-fmodule-file=evil.pcm", "-fmodules-cache-path=/tmp/out", "-ivfsoverlay",
            "-vfsoverlay", "-isysroot", "--sysroot=/", "-resource-dir=/evil", "--gcc-toolchain=/evil",
            "-fprofile-instr-generate=/tmp/out", "-serialize-diagnostics", "-O2", "-g", "-Wall",
            "-mavx", "-pthread", "-future-new-option", "--", "-")
        for option in options:
            with self.subTest(option=option):
                self.check_invalid(entry(option), "UNSUPPORTED_OPTION")

    def test_lookalike_joined_forms_do_not_bypass_whitelist(self):
        for option in ("-isystem-after", "-I=include", "-I-", "-D=NAME", "-U=NAME", "-x=c++"):
            with self.subTest(option=option):
                self.check_invalid(entry(option), "INVALID_OPERAND")

    def test_missing_operands_never_consume_another_flag(self):
        for option in ("-I", "-F", "-isystem", "-iquote", "-idirafter", "-iframework", "-D", "-U", "-x", "-target"):
            with self.subTest(option=option):
                self.check_invalid({"directory": "/work/project", "file": "src/main.cpp",
                    "arguments": ["clang++", option]}, "MISSING_OPERAND")
                self.check_invalid(entry(option, "-UNAME"), "MISSING_OPERAND")
        for option in ("-std=", "--target="):
            with self.subTest(option=option):
                self.check_invalid(entry(option, "c++20"), "MISSING_OPERAND")

    def test_invalid_and_function_macro_names(self):
        for option in ("-D9NAME=value", "-DNAME(x)=x", "-DNAME SPACE=value", "-DNAME-=1", "-UNAME=value"):
            with self.subTest(option=option):
                self.check_invalid(entry(option), "INVALID_MACRO")

    def test_source_is_single_final_and_matches_entry_file(self):
        cases = ((["clang++", "src/other.cpp"], "SOURCE_MISMATCH"),
                 (["clang++", "src/main.cpp", "-DN=1"], "SOURCE_NOT_FINAL_OR_MULTIPLE"),
                 (["clang++", "src/main.cpp", "src/other.cpp"], "SOURCE_NOT_FINAL_OR_MULTIPLE"),
                 (["clang++", "-DN=1"], "MISSING_SOURCE"))
        for args, code in cases:
            with self.subTest(args=args):
                value = entry()
                value["arguments"] = args
                self.check_invalid(value, code)

    def test_unapproved_argv0_and_wrappers_cannot_select_an_executable(self):
        for driver in ("/tmp/clang++", "./clang++", "../clang++", "/usr/bin/../bin/clang++",
                       "gcc", "clang-cl", "sh", "bash", "env", "ccache", "xcrun", "CC=clang++",
                       "clang++ --config=evil", "C:\\tools\\clang++.exe"):
            with self.subTest(driver=driver):
                self.check_invalid(entry(driver=driver), "UNAPPROVED_DRIVER")
        result = sanitize(entry(driver="/usr/bin/clang++"), self.profile)
        self.assertNotIn("/usr/bin/clang++", result.flags)

    def test_registered_driver_label_is_metadata_only(self):
        profile = replace(self.profile, drivers=frozenset(("/opt/toolchain/bin/clang++-20",)))
        result = sanitize(entry(driver="/opt/toolchain/bin/clang++-20"), profile)
        self.assertNotIn("/opt/toolchain/bin/clang++-20", result.flags)

    def test_relative_paths_use_recorded_directory_and_allow_internal_parent(self):
        result = sanitize(entry("-I", "../include", source="main.cpp", directory="/work/project/src"), self.profile)
        self.assertEqual(result.source, "/managed/snapshot/src/main.cpp")
        self.assertIn("/managed/snapshot/include", result.flags)
        same = sanitize(entry("-I", "src/../include"), self.profile)
        self.assertEqual(result.fingerprint, same.fingerprint)

    def test_source_aliases_and_unicode_use_snapshot_inventory(self):
        value = entry()
        value["arguments"][-1] = "./src//main.cpp"
        self.assertEqual(sanitize(value, self.profile).source, "/managed/snapshot/src/main.cpp")
        for source in ("src/name space.cpp", "src/猫.cpp"):
            with self.subTest(source=source):
                self.assertEqual(sanitize(entry(source=source), self.profile).source,
                                 "/managed/snapshot/" + source)

    def test_paths_cannot_leave_root_even_when_reentering(self):
        for path in ("../outside", "../project/include", "/work/project/../project/include",
                     "src/../../project/include", "../../installed/sdk/include"):
            with self.subTest(path=path):
                self.check_invalid(entry("-I", path), "PATH_TRAVERSAL")

    def test_whole_components_and_explicit_resource_roots_only(self):
        for path in ("/etc", "/work/project-other/include", "/installed/sdk-other/include",
                     "/managed/snapshot/include", "/usr/include", "/work/./project/include"):
            with self.subTest(path=path):
                self.check_invalid(entry("-I", path), "PATH_OUTSIDE_ROOT")
        self.check_invalid(entry(source="/installed/sdk/include/stddef.h"), "PATH_OUTSIDE_ROOT")
        self.check_invalid(entry(directory="/installed/sdk/include"), "PATH_OUTSIDE_ROOT")

    def test_missing_excluded_wrong_kind_or_file_ancestor_rejected(self):
        for path in ("missing", "missing/../include", "build/generated", "include/missing"):
            with self.subTest(path=path):
                self.check_invalid(entry("-I", path), "PATH_NOT_CAPTURED")
        for path in ("src/main.cpp/../include", "src/main.cpp/../src/main.cpp", "src/main.cpp/."):
            with self.subTest(path=path):
                self.check_invalid(entry("-I", path), "NOT_A_DIRECTORY")
        self.check_invalid(entry("-I", "src/main.cpp"), "PATH_KIND_MISMATCH")
        self.check_invalid(entry(source="include"), "PATH_KIND_MISMATCH")
        self.check_invalid(entry(directory="/work/project/build"), "PATH_NOT_CAPTURED")

    def test_all_symlinks_fail_before_normalization_or_inventory_fallback(self):
        for path in ("escape", "escape/secret", "internal_alias/test.hpp", "internal_alias/../include",
                     "cycle_a", "cycle_b", "/installed/sdk/external_link/secret"):
            with self.subTest(path=path):
                self.check_invalid(entry("-I", path), "SYMLINK_PATH")
        self.check_invalid(entry(source="internal_alias/test.hpp"), "SYMLINK_PATH")
        self.check_invalid(entry(directory="/work/project/internal_alias"), "SYMLINK_PATH")

    def test_windows_and_unc_paths_rejected_on_posix_hosts(self):
        for path in ("C:\\project\\include", "C:/project/include", "\\\\server\\share", "//server/share"):
            with self.subTest(path=path):
                self.check_invalid(entry("-I", path), "NON_POSIX_PATH")

    def test_invalid_entry_types_and_nonabsolute_directory(self):
        for value in (None, [], {"unknown": 1}, {"directory": "/work/project", "file": "src/main.cpp"}):
            with self.subTest(value=value):
                self.check_invalid(value)
        for args in ("clang++ src/main.cpp", (), None, [], ["clang++"], ["clang++", None], ["clang++", 3], ["clang++", ""]):
            with self.subTest(args=args):
                value = entry()
                value["arguments"] = args
                self.check_invalid(value)
        self.check_invalid(entry(directory="."), "DIRECTORY_NOT_ABSOLUTE")

    def test_control_characters_invalid_unicode_and_bounds(self):
        for char in ("\0", "\r", "\n", "\t", "\x1b", "\x7f", "\ud800"):
            with self.subTest(char=repr(char)):
                expected = "INVALID_ENCODING" if char == "\ud800" else "CONTROL_CHARACTER"
                self.check_invalid(entry("-DN=" + char), expected)
        self.check_invalid(entry("-DN=" + "x" * 8192), "INPUT_LIMIT")
        self.check_invalid(entry(*(["-DN=1"] * 1024)), "ARGUMENT_COUNT")
        self.check_invalid(entry(*(["-DN=" + "x" * 8100] * 40)), "INPUT_LIMIT")
        with self.assertRaisesRegex(InvalidContext, "INPUT_LIMIT"):
            tokenize_command("x" * 262145)

    def test_fingerprint_tracks_semantic_changes_but_not_staging_location(self):
        base = sanitize(entry("-DNAME=1"), self.profile)
        moved = replace(self.profile, snapshot=replace(self.profile.snapshot, staged="/temporary/snapshot"),
                        resources=(replace(self.profile.resources[0], staged="/temporary/sdk"),))
        result = sanitize(entry("-DNAME=1"), moved)
        self.assertNotEqual(base.flags, result.flags)
        self.assertEqual(base.fingerprint, result.fingerprint)
        for value, profile in ((entry("-DNAME=2"), self.profile),
                               (entry("-DNAME=1", "-std=c++20"), self.profile),
                               (entry("-DNAME=1"), replace(self.profile, toolchain_id="different-sdk"))):
            with self.subTest(value=value, toolchain=profile.toolchain_id):
                self.assertNotEqual(base.fingerprint, sanitize(value, profile).fingerprint)

    def test_include_and_macro_order_changes_fingerprint(self):
        for first, second in ((("-Iinclude", "-I/installed/sdk/cxx"), ("-I/installed/sdk/cxx", "-Iinclude")),
                              (("-DN=1", "-UN"), ("-UN", "-DN=1"))):
            with self.subTest(first=first):
                self.assertNotEqual(sanitize(entry(*first), self.profile).fingerprint,
                                    sanitize(entry(*second), self.profile).fingerprint)

    def test_profile_inventories_and_results_are_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            self.profile.snapshot.staged = "/untrusted"
        with self.assertRaises(FrozenInstanceError):
            sanitize(entry(), self.profile).flags = ()
        with self.assertRaises(ValueError):
            Root("bad", "/root", "/staged", {"file.c"})
        for original in ("/work/project", "/work/project/include"):
            with self.subTest(original=original), self.assertRaises(ValueError):
                replace(self.profile, resources=(Root("other", original, "/another", frozenset()),))
        with self.assertRaises(ValueError):
            replace(self.profile, system_includes=("/work/project/include",))

    def test_rejection_is_context_limitation_and_does_not_leak_input(self):
        exc = self.check_invalid(entry("-fplugin=/secret/token-DO-NOT-PRINT"), "UNSUPPORTED_OPTION")
        self.assertNotIn("DO-NOT-PRINT", str(exc))
        self.assertNotIn("secret", str(exc))

    def test_malformed_trusted_profile_is_not_an_invalid_source_context(self):
        for root in ("/", "//server/share", "/work/../project", "/work/\0project"):
            with self.subTest(root=root):
                with self.assertRaises(ValueError) as caught:
                    Root("bad", root, "/managed/root", frozenset())
                self.assertNotIsInstance(caught.exception, InvalidContext)
        for files in (frozenset(("",)), frozenset(("../file.c",)), frozenset(("bad\0file.c",))):
            with self.subTest(files=files):
                with self.assertRaises(ValueError) as caught:
                    Root("bad", "/work/root", "/managed/root", files)
                self.assertNotIsInstance(caught.exception, InvalidContext)

    def test_unexpected_exception_is_not_downgraded_to_invalid_context(self):
        value = {"directory": "/work/project", "file": "src/main.cpp", "command": "clang++ src/main.cpp"}
        with patch("reference_compiler.tokenize_command", side_effect=RuntimeError("internal failure")):
            with self.assertRaisesRegex(RuntimeError, "internal failure"):
                sanitize(value, self.profile)

    def test_sanitizer_never_opens_files_launches_processes_or_loads_library(self):
        # Exercise accepted command-only input and an attacker payload through
        # the public entry point while every relevant I/O operation is forbidden.
        value = {"directory": "/work/project", "file": "src/main.cpp",
                 "command": "clang++ -Iinclude '-DTEXT=hello world' src/main.cpp"}
        with patch("builtins.open", side_effect=AssertionError("file I/O")), \
             patch("subprocess.Popen", side_effect=AssertionError("process")), \
             patch("os.system", side_effect=AssertionError("shell")), \
             patch("ctypes.CDLL", side_effect=AssertionError("library")):
            result = sanitize(value, self.profile)
            self.assertIn("-DTEXT=hello world", result.flags)
            self.check_invalid(entry("-fplugin=/untrusted/evil.so"), "UNSUPPORTED_OPTION")


if __name__ == "__main__":
    unittest.main()
