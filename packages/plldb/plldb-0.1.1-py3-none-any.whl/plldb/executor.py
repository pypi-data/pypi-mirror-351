from collections.abc import Callable
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator
import uuid


class Executor:
    """Executor for managing debug sessions.

    This class provides functionality for managing debug sessions, including:
    - Working directory management
    - CloudFormation template handling
    - Virtual environment integration

    Attributes:
        working_dir (Path): Path to the working directory
        cfn_template_path (Path): Path to the CloudFormation template
    """

    def __init__(
        self,
        working_dir: str | Path | None = None,
        cfn_template_path: str | Path | None = None,
    ):
        """Initialize the Executor.

        Args:
            working_dir: Path to the working directory. If None, uses current working directory.
            cfn_template_path: Path to the CloudFormation template. If None, uses 'template.yaml' in working directory.
        """
        self.working_dir = working_dir or Path(os.getcwd())
        self.cfn_template_path = cfn_template_path or Path(self.working_dir) / "template.yaml"

    def invoke_lambda_function(
        self,
        lambda_function_logical_id: str,
        event: dict,
        lambda_context: Any | None = None,
        environment: dict | None = None,
    ) -> None:
        """Invoke a Lambda function locally.

        Args:
            lambda_function_logical_id: Logical ID of the Lambda function in the CloudFormation template
            event: Event data to pass to the Lambda function
            lambda_context: Optional Lambda context object. If None, a default context will be created.

        Returns:
            The result of the Lambda function invocation.

        Raises:
            RuntimeError: If the Lambda function cannot be found or invoked.
        """

        if lambda_context is None:
            # create new type tha mimics the lambda context
            lambda_context = type(
                "LambdaContext",
                (),
                {
                    "aws_request_id": str(uuid.uuid4()),
                    "function_name": lambda_function_logical_id,
                    "function_version": "1",
                    "invoked_function_arn": f"arn:aws:lambda:us-east-1:123456789012:function:{lambda_function_logical_id}",
                    "memory_limit_in_mb": 128,
                    "remaining_time_in_millis": lambda: 300000,  # Placeholder
                },
            )()

        with self.with_site_packages():
            with self.with_lambda_handler(lambda_function_logical_id) as handler:
                with self.with_environment(environment):
                    return handler(event, lambda_context)

    @contextmanager
    def with_environment(self, environment: dict | None = None) -> Generator[None, None, None]:
        """Context manager for setting environment variables."""
        original_environment = os.environ.copy()
        if environment:
            os.environ.update(environment)
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(original_environment)

    @contextmanager
    def with_site_packages(self) -> Generator[None, None, None]:
        """
        This function tries to find virtualenv in the working directory
        If the virtualenv is found then site-packages are added to the PYTHONPATH for the context
        managed by the context manager.
        """
        original_sys_path = sys.path.copy()
        original_pythonpath = os.environ.get("PYTHONPATH", "")

        try:
            # Find virtual environment in working directory
            working_path = Path(self.working_dir)
            venv_candidates = [".venv", "venv", ".virtualenv", "virtualenv", "env"]

            venv_path = None
            for candidate in venv_candidates:
                candidate_path = working_path / candidate
                if candidate_path.exists() and candidate_path.is_dir():
                    # Check if it's a valid virtual environment
                    if (candidate_path / "lib").exists() or (candidate_path / "Lib").exists():
                        venv_path = candidate_path
                        break

            if venv_path:
                # Find site-packages directory
                site_packages = None

                # Check common locations for site-packages
                if sys.platform == "win32":
                    lib_path = venv_path / "Lib"
                    if lib_path.exists():
                        site_packages = lib_path / "site-packages"
                else:
                    lib_path = venv_path / "lib"
                    if lib_path.exists():
                        # Find python version directory
                        for python_dir in lib_path.iterdir():
                            if python_dir.is_dir() and python_dir.name.startswith("python"):
                                site_packages = python_dir / "site-packages"
                                if site_packages.exists():
                                    break

                if site_packages and site_packages.exists():
                    # Add site-packages to sys.path
                    site_packages_str = str(site_packages)
                    if site_packages_str not in sys.path:
                        sys.path.insert(0, site_packages_str)

                    # Update PYTHONPATH environment variable
                    if original_pythonpath:
                        os.environ["PYTHONPATH"] = f"{site_packages_str}{os.pathsep}{original_pythonpath}"
                    else:
                        os.environ["PYTHONPATH"] = site_packages_str

            yield

        finally:
            # Restore original sys.path and PYTHONPATH
            sys.path[:] = original_sys_path
            if original_pythonpath:
                os.environ["PYTHONPATH"] = original_pythonpath
            else:
                os.environ.pop("PYTHONPATH", None)

    @contextmanager
    def with_lambda_handler(
        self,
        lambda_function_logical_id: str,
    ) -> Generator[Callable, None, None]:
        """Context manager for accessing a Lambda function handler.

        Args:
            lambda_function_logical_id: Logical ID of the Lambda function in the CloudFormation template

        Yields:
            The Lambda function handler callable

        Raises:
            LambdaFunctionNotFoundError: If the Lambda function is not found in the template
            LambdaFunctionNotAServerlessFunctionError: If the resource is not an AWS::Serverless::Function
            ValueError: If the handler format is invalid
        """
        cfn_template = self.load_cfn_template()

        if lambda_function_logical_id not in cfn_template["Resources"]:
            raise LambdaFunctionNotFoundError(f"Lambda function '{lambda_function_logical_id}' not found in template")

        lambda_function = cfn_template["Resources"][lambda_function_logical_id]
        if lambda_function["Type"] == "AWS::Serverless::Function":
            code_uri = lambda_function["Properties"].get("CodeUri", ".")
            handler = lambda_function["Properties"]["Handler"]
        else:
            raise LambdaFunctionNotAServerlessFunctionError(f"Resource '{lambda_function_logical_id}' is not an AWS::Serverless::Function")

        # Parse handler string (format: module.function)
        handler_parts = handler.split(".")
        if len(handler_parts) < 2:
            raise ValueError(f"Invalid handler format: {handler}. Expected 'module.function'")

        module_path = ".".join(handler_parts[:-1])
        handler_name = handler_parts[-1]

        # Build full path to the lambda code
        code_path = Path(self.working_dir) / code_uri

        # Save original sys.path
        original_sys_path = sys.path.copy()

        try:
            # Add code path to sys.path so we can import the module
            if str(code_path) not in sys.path:
                sys.path.insert(0, str(code_path))

            # Import the module
            import importlib

            module = importlib.import_module(module_path)

            # Get the handler function
            handler_func = getattr(module, handler_name)

            yield handler_func

        finally:
            # Restore original sys.path
            sys.path[:] = original_sys_path

            # Remove the imported module from sys.modules to ensure clean state
            if module_path in sys.modules:
                del sys.modules[module_path]

    def load_cfn_template(self):
        from plldb.util.cfn import load_yaml

        with open(self.cfn_template_path, "r") as file:
            return load_yaml(file.read())


class LambdaFunctionNotFoundError(Exception):
    """Exception raised when a Lambda function is not found in the CloudFormation template."""


class LambdaFunctionNotAServerlessFunctionError(Exception):
    """Exception raised when a resource is not an AWS::Serverless::Function."""
