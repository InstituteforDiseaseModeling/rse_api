import os
import unittest

from rse_api.utils import load_modules


class TestUtils(unittest.TestCase):
    def test_load_modules(self):
        path = os.path.join(os.path.dirname( os.path.realpath(__file__)), 'dummy_app')
        controller_path = os.path.join(path, 'controllers')
        modules = load_modules('tests.dummy_app.controllers', controller_path)
        self.assertEquals(modules, ['tests.dummy_app.controllers.dummy_controller', 'tests.dummy_app.controllers.nested.nested_controller'])
