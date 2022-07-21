from pathlib import Path


def get_mocked_data(filename: str):
    here = Path(__file__).parent
    file_path = here / 'data' / Path(filename)
    return file_path.read_text()
