from tempfile import TemporaryDirectory
from pathlib import Path
from uuid import uuid4

import pytest

from ..outputs import OutputsManager


def stream(text: str):
    return {
        "output_type": "stream",
        "name": "stdout",
        "text": text
    }

def display_data_text(text: str):
    return {
        "output_type": "display_data",
        "data": {
            "text/plain": text
        }
}

def test_instantiation():
    op = OutputsManager()
    assert isinstance(op, OutputsManager)

def test_paths():
    """Verify that the paths are working properly."""
    op = OutputsManager()
    file_id = str(uuid4())
    cell_id = str(uuid4())
    with TemporaryDirectory() as td:
        op.outputs_path = Path(td) / "outputs"
        output_index = 0
        assert op._build_path(file_id, cell_id, output_index) == \
            op.outputs_path / file_id / cell_id / f"{output_index}.output"

def test_stream():
    """Test stream outputs."""
    text = "0123456789"
    streams = list([stream(c) for c in text])
    with TemporaryDirectory() as td:
        op = OutputsManager()
        op.outputs_path = Path(td) / "outputs"
        file_id = str(uuid4())
        cell_id = str(uuid4())
        for s in streams:
            op.write_stream(file_id, cell_id, s)
        assert op.get_stream(file_id, cell_id) == text

def test_display_data():
    """Test display data."""
    texts = [
        "Hello World!",
        "Hola Mundo!",
        "Bonjour le monde!"
    ]
    outputs = list([display_data_text(t) for t in texts])
    with TemporaryDirectory() as td:
        op = OutputsManager()
        op.outputs_path = Path(td) / "outputs"
        file_id = str(uuid4())
        cell_id = str(uuid4())
        for (i, output) in enumerate(outputs):
            op.write_output(file_id, cell_id, output)
        for (i, output) in enumerate(outputs):
            assert op.get_output(file_id, cell_id, i) == outputs[i]

def test_clear():
    """Test the clearing of outputs for a file_id."""
    output = display_data_text("Hello World!")
    with TemporaryDirectory() as td:
        op = OutputsManager()
        op.outputs_path = Path(td) / "outputs"
        file_id = str(uuid4())
        cell_id = str(uuid4())
        op.write_output(file_id, cell_id, output)
        path = op._build_path(file_id, cell_id, output_index=0)
        assert path.exists()
        op.clear(file_id)
        assert not path.exists()

def file_not_found():
    """Test to ensure FileNotFoundError is raised."""
    with TemporaryDirectory() as td:
        op = OutputsManager()
        op.outputs_path = Path(td) / "outputs"
        with pytest.raises(FileNotFoundError):
            op.get_output('a','b',0)
        with pytest.raises(FileNotFoundError):
            op.get_stream('a','b')       
