import random
from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseModel, validator

from hyfi.hydra import Composer
from hyfi.utils.logging import getLogger

logger = getLogger(__name__)


class BatchConfig(BaseModel):
    config_name: str = "__init__"
    batch_name: str
    batch_num: int = -1
    batch_root: str = "outputs"
    output_suffix: str = ""
    output_extention: str = ""
    random_seed: bool = True
    seed: int = -1
    resume_run: bool = False
    resume_latest: bool = False
    device: str = "cpu"
    num_devices: int = 1
    num_workers: int = 1
    config_yaml = "config.yaml"
    config_json = "config.json"
    config_dirname = "configs"
    verbose: Union[bool, int] = False

    def __init__(
        self,
        config_name: str = "__init__",
        config_group: str = "batch",
        **data: Any,
    ):
        """
        Initialize the config. This is the base implementation of __init__.
        You can override this in your own subclass if you want to customize the initilization of a config by passing a keyword argument ` data `.

        Args:
                config_name: The name of the config to initialize
                data: The data to initialize
        """
        super().__init__(**data)
        self.initialize_configs(
            config_name=config_name,
            config_group=config_group,
            **data,
        )

    def initialize_configs(
        self,
        config_name: str = "__init__",
        config_group: str = "batch",
        **data,
    ):
        # Initialize the config with the given config_name.
        data = Composer(
            config_group=f"{config_group}={config_name}",
            config_data=data,
        ).config_as_dict
        self.__dict__.update(data)
        self.init_batch_num()

    def init_batch_num(self):
        if self.batch_num is None:
            self.batch_num = -1
        if self.batch_num < 0:
            num_files = len(list(self.config_dir.glob(self.config_filepattern)))
            self.batch_num = num_files - 1 if self.resume_latest else num_files
        if self.verbose:
            logger.info(
                "Init batch - Batch name: %s, Batch num: %s",
                self.batch_name,
                self.batch_num,
            )

    @validator("seed")
    def _validate_seed(cls, v, values):
        if values["random_seed"] or v is None or v < 0:
            random.seed()
            seed = random.randint(0, 2**32 - 1)
            if values.get("verbose"):
                logger.info(f"Setting seed to {seed}")
            return seed
        return v

    @validator("batch_num", pre=True, always=True)
    def _validate_batch_num(cls, v):
        return v or -1

    @validator("output_suffix", pre=True, always=True)
    def _validate_output_suffix(cls, v):
        return v or ""

    @validator("output_extention", pre=True, always=True)
    def _validate_output_extention(cls, v):
        return v.strip(".") if v else ""

    @property
    def root_dir(self):
        return Path(self.batch_root)

    @property
    def batch_dir(self):
        batch_dir = self.root_dir / self.batch_name
        batch_dir.mkdir(parents=True, exist_ok=True)
        return batch_dir

    @property
    def config_dir(self):
        config_dir = self.batch_dir / self.config_dirname
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @property
    def file_prefix(self):
        return f"{self.batch_name}({self.batch_num})"

    @property
    def output_file(self):
        if self.output_suffix:
            return f"{self.file_prefix}_{self.output_suffix}.{self.output_extention}"
        else:
            return f"{self.file_prefix}.{self.output_extention}"

    @property
    def config_filename(self):
        return f"{self.file_prefix}_{self.config_yaml}"

    @property
    def config_jsonfile(self):
        return f"{self.file_prefix}_{self.config_json}"

    @property
    def config_filepattern(self):
        return f"{self.batch_name}(*)_{self.config_yaml}"

    @property
    def config_filepath(self):
        return self.config_dir / self.config_filename

    @property
    def config_jsonpath(self):
        return self.config_dir / self.config_jsonfile
