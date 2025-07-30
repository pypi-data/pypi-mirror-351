import pathlib
from fasttextlt.format import load, Model


# TODO: test with and without full model
def test_load_model(model_path: pathlib.Path):
    with open(model_path, "rb") as in_stream:
        m = load(in_stream)
    assert isinstance(m, Model)


def test_save_model(model, tmp_path):
    pass