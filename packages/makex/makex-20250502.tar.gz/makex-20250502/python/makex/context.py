import os
import re
import shutil
from copy import copy
from dataclasses import (
    dataclass,
    field,
)
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Callable,
    Pattern,
)

from makex._logging import debug
from makex.colors import (
    ColorsNames,
    NoColors,
)
from makex.configuration import Configuration
from makex.constants import (
    BUILT_IN_REFLINKS,
    DEFAULT_IGNORE_PATTERN,
    MAKEX_FILE_NAMES,
    OUTPUT_DIRECTORY_NAME,
    WORKSPACE_FROM_CONFIGURATION_ENABLED,
)
from makex.errors import (
    CacheError,
    ErrorCategory,
    ErrorLevel,
)
from makex.file_system import (
    safe_reflink,
    same_fs,
    shutil_compatible_copy_file,
    shutil_copy_file,
)
from makex.flags import (
    IMPLICIT_REQUIREMENTS_ENABLED,
    MAKEX_SYNTAX_VERSION,
)
from makex.patterns import combine_patterns
from makex.platform_object import PlatformObject
from makex.ui import UI
from makex.workspace import (
    Workspace,
    WorkspaceCache,
)

if BUILT_IN_REFLINKS:
    import makex.file_cloning as reflink
else:
    import file_cloning

if TYPE_CHECKING:
    from makex.makex_file_parser import TargetGraph
    from makex.target import EvaluatedTaskGraph


def detect_shell():
    enclosing_shell = os.environ.get("SHELL", None)

    # prefer sh shell if it exists
    sh_path = Path("/bin/sh")
    sh_exists = sh_path.exists()

    if sh_exists:
        return sh_path.as_posix()

    # prefer bash shell if it exists
    sh_path = Path("/bin/bash")
    sh_exists = sh_path.exists()

    if sh_exists:
        return sh_path.as_posix()

    # otherwise use enclosing shell
    return enclosing_shell


