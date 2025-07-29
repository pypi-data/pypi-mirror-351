"""
Dynamic flags.
"""
from os import environ

from makex.constants import (
    SYNTAX_2024,
    SYNTAX_2025,
)

_SENTINEL = object()


def _get_bool(name, default: bool = _SENTINEL, prefix="MAKEX_", environ=environ) -> bool:
    v = environ.get(f"{prefix}{name}", None)
    if v is None:
        if default is not _SENTINEL:
            return default
        return False

    v = v.lower()

    if v in {"true", "1", "on"}:
        return True
    else:
        return False


def _get_string(name, default: str = _SENTINEL, prefix="MAKEX_", environ=environ) -> bool:
    v = environ.get(f"{prefix}{name}", None)
    if v is None:
        if default is not _SENTINEL:
            return default
        return None

    return name


# Enable/disable all features in development, which may not be documented.
DEVELOPMENT_ENABLED = _get_bool("DEVELOPER", False)

# Enable detection of nested Workspaces
NESTED_WORKSPACES_ENABLED = _get_bool("NESTED_WORKSPACES_ENABLED", True)

# Enable the `find() function in makex files. Default to True.
# find() may cause slowdowns in large repositories; we may want to disable find.
FIND_FUNCTION_ENABLED = _get_bool("FIND_FUNCTION_ENABLED", True)

GLOB_FUNCTION_ENABLED = _get_bool("GLOB_FUNCTION_ENABLED", True)

ERASE_FUNCTION_ENABLED = _get_bool("ERASE_FUNCTION_ENABLED", True)

# Enable glob functions in the Target outputs list.
GLOBS_IN_OUTPUTS_ENABLED = _get_bool("GLOBS_IN_OUTPUTS_ENABLED", True)

FIND_IN_INPUTS_ENABLED = _get_bool("FIND_IN_INPUTS_ENABLED", True)

# Enable glob functions in the Target inputs list.
GLOBS_IN_INPUTS_ENABLED = _get_bool("GLOBS_IN_INPUTS_ENABLED", True)

# Enable globs in various arguments to Actions.
GLOBS_IN_ACTIONS_ENABLED = _get_bool("GLOBS_IN_ACTIONS_ENABLED", DEVELOPMENT_ENABLED)

# enable feature for variants of outputs
VARIANTS_ENABLED = _get_bool("VARIANTS_ENABLED", False)

# Enable the expand() function in makex files.
EXPAND_FUNCTION_ENABLED = _get_bool("EXPAND_FUNCTION_ENABLED", False)

# Enable the archive() function in makex files.
ARCHIVE_FUNCTION_ENABLED = _get_bool("ARCHIVE_FUNCTION_ENABLED", True)

# Enable the home() function in makex files.
HOME_FUNCTION_ENABLED = _get_bool("HOME_FUNCTION_ENABLED", True)

# Use `{ line; } || (exit $?)` for each line of shell script.
SHELL_USES_RETURN_CODE_OF_LINE = _get_bool("SHELL_USES_RETURN_CODE_OF_LINE", True)

# If true, absolute paths are enabled throughout the codebase
# Inputs/outputs/Path element can all take absolute paths.
ABSOLUTE_PATHS_ENABLED = _get_bool("ABSOLUTE_PATHS_ENABLED", True)

# Enable/disable the shell() function.
SHELL_FUNCTION_ENABLED = _get_bool("SHELL_FUNCTION_ENABLED", True)

# Enable dictionaries/named outputs.
NAMED_OUTPUTS_ENABLED = True

# Enable embedding various paths in strings.
# This should not be enabled until we carefully work in late string (joined or concatenated) evaluation
# and early arugment processing.
# Enable this in dev mode because we know what we want.
# Disable for public because it can really footgun (cyclical deps).
ENABLE_PATH_TO_STRING = _get_bool("ENABLE_PATH_TO_STRING", DEVELOPMENT_ENABLED)

# Enable setting of target path.
# We will likely set this to False by default.
TARGET_PATH_ENABLED = _get_bool("TARGET_PATH_ENABLED", True)

INCLUDE_ENABLED = _get_bool("INCLUDE_ENABLED", True)

# allow includes to make an `include()` call.
INCLUDE_MULTIPLE_LEVEL_ENABLED = False

IMPORT_ENABLED = _get_bool("IMPORT_ENABLED", False)

# Allow explicitly specifying the configuration file name. This will skip use of
# the builtin file names.
CONFIGURATION_FILE_NAME = _get_string("CONFIGURATION_FILE_NAME", None)

# If True, enable task self references; e.g. self.outputs, self.inputs, self.path, self.name
TASK_SELF_ENABLED = _get_bool("TASK_SELF_ENABLED", True)

# If true, any requirements inside of task's or a task's steps will be added to the task's requirements.
# False so that users are explicit.
IMPLICIT_REQUIREMENTS_ENABLED = _get_bool("IMPLICIT_REQUIREMENTS_ENABLED", False)

# Enable late joined strings. String of the form f"{variable1}text1{variable2}text3" will be decomposed into a
# JoinedString(variable1, "text1", variable2, "text") which can be evaluated later.
LATE_JOINED_STRINGS = _get_bool("LATE_JOINED_STRINGS", True)

# Enable optional task requirements.
OPTIONAL_REQUIREMENTS_ENABLED = _get_bool("OPTIONAL_REQUIREMENTS_ENABLED", True)

# Enable paths in globs as a first argument.
PATH_IN_GLOB_ENABLED = _get_bool("PATH_IN_GLOB_ENABLED", True)

# Enable debugging of scheduling/queueing code. This will emit a lot of log messages while tasks are waiting/executing.
SCHEDULE_DEBUG_ENABLED = _get_bool("SCHEDULE_DEBUG_ENABLED", False)

# Enable reading makex config files from the current working directory or any ancestors.
READ_CONFIG_FROM_PARENTS = _get_bool("READ_CONFIG_FROM_PARENTS", False)

# Set the makex syntax version
# See the breaking changes document for more information
# TODO: SYNTAX_2025: switch this to 2 once we confirm reversing of locators and requires list migration flags.
MAKEX_SYNTAX_VERSION = _get_string("SYNTAX", SYNTAX_2025)

FOLDERS_IN_INPUTS = _get_string("FOLDERS_IN_INPUTS", True)
FOLDERS_IN_OUTPUTS = _get_string("FOLDERS_IN_OUTPUTS", True)

# internal or shutil
COPY_LIBRARY = _get_string("COPY_LIBRARY", "internal")

# Strict mode
# - Disable the shell (unless really explicit)
# - Make sure all used files are declared (or just handle this implicitly)
# - Disable globs/finds
# - Using paths of another target should be prohibited unless it is an internal (copy/sync/write).
#   - Any paths of required targets become a dependency and would break composition.
# - If shell must be enabled, disable __str__ on any TaskPath so they can't be hidden in shell strings.
#   - add concatenate() to explicitly concatenate [shell] strings and any paths they may require.
STRICT_MODE = _get_bool("STRICT_MODE", False)

if STRICT_MODE:
    SHELL_FUNCTION_ENABLED = False
    GLOB_FUNCTION_ENABLED = False
    FIND_FUNCTION_ENABLED = False
    ENABLE_PATH_TO_STRING = False
    IMPLICIT_REQUIREMENTS_ENABLED = False
