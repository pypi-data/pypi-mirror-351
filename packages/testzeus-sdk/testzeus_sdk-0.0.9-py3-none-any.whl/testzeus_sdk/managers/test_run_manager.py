"""
TestRun manager class for TestZeus test run operations.
"""

from typing import Any, Dict, List, Literal, Optional

from testzeus_sdk.client import TestZeusClient
from testzeus_sdk.managers.base import BaseManager
from testzeus_sdk.models.test_run import TestRun
from testzeus_sdk.utils.helpers import expand_test_run_tree, get_id_by_name


class TestRunManager(BaseManager[TestRun]):
    """
    Manager class for TestZeus test run entities.

    This class provides CRUD operations and specialized methods
    for working with test run entities.
    """

    def __init__(self, client: TestZeusClient) -> None:
        """
        Initialize a TestRunManager.

        Args:
            client: TestZeus client instance
        """
        super().__init__(client, "test_runs", TestRun)

    async def create_and_start(
        self,
        name: str,
        test: str,
        modified_by: Optional[str] = None,
        tenant: Optional[str] = None,
        execution_mode: Optional[Literal["lenient", "strict"]] = "lenient",
    ) -> TestRun:
        """
        Create and start a test run.

        Args:
            name: Name for the test run
            test: Test ID or name
            modified_by: User ID who is modifying the test run (optional)
            tenant: Tenant ID to associate with this test run (optional)

        Returns:
            Created and started test run instance
        """
        from testzeus_sdk.managers.test_manager import TestManager

        # Get test ID if a name was provided
        test_id = test
        if not self._is_valid_id(test):
            test_manager = TestManager(self.client)
            test_obj = await test_manager.get_one(test)
            test_id = str(test_obj.id)

            if execution_mode != test_obj.execution_mode:
                await test_manager.update_test(test_id, execution_mode=execution_mode)

        # Create the test run data
        run_data = {
            "name": name,
            "status": "pending",
            "test": test_id,
            "execution_mode": execution_mode,	
        }

        # Add modified_by if provided
        if modified_by:
            run_data["modified_by"] = modified_by

        # Add tenant if provided
        if tenant:
            run_data["tenant"] = tenant

        # Create the test run
        return await self.create(run_data)

    async def cancel(
        self,
        id_or_name: str,
        modified_by: Optional[str] = None,
        tenant: Optional[str] = None,
    ) -> TestRun:
        """
        Cancel a test run.

        Args:
            id_or_name: Test run ID or name
            modified_by: User ID who is canceling the test run (optional)
            tenant: Tenant ID to associate with this operation (optional)

        Returns:
            Updated test run instance
        """
        # Get the test run
        test_run = await self.get_one(id_or_name)

        # Check if it's in a cancellable state
        if test_run.status not in ["pending", "running"]:
            raise ValueError(f"Test run must be in 'pending' or 'running' status to cancel, but is in '{test_run.status}'")

        # Prepare update data
        update_data = {"status": "cancelled"}

        # Add modified_by if provided
        if modified_by:
            update_data["modified_by"] = modified_by

        # Add tenant if provided
        if tenant:
            update_data["tenant"] = tenant

        # Update to cancelled status
        return await self.update(str(test_run.id), update_data)

    async def cancel_with_email(self, id_or_name: str, user_email: str, tenant: Optional[str] = None) -> TestRun:
        """
        Cancel a test run, using a user's email address.

        Args:
            id_or_name: Test run ID or name
            user_email: Email address of the user who is canceling the test run
            tenant: Tenant ID to associate with this operation (optional)

        Returns:
            Updated test run instance
        """
        # Look up the user ID from the email
        user = await self.client.users.find_by_email(user_email)
        if not user:
            raise ValueError(f"Could not find user with email: {user_email}")

        # Use the user ID to cancel the test run
        return await self.cancel(id_or_name, modified_by=str(user.id), tenant=tenant)

    async def get_expanded(self, id_or_name: str) -> Dict[str, Any]:
        """
        Get a test run with all expanded details including outputs, steps, and attachments.

        Args:
            id_or_name: Test run ID or name

        Returns:
            Complete test run tree with all details
        """
        # Get the ID if a name was provided
        test_run_id = await self._get_id_from_name_or_id(id_or_name)
        return await expand_test_run_tree(self.client, test_run_id)

    async def download_all_attachments(self, id_or_name: str, output_dir: str = ".") -> List[str]:
        """
        Download all attachments for a test run.

        Args:
            id_or_name: Test run ID or name
            output_dir: Directory to save attachments

        Returns:
            List of downloaded attachment filenames
        """

        expanded_test_run = await self.get_expanded(id_or_name)
        attachments = expanded_test_run["test_run_dash_outputs_attachments"]
        downloaded_files = []

        for attachment in attachments:
            filepath = await self.client.test_run_dash_outputs_attachments.download_attachment(attachment["id"], output_dir)
            if filepath:
                downloaded_files.append(filepath)

        return downloaded_files

    def _process_references(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process name-based references to ID-based references.

        Args:
            data: Test run data with potential name-based references

        Returns:
            Processed data with ID-based references
        """
        result = data.copy()
        tenant_id = self.client.get_tenant_id()

        # Process test reference
        if "test" in result and isinstance(result["test"], str) and not self._is_valid_id(result["test"]):
            test_id = get_id_by_name(self.client, "tests", result["test"], tenant_id)
            if test_id:
                result["test"] = test_id

        # Process environment reference
        if "environment" in result and isinstance(result["environment"], str) and not self._is_valid_id(result["environment"]):
            env_id = get_id_by_name(self.client, "environment", result["environment"], tenant_id)
            if env_id:
                result["environment"] = env_id

        # Process tags references
        if "tags" in result and isinstance(result["tags"], list):
            tag_ids = []
            for tag in result["tags"]:
                if isinstance(tag, str):
                    if self._is_valid_id(tag):
                        tag_ids.append(tag)
                    else:
                        tag_id = get_id_by_name(self.client, "tags", tag, tenant_id)
                        if tag_id:
                            tag_ids.append(tag_id)
            result["tags"] = tag_ids

        return result

    async def create_and_start_with_email(self, name: str, test: str, user_email: str, tenant: Optional[str] = None) -> TestRun:
        """
        Create and start a test run, using a user's email address.

        Args:
            name: Name for the test run
            test: Test ID or name
            user_email: Email address of the user who is creating the test run
            tenant: Tenant ID to associate with this test run (optional)

        Returns:
            Created and started test run instance
        """
        # Look up the user ID from the email
        user = await self.client.users.find_by_email(user_email)
        if not user:
            raise ValueError(f"Could not find user with email: {user_email}")

        # Use the user ID to create and start the test run
        return await self.create_and_start(name, test, modified_by=str(user.id), tenant=tenant)
