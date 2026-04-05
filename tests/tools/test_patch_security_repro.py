import pytest
from unittest.mock import MagicMock
from tools.patch_parser import _apply_delete, _apply_move, PatchOperation, OperationType

@pytest.fixture
def mock_file_ops():
    return MagicMock()

def test_apply_delete_denied(mock_file_ops):
    op = PatchOperation(operation=OperationType.DELETE, file_path="/etc/shadow")
    success, error = _apply_delete(op, mock_file_ops)
    assert success is False
    assert "delete denied" in error.lower()
    mock_file_ops.read_file.assert_not_called()

def test_apply_move_source_denied(mock_file_ops):
    op = PatchOperation(operation=OperationType.MOVE, file_path="/etc/shadow", new_path="/tmp/shadow")
    success, error = _apply_move(op, mock_file_ops)
    assert success is False
    assert "move denied" in error.lower()
    assert "source" in error.lower()
    mock_file_ops._exec.assert_not_called()

def test_apply_move_destination_denied(mock_file_ops):
    op = PatchOperation(operation=OperationType.MOVE, file_path="/tmp/safe", new_path="/etc/shadow")
    success, error = _apply_move(op, mock_file_ops)
    assert success is False
    assert "move denied" in error.lower()
    assert "destination" in error.lower()
    mock_file_ops._exec.assert_not_called()
