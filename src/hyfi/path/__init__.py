from pathlib import Path
from typing import Any

from pydantic import BaseModel

from hyfi.__global__ import __about__
from hyfi.hydra import _compose
from hyfi.utils.logging import getLogger

logger = getLogger(__name__)


class PathConfig(BaseModel):
    config_name: str = "__init__"
    # internal paths for hyfi
    home: str = ""
    hyfi: str = ""
    resources: str = ""
    runtime: str = ""
    # global paths
    global_hyfi_root: str = ""
    global_workspace_name: str = "workspace"
    global_workspace_root: str = ""
    global_archive: str = ""
    global_datasets: str = ""
    global_models: str = ""
    global_modules: str = ""
    global_library: str = ""
    global_cache: str = ""
    global_tmp: str = ""
    # project specific paths
    project_root: str = ""
    project_workspace_name: str = "workspace"
    project_workspace_root: str = ""
    project_archive: str = ""
    project_datasets: str = ""
    project_models: str = ""
    project_modules: str = ""
    project_outputs: str = ""
    project_logs: str = ""
    project_library: str = ""
    project_cache: str = ""
    project_tmp: str = ""

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    def __init__(
        self,
        config_name: str = "__init__",
        **data: Any,
    ):
        """
        Initialize the config. This is the base implementation of __init__. You can override this in your own subclass if you want to customize the initilization of a config by passing a keyword argument ` data `.

        Args:
                config_name: The name of the config to initialize
                data: The data to initialize
        """
        # Initialize the config module.
        data = _compose(
            f"path={config_name}",
            config_data=data,
            config_module=__about__.config_module,
        )  # type: ignore
        super().__init__(config_name=config_name, **data)

    @property
    def log_dir(self):
        """
        Create and return the path to the log directory. This is a convenience method for use in unit tests that want to ensure that the log directory exists and is accessible to the user.


        Returns:
                absolute path to the log directory for the project ( including parent directories
        """
        Path(self.project_logs).mkdir(parents=True, exist_ok=True)
        return Path(self.project_logs).absolute()

    @property
    def cache_dir(self):
        """
        Create and return the directory where cache files are stored. This is useful for debugging and to ensure that we don't accidentally delete the cache files when there are too many files in the cache.


        Returns:
                absolute path to the cache directory for this test run
        """
        Path(self.global_cache).mkdir(parents=True, exist_ok=True)
        return Path(self.global_cache).absolute()