from typer.testing import CliRunner
from mem_utils.cli import app

runner = CliRunner()

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output

def test_show():
    result = runner.invoke(app, ["show"])
    assert result.exit_code == 0
    assert "Version actuelle" in result.output
