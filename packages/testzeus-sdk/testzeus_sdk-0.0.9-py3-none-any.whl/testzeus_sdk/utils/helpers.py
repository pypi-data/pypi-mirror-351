"""
Helper functions for TestZeus SDK.
"""

from typing import Any, Dict, List, Optional, Union

from testzeus_sdk.client import TestZeusClient
from testzeus_sdk.managers.base import record_to_dict


def get_id_by_name(client: TestZeusClient, collection: str, name: str, tenant_id: Optional[str] = None) -> Optional[str]:
    """
    Get entity ID by name.

    Args:
        client: TestZeus client instance
        collection: Collection name
        name: Entity name
        tenant_id: Tenant ID (optional, will use authenticated user's tenant if not provided)

    Returns:
        Entity ID or None if not found
    """
    if not tenant_id:
        tenant_id = client.get_tenant_id()
        if not tenant_id:
            raise ValueError("User must be authenticated with a tenant to find by name")

    try:
        filter_str = f'name = "{name}" && tenant = "{tenant_id}"'
        result = client.pb.collection(collection).get_first_list_item(filter_str)
        return str(result.id) if result else None
    except Exception as e:
        print(f"Warning: Error finding entity by name ({name}): {str(e)}")
        return None


async def expand_test_run_tree(client: TestZeusClient, test_run_id: str) -> Dict[str, Any]:
    """
    Build complete expanded tree of a test run with all details.

    Args:
        client: TestZeus client instance
        test_run_id: Test run ID

    Returns:
        Complete test run tree with all details
    """
    test_run = await client.test_runs.get_one(test_run_id)
    test_run_dashs = await client.test_run_dashs.get_list(filters={"test_run": test_run_id})
    test_run_dashs_data = []
    for test_run_dash in test_run_dashs["items"]:
        test_run_dashs_data.append(test_run_dash.data)

    test_run_dash_outputs = await client.test_run_dash_outputs.get_list(filters={"test_run_dash": [test_run_dash.id for test_run_dash in test_run_dashs["items"]]})
    test_run_dash_outputs_data = []
    for test_run_dash_output in test_run_dash_outputs["items"]:
        test_run_dash_outputs_data.append(test_run_dash_output.data)

    test_run_dash_output_steps = await client.test_run_dash_output_steps.get_list(
        filters={"test_run_dash_output": [test_run_dash_output.id for test_run_dash_output in test_run_dash_outputs["items"]]}
    )
    test_run_dash_output_steps_data = []
    for test_run_dash_output_step in test_run_dash_output_steps["items"]:
        test_run_dash_output_steps_data.append(test_run_dash_output_step.data)

    test_run_dash_outputs_attachments = await client.test_run_dash_outputs_attachments.get_list(
        filters={"test_run_dash_output": [test_run_dash_output.id for test_run_dash_output in test_run_dash_outputs["items"]]}
    )
    test_run_dash_outputs_attachments_data = []
    for test_run_dash_outputs_attachment in test_run_dash_outputs_attachments["items"]:
        test_run_dash_outputs_attachments_data.append(test_run_dash_outputs_attachment.data)

    result_dict: Dict[str, Any] = {
        "test_run": test_run.data,
        "test_run_dashs": test_run_dashs_data,
        "test_run_dash_outputs": test_run_dash_outputs_data,
        "test_run_dash_output_steps": test_run_dash_output_steps_data,
        "test_run_dash_outputs_attachments": test_run_dash_outputs_attachments_data,
    }

    return result_dict


def convert_name_refs_to_ids(client: TestZeusClient, data: Dict[str, Any], ref_fields: Dict[str, str]) -> Dict[str, Any]:
    """
    Convert name-based references to ID-based references.

    Args:
        client: TestZeus client instance
        data: Entity data with potential name-based references
        ref_fields: Dictionary mapping field names to collection names

    Returns:
        Processed data with ID-based references
    """
    result = data.copy()
    tenant_id = client.get_tenant_id()

    if not tenant_id:
        print("Warning: No tenant ID available for reference conversion")

    for field, collection in ref_fields.items():
        if field in result and isinstance(result[field], str):
            # Skip conversion if field value is already a valid ID
            # Simple ID validation - 15 character alphanumeric string
            if len(result[field]) == 15 and result[field].isalnum():
                continue

            # Convert name to ID
            entity_id = get_id_by_name(client, collection, result[field], tenant_id)
            if entity_id:
                result[field] = entity_id
            else:
                print(f"Warning: Could not find entity with name '{result[field]}' in collection '{collection}'")

    return result
