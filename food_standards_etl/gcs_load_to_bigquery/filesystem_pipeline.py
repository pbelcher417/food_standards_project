# flake8: noqa
import os
from typing import Iterator

import dlt
from dlt.sources import TDataItems
from dlt.sources.filesystem import FileItemDict, filesystem, readers, read_parquet

def read_food_standards_parquet() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="standard_filesystem",
        destination='bigquery',
        dataset_name="food_standards",
    )

    file_system_pipe = filesystem() | read_parquet()
    
    # load both folders together to specified tables
    load_info = pipeline.run(file_system_pipe)

    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    read_food_standards_parquet()
