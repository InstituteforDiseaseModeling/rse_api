import os
import unittest

import pytest


class TestCore(unittest.TestCase):
    def test_worker_cli_list(self):
        from tests.dummy_app.app import application
        runner = application.test_cli_runner()
        result = runner.invoke(args=['workers', 'list'])
        print(result.output)

    @pytest.mark.skipif(not os.environ.get('RUN_TEST_APPS', False))
    def test_worker_cli_start(self):
        from tests.dummy_app.app import application
        runner = application.test_cli_runner()
        result = runner.invoke(args=['workers', 'start'])
        print(result.output)

    @pytest.mark.skipif(not os.environ.get('RUN_TEST_APPS', False))
    def test_worker_cli_start_no_cron(self):
        from tests.dummy_app.app import application
        runner = application.test_cli_runner()
        result = runner.invoke(args=['workers', 'start', '--cron=False'])
        print(result.output)

    @pytest.mark.skipif(not os.environ.get('RUN_TEST_APPS', False))
    def test_worker_cli_cron(self):
        from tests.dummy_app.app import application
        runner = application.test_cli_runner()
        result = runner.invoke(args=['workers', 'cron'])
        print(result.output)
