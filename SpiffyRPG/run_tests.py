#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

loader = unittest.TestLoader()
tests = loader.discover(".")
testRunner = unittest.runner.TextTestRunner()
testRunner.run(tests)
