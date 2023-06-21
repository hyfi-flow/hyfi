from hyfi.main import HyFI
from pathlib import Path


def test_dataframe_load_and_save():
    """Test dataframe loading"""
    _path = HyFI.cached_path(
        "https://assets.entelecheia.ai/datasets/bok_minutes.zip",
        extract_archive=True,
    )
    print(_path)
    data_path = Path(str(_path)) / "bok_minutes" / "bok_minutes-train.parquet"
    df = HyFI.load_data(data_files=data_path)
    assert df is not None
    print(df)
    # assert df.shape == (10, 2)
    HyFI.save_dataframes(df, "tmp/test.parquet")

def test_dataframe_load_and_save2():
    """Test dataframe loading"""
    data_path = "https://assets.entelecheia.ai/datasets/bok_minutes/meta-bok_minutes-train.parquet"
    df = HyFI.load_data(data_files=data_path, use_cached=True, filetype="parquet")
    df = HyFI.load_data(data_files=data_path, use_cached=False)
    assert df is not None
    print(df)
    # assert df.shape == (10, 2)
    HyFI.save_dataframes(df, "tmp/meta-test.parquet")


if __name__ == "__main__":
    test_dataframe_load_and_save2()
