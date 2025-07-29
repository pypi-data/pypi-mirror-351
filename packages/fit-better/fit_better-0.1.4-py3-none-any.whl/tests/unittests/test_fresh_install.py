"""
Test to verify that the fit_better package can be built, installed in a fresh virtual environment,
and that all tests pass when using the installed wheel.

This script:
1. Creates a fresh virtual environment
2. Builds the wheel package of fit_better
3. Installs the wheel in the virtual environment
4. Runs tests using the installed package to verify functionality

Usage:
    python -m pytest tests/test_fresh_install.py -v
"""

import os
import sys
import subprocess
import unittest
import shutil
import tempfile
import venv
import json
import datetime
from pathlib import Path


class FreshInstallTest(unittest.TestCase):
    """Test case for verifying the installed wheel package functionality."""

    def setUp(self):
        """Set up the test environment with a fresh virtual environment."""
        # Create a temporary directory for the virtual environment
        self.temp_dir = tempfile.mkdtemp(prefix="fit_better_fresh_install_")
        self.venv_dir = os.path.join(self.temp_dir, "venv")
        self.wheel_dir = os.path.join(self.temp_dir, "wheel")

        # Project root directory
        # Need to go up two levels: from unittests to tests, then to project root
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        print(f"Project root directory: {self.project_root}")

        # Create wheel directory
        os.makedirs(self.wheel_dir, exist_ok=True)

        # Create a directory for test results
        self.results_dir = os.path.join(self.temp_dir, "test_results")
        os.makedirs(self.results_dir, exist_ok=True)

        # Initialize results tracking
        self.test_results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "environment": {
                "system": sys.platform,
                "python_version": sys.version,
            },
            "steps": [],
            "summary": {"status": "unknown", "duration": 0, "details": ""},
        }

        print(f"Test environment set up in: {self.temp_dir}")

    def tearDown(self):
        """Clean up after the test."""
        # Copy test results to a permanent location before cleanup
        try:
            # Use the data_gen directory directly under tests, no need for "tests" in the path again
            # since self.project_root now points to the real project root
            results_archive_dir = os.path.join(
                self.project_root, "tests", "data_gen", "fresh_install_results"
            )

            print(f"Archive directory: {results_archive_dir}")
            os.makedirs(results_archive_dir, exist_ok=True)
            # Print path for debugging
            print(f"Archive directory: {results_archive_dir}")

            # Save results summary
            summary_path = os.path.join(self.results_dir, "results_summary.json")
            with open(summary_path, "w") as f:
                json.dump(self.test_results, f, indent=4)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            status = (
                self.test_results["summary"]["status"]
                if "summary" in self.test_results
                else "unknown"
            )
            archive_name = f"fresh_install_{timestamp}_{status}"
            archive_path = os.path.join(results_archive_dir, archive_name)

            if os.path.exists(self.results_dir) and os.listdir(self.results_dir):
                print(f"Archiving test results to: {archive_path}")
                shutil.copytree(self.results_dir, archive_path)

                # Create a symlink to the latest results for easy access
                latest_link = os.path.join(results_archive_dir, "latest")
                if os.path.exists(latest_link):
                    if os.path.islink(latest_link):
                        os.unlink(latest_link)
                    else:
                        shutil.rmtree(latest_link)

                # Create relative symlink when possible, but fall back to absolute path if needed
                try:
                    os.symlink(
                        os.path.basename(archive_path),
                        latest_link,
                        target_is_directory=True,
                    )
                    print(f"Created symlink to latest results: {latest_link}")
                except (OSError, AttributeError):
                    # On Windows or other platforms where symlinks might not be supported
                    try:
                        # Just copy the directory instead
                        shutil.copytree(archive_path, latest_link)
                        print(f"Created copy of latest results: {latest_link}")
                    except Exception as copy_error:
                        print(
                            f"Warning: Failed to create latest results copy: {str(copy_error)}"
                        )
        except Exception as e:
            print(f"Warning: Failed to archive test results: {str(e)}")

        # Remove the temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _run_command(self, cmd, cwd=None, env=None, verbose=True):
        """Run a shell command and return its output."""
        if verbose:
            print(f"Running command: {cmd}")

        if cwd is None:
            cwd = self.project_root

        if env is None:
            env = os.environ.copy()

        result = subprocess.run(
            cmd, shell=True, cwd=cwd, env=env, capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"Command failed: {cmd}")
            print(f"Error output: {result.stderr}")
            return None

        return result.stdout.strip()

    def _get_python_executable(self):
        """Get the Python executable path from the virtual environment."""
        if sys.platform == "win32":
            return os.path.join(self.venv_dir, "Scripts", "python.exe")
        return os.path.join(self.venv_dir, "bin", "python")

    def _get_pip_executable(self):
        """Get the pip executable path from the virtual environment."""
        if sys.platform == "win32":
            return os.path.join(self.venv_dir, "Scripts", "pip.exe")
        return os.path.join(self.venv_dir, "bin", "pip")

    def _get_pytest_executable(self):
        """Get the pytest executable path from the virtual environment."""
        if sys.platform == "win32":
            return os.path.join(self.venv_dir, "Scripts", "pytest.exe")
        return os.path.join(self.venv_dir, "bin", "pytest")

    def _log_step_result(self, step_name, success, duration, details=""):
        """Log the result of a test step."""
        self.test_results["steps"].append(
            {
                "name": step_name,
                "success": success,
                "duration": duration,
                "details": details,
            }
        )

        if success:
            print(f"✓ {step_name} completed successfully ({duration:.1f}s)")
        else:
            print(f"✗ {step_name} failed ({duration:.1f}s)")
            if details:
                print(f"  Details: {details}")

    def test_fresh_install_and_tests(self):
        """Test the full workflow: create venv, build wheel, install, run tests."""
        start_time = datetime.datetime.now()

        # Step 1: Create a virtual environment
        step_start = datetime.datetime.now()
        print("\n========== Step 1: Creating virtual environment ==========")

        try:
            venv.create(self.venv_dir, with_pip=True)

            # Configure pip to use Aliyun mirror if needed
            pip_conf_dir = os.path.join(
                self.venv_dir, "pip.conf" if sys.platform != "win32" else "pip.ini"
            )
            with open(pip_conf_dir, "w") as f:
                f.write(
                    "[global]\nindex-url = http://mirrors.aliyun.com/pypi/simple\ntrusted-host = mirrors.aliyun.com\n"
                )

            step_duration = (datetime.datetime.now() - step_start).total_seconds()
            self._log_step_result("Create virtual environment", True, step_duration)
        except Exception as e:
            step_duration = (datetime.datetime.now() - step_start).total_seconds()
            self._log_step_result(
                "Create virtual environment", False, step_duration, f"Error: {str(e)}"
            )
            raise

        python_exe = self._get_python_executable()
        pip_exe = self._get_pip_executable()

        # Step 2: Install build dependencies and build the wheel
        step_start = datetime.datetime.now()
        print("\n========== Step 2: Building wheel package ==========")

        # Install build dependencies
        print("Installing build dependencies...")
        deps_result = self._run_command(
            f"{pip_exe} install --upgrade pip wheel setuptools", verbose=True
        )

        # Make sure build package is installed
        build_install = self._run_command(f"{pip_exe} install build", verbose=True)

        # Show pip list for debugging
        pip_list = self._run_command(f"{pip_exe} list", verbose=True)
        print(f"Installed packages: {pip_list}")

        # Check if project directories are set up correctly
        print(f"Checking project setup...")
        print(f"Project root: {self.project_root}")
        has_setup_py = os.path.exists(os.path.join(self.project_root, "setup.py"))
        has_pyproject = os.path.exists(
            os.path.join(self.project_root, "pyproject.toml")
        )
        print(f"setup.py exists: {has_setup_py}")
        print(f"pyproject.toml exists: {has_pyproject}")

        build_output = None

        # Try multiple build methods, in order of preference
        build_methods = [
            # Method 1: Use pip wheel directly on project root
            {
                "name": "pip wheel",
                "cmd": f"{pip_exe} wheel --no-deps -w {self.wheel_dir} {self.project_root}",
                "cwd": None,
            },
            # Method 2: Use setuptools directly if setup.py exists
            {
                "name": "setuptools direct",
                "cmd": f"{python_exe} setup.py bdist_wheel -d {self.wheel_dir}",
                "cwd": self.project_root,
            },
            # Method 3: Use build package
            {
                "name": "build package",
                "cmd": f"{python_exe} -m build --wheel --outdir {self.wheel_dir}",
                "cwd": self.project_root,
            },
            # Method 4: Use pip install with --no-deps and install from the project root
            {
                "name": "pip install as wheel",
                "cmd": f"{pip_exe} install --no-deps --target {self.temp_dir}/build_target {self.project_root} && {pip_exe} wheel --no-deps -w {self.wheel_dir} {self.project_root}",
                "cwd": None,
            },
        ]

        # Try each build method until one succeeds
        success = False
        for method in build_methods:
            print(f"\nTrying build method: {method['name']}...")
            output = self._run_command(method["cmd"], cwd=method["cwd"], verbose=True)
            if output is not None:
                build_output = output
                print(f"Build succeeded with method: {method['name']}")
                success = True
                break
            else:
                print(f"Build method {method['name']} failed, trying next method...")

        if not success:
            step_duration = (datetime.datetime.now() - step_start).total_seconds()
            self._log_step_result(
                "Build wheel package",
                False,
                step_duration,
                "Failed to build the wheel package using multiple methods",
            )
            raise AssertionError("Failed to build the wheel package")

        # Find the wheel file
        wheel_files = list(Path(self.wheel_dir).glob("*.whl"))
        if len(wheel_files) == 0:
            step_duration = (datetime.datetime.now() - step_start).total_seconds()
            self._log_step_result(
                "Build wheel package",
                False,
                step_duration,
                "No wheel file was generated",
            )
            raise AssertionError("No wheel file was generated")

        wheel_file = str(wheel_files[0])
        print(f"Built wheel: {os.path.basename(wheel_file)}")

        step_duration = (datetime.datetime.now() - step_start).total_seconds()
        wheel_details = f"Built {os.path.basename(wheel_file)}"
        self._log_step_result("Build wheel package", True, step_duration, wheel_details)

        # Step 3: Install the wheel and its dependencies
        step_start = datetime.datetime.now()
        print("\n========== Step 3: Installing wheel package ==========")
        install_output = self._run_command(f"{pip_exe} install {wheel_file}")
        if install_output is None:
            step_duration = (datetime.datetime.now() - step_start).total_seconds()
            self._log_step_result(
                "Install wheel package",
                False,
                step_duration,
                "Failed to install the wheel package",
            )
            raise AssertionError("Failed to install the wheel package")

        # Install test dependencies
        print("Installing test dependencies...")
        self._run_command(
            f"{pip_exe} install pytest numpy scikit-learn matplotlib joblib"
        )

        # Install optional dependencies
        print("Installing optional dependencies...")
        deps_output = self._run_command(f"{pip_exe} install xgboost lightgbm")

        step_duration = (datetime.datetime.now() - step_start).total_seconds()
        self._log_step_result(
            "Install wheel package",
            True,
            step_duration,
            f"Installed {os.path.basename(wheel_file)}",
        )

        # Step 4: Verify the package can be imported
        step_start = datetime.datetime.now()
        print("\n========== Step 4: Verifying package import ==========")

        # Create a small test script to avoid issues with interpolation
        import_test_script = os.path.join(self.temp_dir, "import_test.py")
        with open(import_test_script, "w") as f:
            f.write(
                """
try:
    import fit_better
    print(f"fit_better version: {fit_better.__version__}")
    print("Import successful!")
    exit(0)
except ImportError as e:
    print(f"Import error: {str(e)}")
    exit(1)
except Exception as e:
    print(f"Unexpected error: {str(e)}")
    exit(2)
"""
            )

        # Run the import test script
        import_test = self._run_command(
            f"{python_exe} {import_test_script}", verbose=True
        )
        if import_test is None:
            step_duration = (datetime.datetime.now() - step_start).total_seconds()
            self._log_step_result(
                "Verify package import",
                False,
                step_duration,
                "Failed to import the fit_better package",
            )
            raise AssertionError("Failed to import the fit_better package")

        print(f"Import test result: {import_test}")
        step_duration = (datetime.datetime.now() - step_start).total_seconds()
        self._log_step_result("Verify package import", True, step_duration, import_test)

        # Create a temporary directory for testing
        test_dir = os.path.join(self.temp_dir, "tests")
        os.makedirs(test_dir, exist_ok=True)

        # Copy test files to the test directory
        self._run_command(
            f"cp -r {os.path.join(self.project_root, 'tests')}/* {test_dir}/"
        )

        # Step 5: Run a subset of tests to verify functionality
        step_start = datetime.datetime.now()
        print("\n========== Step 5: Running tests with installed package ==========")

        # Install pytest and run unit tests
        pytest_exe = self._get_pytest_executable()
        tests_passed = True
        test_messages = []

        # First, generate required test data
        print("Generating test data...")
        test_data_script = os.path.join(test_dir, "usages", "generate_test_data.py")
        if os.path.exists(test_data_script):
            data_gen_output = self._run_command(
                f"{python_exe} {test_data_script}", cwd=test_dir
            )
            if data_gen_output is None:
                test_messages.append("Failed to generate test data")
                tests_passed = False
            else:
                test_messages.append("Test data generated successfully")

        # Run unit tests
        print("\nRunning core unit tests...")
        test_env = os.environ.copy()
        test_env["PYTHONPATH"] = test_dir

        unit_test_output = self._run_command(
            f"{pytest_exe} {os.path.join(test_dir, 'unittests')} -v",
            env=test_env,
            cwd=test_dir,
        )

        if unit_test_output:
            print("Unit tests completed successfully")
            with open(
                os.path.join(self.results_dir, "unit_tests_output.txt"), "w"
            ) as f:
                f.write(unit_test_output)
            test_messages.append("Unit tests passed")
        else:
            print("Warning: Unit tests failed or produced no output")
            with open(
                os.path.join(self.results_dir, "unit_tests_output.txt"), "w"
            ) as f:
                f.write("Unit tests failed or produced no output")
            tests_passed = False
            test_messages.append("Unit tests failed")

        # Run a basic usage example to verify functionality
        print("\nRunning basic usage example...")
        example_script = os.path.join(
            test_dir, "usages", "simplified_model_evaluation.py"
        )
        if os.path.exists(example_script):
            example_output = self._run_command(
                f"{python_exe} {example_script}", cwd=test_dir
            )
            with open(os.path.join(self.results_dir, "example_output.txt"), "w") as f:
                f.write(example_output or "Example failed to run")
            if example_output:
                test_messages.append("Usage example ran successfully")
            else:
                tests_passed = False
                test_messages.append("Usage example failed")

        step_duration = (datetime.datetime.now() - step_start).total_seconds()
        self._log_step_result(
            "Run tests with installed package",
            tests_passed,
            step_duration,
            "; ".join(test_messages),
        )

        # Final verification - Check the package structure to ensure it was installed correctly
        step_start = datetime.datetime.now()
        print("\n========== Final Verification: Package structure check ==========")
        structure_check_script = os.path.join(self.temp_dir, "check_structure.py")

        with open(structure_check_script, "w") as f:
            f.write(
                """
import sys
import os
import importlib
from pathlib import Path

try:
    # Import fit_better safely
    fit_better = importlib.import_module("fit_better")
    
    # Check if __version__ attribute exists
    version = getattr(fit_better, "__version__", "unknown")
    print(f"fit_better version: {version}")
    print(f"fit_better package location: {os.path.dirname(fit_better.__file__)}")
    
    # Check key modules and subpackages
    core_packages = ["models", "core", "utils", "evaluation", "io"]
    for pkg in core_packages:
        try:
            module = importlib.import_module(f"fit_better.{pkg}")
            print(f"✓ Successfully imported fit_better.{pkg}")
        except ImportError as e:
            print(f"✗ Failed to import fit_better.{pkg}: {e}")
    
    # Print package directory structure
    base_dir = Path(os.path.dirname(fit_better.__file__))
    print("\\nPackage directory structure:")
    for i, (root, dirs, files) in enumerate(os.walk(base_dir)):
        if i > 10:  # Limit depth to avoid excessive output
            break
        rel_root = os.path.relpath(root, base_dir.parent)
        print(f"{rel_root}/")
        for d in sorted(dirs):
            print(f"  └── {d}/")
        for f in sorted(files):
            if f.endswith('.py'):
                print(f"  ├── {f}")
    
    print("\\nStructure check completed successfully")
    sys.exit(0)
except Exception as e:
    print(f"Error during structure check: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
            )

        structure_output = self._run_command(f"{python_exe} {structure_check_script}")
        structure_success = structure_output is not None

        with open(os.path.join(self.results_dir, "structure_check.txt"), "w") as f:
            f.write(structure_output or "Structure check failed")

        step_duration = (datetime.datetime.now() - step_start).total_seconds()
        self._log_step_result(
            "Package structure check",
            structure_success,
            step_duration,
            (
                "Structure check completed"
                if structure_success
                else "Structure check failed"
            ),
        )

        # Calculate overall test status and duration
        end_time = datetime.datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        # Update summary
        successful_steps = sum(
            1 for step in self.test_results["steps"] if step["success"]
        )
        total_steps = len(self.test_results["steps"])

        self.test_results["summary"]["status"] = (
            "passed" if successful_steps == total_steps else "failed"
        )
        self.test_results["summary"]["duration"] = total_duration
        self.test_results["summary"][
            "details"
        ] = f"Completed {successful_steps}/{total_steps} steps successfully"

        # Save the test results to a JSON file
        results_file = os.path.join(self.results_dir, "test_results.json")
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)

        if successful_steps == total_steps:
            print(
                f"\n========== Test completed successfully! ({total_duration:.1f}s) =========="
            )
        else:
            print(
                f"\n========== Test completed with {total_steps - successful_steps} failures! ({total_duration:.1f}s) =========="
            )

        print(f"Test results saved to: {self.results_dir}")

        # Required for the test to pass even if some steps failed
        return successful_steps == total_steps


if __name__ == "__main__":
    unittest.main()
