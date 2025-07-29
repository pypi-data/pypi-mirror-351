import subprocess
import sys
import os
import pytest

def run_cli(args):
    cmd = [sys.executable, '-m', 'getllm.cli'] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def test_cli_list_runs():
    result = run_cli(['list'])
    assert result.returncode == 0
    assert 'Dostępne modele' in result.stdout

def test_cli_default_runs():
    result = run_cli(['default'])
    assert result.returncode == 0
    assert 'Domyślny model' in result.stdout

def test_cli_help():
    result = run_cli([])
    assert result.returncode == 0
    assert 'usage:' in result.stdout.lower()
