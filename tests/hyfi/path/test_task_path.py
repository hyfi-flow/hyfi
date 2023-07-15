from hyfi.path.task import TaskPathConfig
from pathlib import Path
from pprint import pprint


def test_path_config():
    config = TaskPathConfig(
        task_root="workspace/tasks",
        task_name="test-task",
    )
    pprint(config.model_dump())
    # Test that the default values are set correctly
    config.task_name = "test-task2"
    print(config.task_dir)
    assert config.workspace_dir == Path("workspace/tasks/test-task2")

    # Test that the log_dir is created
    assert Path(config.log_dir).is_dir()
    print(config.config_jsonpath)
    assert config.config_filepath == Path(
        "workspace/tasks/test-task2/configs/test-task2_config.yaml"
    )


if __name__ == "__main__":
    test_path_config()