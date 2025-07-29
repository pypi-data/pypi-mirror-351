"""
The pycity_scheduling framework


Copyright (C) 2025,
Institute for Automation of Complex Power Systems (ACS),
E.ON Energy Research Center (E.ON ERC),
RWTH Aachen University

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import numpy as np
import unittest
import os
import importlib.util


class TestExamples(unittest.TestCase):
    pass

def make_example_test(example_filename, example_filepath, test_name):
    def example_test(self):
        try:
            spec = importlib.util.spec_from_file_location(example_filename, example_filepath)
            example_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(example_module)
            example_module.main(do_plot=False)
        except Exception as e:
            self.fail(f'{str(test_name)} failed: {e}')
    return example_test

this_dir = os.path.dirname(__file__)
example_dir = os.path.join(this_dir, "../../examples")
files = os.listdir(example_dir)
for file in sorted(files):
    filepath = os.path.join(example_dir, file)
    example_name, file_ext = os.path.splitext(os.path.split(filepath)[-1])
    if file_ext.lower() == '.py' and example_name != '__init__':
        example_test_name = f'test_{str(example_name)}'
        setattr(TestExamples, example_test_name, make_example_test(example_name, filepath, example_test_name))
