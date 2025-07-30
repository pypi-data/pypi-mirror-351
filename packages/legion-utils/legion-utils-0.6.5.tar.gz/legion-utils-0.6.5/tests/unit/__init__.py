from pathlib import Path

from typeguard import typechecked


@typechecked
def file_with(filepath: Path, contents: str) -> Path:
    with filepath.open('w+') as file:
        file.write(contents)
    return filepath
