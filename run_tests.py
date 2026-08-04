import sys
import os
sys.path.insert(0, os.path.abspath('tests/mcp_adapter'))
import unittest
import test_tool_call_mapping
suite = unittest.TestLoader().loadTestsFromModule(test_tool_call_mapping)
unittest.TextTestRunner().run(suite)
