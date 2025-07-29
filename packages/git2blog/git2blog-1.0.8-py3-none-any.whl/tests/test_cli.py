import os
import sys
import subprocess
import tempfile
import shutil
import pytest
from pathlib import Path

GIT2BLOG_SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'git2blog.py')


def run_cli(args, input_data=None, env=None):
    """Uruchamia CLI git2blog.py z podanymi argumentami i opcjonalnym wejściem"""
    cmd = [sys.executable, GIT2BLOG_SCRIPT] + args
    result = subprocess.run(
        cmd,
        input=input_data,
        text=True,
        capture_output=True,
        env=env or os.environ.copy()
    )
    return result


def test_help():
    result = run_cli(['--help'])
    assert result.returncode == 0
    assert 'git2blog' in result.stdout
    assert '--init' in result.stdout
    assert '--menu' in result.stdout


def test_init_creates_config(tmp_path):
    os.chdir(tmp_path)
    result = run_cli(['--init'])
    assert result.returncode == 0
    assert os.path.exists('git2blog.yaml')
    with open('git2blog.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'blog_title' in content


def test_menu_creates_config(tmp_path):
    os.chdir(tmp_path)
    # Przygotuj odpowiedzi na input() jako stdin (każda odpowiedź w nowej linii)
    answers = '\n'.join([
        'Test Blog',    # Tytuł
        'Opis testowy', # Opis
        'Tester',       # Autor
        'https://github.com/test/proj', # repo_url
        '',             # issues_url
        '',             # pages_url
        'llama3.2',     # model
        '5',            # commit_limit
        '60'            # timeout
    ]) + '\n'
    result = run_cli(['--menu'], input_data=answers)
    assert result.returncode == 0
    assert os.path.exists('git2blog.yaml')
    with open('git2blog.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'Test Blog' in content
        assert 'Tester' in content
        assert 'https://github.com/test/proj' in content


def test_invalid_arg():
    result = run_cli(['--no-such-option'])
    assert result.returncode != 0
    assert 'unrecognized arguments' in result.stderr