@dataclass
class Context:
    """
    This primary object is passed throughout the program and its functions.
    
    The Context object retains configuration, settings, state, and globally accessible objects.
    
    This object is initialized once during program initialization.
    
    Field values may be filled or modified as needed.
    """
    # environment variables
    environment: dict[str, str] = field(default_factory=dict)

    # graph is used everywhere so it is attached to context
    # TODO: rename as we need two graphs (graph1 and graph2).
    # TODO: this doesn't really need to be in this Context object
    graph: "TargetGraph" = None

    graph_2: "EvaluatedTaskGraph" = None

    # platform query is used everywhere
    platform: PlatformObject = None

    # used to show messaging
    ui: UI = field(default_factory=UI)

    # The workspace path and detected workspace
    #workspace_path: Path = None

    # The root/initial workspace detected when starting makex.
    workspace_object: Workspace = None

    workspace_cache: WorkspaceCache = field(default_factory=WorkspaceCache)

    # Path to the cache we prefer
    cache: Path = Path("~/.cache/makex/").expanduser()

    # a pattern used to ignore all files from input, output, glob, and find
    ignore_pattern: Pattern = re.compile(DEFAULT_IGNORE_PATTERN)

    # preferred copy file function
    # may be changed to use reflinks on supported systems
    copy_file_function: Callable[[str, str], None] = shutil.copy
    copy_file_function: Callable[[str, str], None] = shutil_copy_file

    # the configuration file
    # TODO: this isn't really used, we expand Configuration into context
    configuration: Configuration = None

    # stack of workspaces as we enter directories that are detected as separate workspaces
    _workspace_stack: list[Workspace] = field(default_factory=list)

    # debug enabled
    # tracing and any expensive debug will use this flag
    debug: bool = False

    # verbosity level
    # 1 is low, 3 is high
    verbose: int = 0

    # Map of color names to strings
    colors: ColorsNames = NoColors

    # True if color enabled.
    # TODO: We probably don't need this.
    color: bool = False

    # TODO: detect the current shell here early if any
    # otherwise use automatic
    shell: str = field(default_factory=detect_shell)

    # names of makex files (Makexfile, makexfile, Build)
    makex_file_names = MAKEX_FILE_NAMES

    # name of the output directory/link (_output_)
    output_folder_name = OUTPUT_DIRECTORY_NAME

    # names of folders/files we should ignore.
    ignore_names = {output_folder_name}

    dry_run: bool = False

    # True if copy on write is enabled on the workspace and cache.
    # this will automatically be detected.
    copy_on_write = False

    # Change the way implicit requirements are handled:
    # If True, implicit requirements will be added when discovered.
    # If False, implicit requirements will be disabled entirely.
    implicit_requirements = IMPLICIT_REQUIREMENTS_ENABLED

    # Change the way errors are handled/reported.
    # Each category may be one of OFF/ERROR/WARNING
    error_levels = {
        ErrorCategory.IMPLICIT_REQUIREMENT_ADDED: ErrorLevel.WARNING,
        ErrorCategory.DUPLICATE_TASK: ErrorLevel.ERROR,
    }

    cpus: int = 1

    makex_syntax_version: int = MAKEX_SYNTAX_VERSION

    files_in_requirements_enabled: bool = False

    include_enabled: bool = False

    @property
    def workspace_path(self):
        if self._workspace_stack:
            return self._workspace_stack[-1].path

        return self.workspace_object.path

    def push_workspace(self, workspace: Workspace):
        self._workspace_stack.append(workspace)

    def pop_workspace(self) -> Workspace:
        return self._workspace_stack.pop()

    def current_workspace(self):
        if self._workspace_stack:
            return self._workspace_stack[-1]

        return self.workspace_object

    def with_configuration(self, configuration: Configuration, early_ui) -> "Context":
        ctx = copy(self)
        ctx.configuration = configuration

        if configuration.ignore:
            ctx.ignore_pattern = combine_patterns(configuration.ignore)

        if WORKSPACE_FROM_CONFIGURATION_ENABLED:
            if configuration.workspace:
                # override WORKSPACE use the workspace defined in the configuration file
                workspace = Path(configuration.workspace).expanduser()
                if not workspace.exists():
                    raise Exception(
                        f"Workspace {configuration.workspace} defined in configuration file at {configuration.path} doesn't exist at {workspace}"
                    )

                ctx.workspace_object = Workspace(workspace)

        cache = ctx.cache

        if configuration.cache:
            # XXX: overwrite ctx.cache here instead of creating a new object
            ctx.cache = cache = Path(configuration.cache).expanduser()
            cache = cache

        if not cache.exists():
            # TODO: create the cache dir here?
            early_ui(f"Creating cache at {cache}")
            try:
                cache.mkdir(parents=True)
            except Exception as e:
                raise CacheError(f"Error creating cache directory at {cache}: {e}")

        # check this after we have a cache and workspace
        if configuration.reflinks is None or configuration.reflinks is True:
            # configuration specified automatic detection of reflinksd
            _same_fs = same_fs(ctx.workspace_path, ctx.cache)
            _reflink_support_workspace = reflink.supported_at(ctx.workspace_path)
            debug("Workspace and Cache are same filesystem: %s", _same_fs)
            debug("Reflink system support: %s", reflink.SUPPORTED)
            debug("Reflink workspace support %s", _reflink_support_workspace)

            if _same_fs and _reflink_support_workspace:
                #ctx.copy_file_function = safe_reflink
                # Use a shutil compatible copy file function
                # TODO: replace this with a faster less-statier one once we drop shutil usage.
                ctx.copy_file_function = shutil_compatible_copy_file
                ctx.copy_on_write = True
        else:
            debug("Using traditional file copy functions.")

        if configuration.file_names:
            # TODO: validate string of
            ctx.makex_file_names = set(configuration.file_names)

        if configuration.output_folder:
            ctx.output_folder_name = configuration.output_folder

        if configuration.include_enabled is not None:
            ctx.include_enabled = configuration.include_enabled

        return ctx

    def new_environment(self, env=None) -> "EnviromentContextManager":
        return EnviromentContextManager(self, env or {})


class EnviromentContextManager:
    def __init__(self, ctx: Context, env: dict = None):
        self.ctx = ctx
        # create a new dict/copy
        self.env = {**ctx.environment, **env}
        self.old_env = self.ctx.environment

    def __enter__(self):
        self.ctx.environment = self.env
        return self.ctx

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ctx.environment = self.old_env
