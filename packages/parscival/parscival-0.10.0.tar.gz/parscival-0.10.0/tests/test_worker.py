import pytest

from parscival.worker import main

__author__ = "martinec"
__copyright__ = "CorTexT Platform, Cogniteva SAS"
__license__ = "MIT"

def test_main(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts agains stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    # main(["7"])
    # captured = capsys.readouterr()
    # assert "The 7-th Fibonacci number is 13" in captured.out
