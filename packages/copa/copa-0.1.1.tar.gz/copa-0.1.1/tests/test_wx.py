#!/usr/bin/env python3

"""Tests for `copa`"""

import pytest
from click.testing import CliRunner

from copa import copa
from copa import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/engineervix/cookiecutter-pyproject')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'copa.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


class TestWx():
    """Tests the copa module"""

    @staticmethod
    def test_addition():
        """tests for addition"""
        assert copa.add(2, 2) == 4  # nosec

    @staticmethod
    def test_subtraction():
        """tests for subtraction"""
        assert cop.subtract(4, 2) == 2  # nosec
