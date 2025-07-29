from unittest.mock import patch, MagicMock

from pystruction.commands import add_dependencies, uv_run


@patch("pystruction.commands.subprocess.run")
def test_add_dependencies_base_single(mock_run: MagicMock) -> None:
    add_dependencies(["test"])
    mock_run.assert_called_with(["uv", "add", "test"], check=False)
    mock_run.assert_called_once()


@patch("pystruction.commands.subprocess.run")
def test_add_dependencies_base_multiple(mock_run: MagicMock) -> None:
    add_dependencies(["test", "test2"])
    mock_run.assert_called_with(["uv", "add", "test", "test2"], check=False)
    mock_run.assert_called_once()


@patch("pystruction.commands.subprocess.run")
def test_add_dependencies_group_single(mock_run: MagicMock) -> None:
    add_dependencies(["test"], "dev")
    mock_run.assert_called_with(["uv", "add", "--group", "dev", "test"], check=False)
    mock_run.assert_called_once()


@patch("pystruction.commands.subprocess.run")
def test_add_dependencies_group_multiple(mock_run: MagicMock) -> None:
    add_dependencies(["test", "test2"], "dev")
    mock_run.assert_called_with(
        ["uv", "add", "--group", "dev", "test", "test2"], check=False
    )
    mock_run.assert_called_once()


@patch("pystruction.commands.subprocess.run")
def test_uv_run_single(mock_run: MagicMock) -> None:
    uv_run("test")
    mock_run.assert_called_with(["uv", "run", "test"], check=False)
    mock_run.assert_called_once()


@patch("pystruction.commands.subprocess.run")
def test_uv_run_multiple(mock_run: MagicMock) -> None:
    uv_run("test", "check")
    mock_run.assert_called_with(["uv", "run", "test", "check"], check=False)
    mock_run.assert_called_once()
