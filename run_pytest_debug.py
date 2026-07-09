import pytest
import sys
import os

class TracebackDebugger:
    def pytest_runtest_call(self, item):
        print(f"Running test: {item.name}")

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == "call" and report.failed:
            print("\n================== TEST FAILED ==================")
            print(f"Test name: {item.nodeid}")
            print(f"Exception info: {call.excinfo}")
            if call.excinfo:
                tb = call.excinfo.tb
                while tb.tb_next:
                    tb = tb.tb_next
                # print local variables at the frame of failure
                print("\nLocal variables at failure frame:")
                for k, v in tb.tb_frame.f_locals.items():
                    print(f"  {k}: {repr(v)}")
            print("=================================================\n")

# Make sure we import conftest to setup the DB path, etc.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

debugger = TracebackDebugger()
pytest.main(["-v", "-p", "no:warnings", "tests/test_tier1.py::test_bot_centralized_seniority_level_filtering"], plugins=[debugger])
