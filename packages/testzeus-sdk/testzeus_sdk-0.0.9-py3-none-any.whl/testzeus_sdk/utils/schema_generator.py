"""
Schema generator for TestZeus SDK.

This script generates model and manager classes from schema.json file.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union


class SchemaGenerator:
    """
    Generate Python models and manager classes from schema.json
    """

    def __init__(self, schema_path: str, output_dir: str):
        """
        Initialize the generator with schema path and output directory

        Args:
            schema_path: Path to the schema.json file
            output_dir: Root directory to output generated files
        """
        self.schema_path = schema_path
        self.output_dir = output_dir
        self.schema = self._load_schema()

        # Ensure output directories exist
        self.models_dir = os.path.join(output_dir, "models")
        self.managers_dir = os.path.join(output_dir, "managers")
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.managers_dir, exist_ok=True)

    def _load_schema(self) -> List[Dict[str, Any]]:
        """
        Load and parse the schema.json file

        Returns:
            List of collections from schema
        """
        with open(self.schema_path, "r") as file:
            return json.load(file)

    def generate_all(self):
        """Generate all models and managers from the schema"""
        # Skip system collections
        collections = [collection for collection in self.schema if not collection.get("system", False) and not collection.get("name", "").startswith("_")]

        for collection in collections:
            print(f"Generating model for {collection['name']}")
            self._generate_model(collection)
            print(f"Generating manager for {collection['name']}")
            self._generate_manager(collection)

        # Generate __init__.py files to make imports work
        self._generate_init_files(collections)

    def _to_snake_case(self, name: str) -> str:
        """Convert a string to snake_case"""
        # Already snake case
        if "_" in name:
            return name
        # Convert camelCase to snake_case
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        return name

    def _to_pascal_case(self, name: str) -> str:
        """Convert a string to PascalCase"""
        # Handle snake_case to PascalCase
        if "_" in name:
            return "".join(word.capitalize() for word in name.split("_"))
        # Already PascalCase or camelCase
        return name[0].upper() + name[1:]

    def _python_type_from_schema(self, field_type: str) -> str:
        """Convert schema field type to Python type"""
        type_map = {
            "text": "str",
            "email": "str",
            "url": "str",
            "number": "float",
            "bool": "bool",
            "date": "str",
            "select": "str",
            "json": "Dict[str, Any]",
            "file": "List[str]",
            "relation": "str",  # IDs are strings
            "editor": "str",
            "password": "str",
            "autodate": "str",
        }
        return type_map.get(field_type, "Any")

    def _generate_model(self, collection: Dict[str, Any]):
        """Generate a model class for the given collection"""
        collection_name = collection.get("name")
        model_name = self._to_snake_case(collection_name)
        class_name = self._to_pascal_case(model_name)

        # Don't overwrite existing model files
        file_path = os.path.join(self.models_dir, f"{model_name}.py")
        if os.path.exists(file_path):
            print(f"Skipping existing model file: {file_path}")
            return

        fields = collection.get("fields", [])

        # Start building the model class
        code = f"""\"\"\"
Model for {collection_name} collection.
\"\"\"

from typing import Dict, List, Any, Optional
import datetime
from .base import BaseModel


class {class_name}(BaseModel):
    \"\"\"
    {class_name} model for {collection_name} collection
    \"\"\"

    def __init__(self, data: Dict[str, Any]):
        \"\"\"
        Initialize a {class_name} instance
        
        Args:
            data: Dictionary containing model data
        \"\"\"
        super().__init__(data)
"""

        # Add fields from schema as class attributes
        system_fields = ["id", "created", "updated"]

        for field in fields:
            field_name = field.get("name")
            field_type = field.get("type")

            # Skip system fields already in BaseModel
            if field_name in system_fields:
                continue

            # Add field property
            code += f'        self.{field_name} = data.get("{field_name}")\n'

        # Write the model to file
        with open(file_path, "w") as file:
            file.write(code)

    def _generate_manager(self, collection: Dict[str, Any]):
        """Generate a manager class for the given collection"""
        collection_name = collection.get("name")
        model_name = self._to_snake_case(collection_name)
        class_name = self._to_pascal_case(model_name)
        manager_name = f"{class_name}Manager"

        # Don't overwrite existing manager files
        file_path = os.path.join(self.managers_dir, f"{model_name}_manager.py")
        if os.path.exists(file_path):
            print(f"Skipping existing manager file: {file_path}")
            return

        # Start building the manager class
        code = f"""\"\"\"
Manager for {collection_name} collection.
\"\"\"

from typing import Dict, List, Any, Optional, Union
from testzeus_sdk.models.{model_name} import {class_name}
from testzeus_sdk.client import TestZeusClient
from .base import BaseManager


class {manager_name}(BaseManager):
    \"\"\"
    Manager for {class_name} resources
    \"\"\"
    
    def __init__(self, client: TestZeusClient) -> None:
        \"\"\"
        Initialize the {class_name} manager
        
        Args:
            client: TestZeus client instance
        \"\"\"
        super().__init__(client, \"{collection_name}\", {class_name})

    def _process_references(self, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Process name-based references to ID-based references
        
        Args:
            data: Entity data with potential name-based references
            
        Returns:
            Processed data with ID-based references
        \"\"\"
        from testzeus_sdk.utils.helpers import convert_name_refs_to_ids
        
        # Define which fields are relations and what collections they reference
        ref_fields = {{
"""

        # Add relation fields
        relation_fields = []
        for field in collection.get("fields", []):
            if field.get("type") == "relation":
                field_name = field.get("name")
                target_collection = field.get("collectionId")
                relation_fields.append((field_name, target_collection))

        # Generate reference field mappings
        for field_name, target_collection in relation_fields:
            code += f'            "{field_name}": "{target_collection}",\n'

        code += """        }
        
        return convert_name_refs_to_ids(self.client, data, ref_fields)
"""

        # Add collection-specific methods based on collection name
        if collection_name == "tests":
            code += """
    def run_test(self, test_id: str, environment_id: Optional[str] = None) -> Any:
        \"\"\"
        Run a test
        
        Args:
            test_id: Test ID or name
            environment_id: Environment ID (optional)
            
        Returns:
            Test run result
        \"\"\"
        # Convert name to ID if needed
        if not self._is_valid_id(test_id):
            test = self.get_one(test_id)
            if not test:
                raise ValueError(f"Test not found: {test_id}")
            test_id = test.id
            
        data = {"test": test_id}
        if environment_id:
            data["environment"] = environment_id
            
        # Use the test runs manager to create a run
        return self.client.test_runs.create(data)
"""
        elif collection_name == "test_run_dashs":
            code += """
    def get_expanded(self, test_run_id: str) -> Dict[str, Any]:
        \"\"\"
        Get complete expanded tree of a test run with all details
        
        Args:
            test_run_id: Test run ID
            
        Returns:
            Complete test run tree with all details
        \"\"\"
        from testzeus_sdk.utils.helpers import expand_test_run_tree
        return expand_test_run_tree(self.client, test_run_id)
        
    def cancel(self, test_run_id: str) -> bool:
        \"\"\"
        Cancel a test run
        
        Args:
            test_run_id: Test run ID
            
        Returns:
            True if successful
        \"\"\"
        return self.update(test_run_id, {"status": "cancelled"})
"""

        # Write the manager to file
        with open(file_path, "w") as file:
            file.write(code)

    def _generate_init_files(self, collections: List[Dict[str, Any]]):
        """Generate __init__.py files for models and managers packages"""
        # Skip system collections
        valid_collections = [collection for collection in collections if not collection.get("system", False) and not collection.get("name", "").startswith("_")]

        # Generate models/__init__.py
        models_init_content = """\"\"\"
Models for TestZeus SDK.
\"\"\"

# Import all model classes
from .base import BaseModel
"""

        for collection in valid_collections:
            collection_name = collection.get("name")
            model_name = self._to_snake_case(collection_name)
            class_name = self._to_pascal_case(model_name)

            # Check if model file exists
            if os.path.exists(os.path.join(self.models_dir, f"{model_name}.py")):
                models_init_content += f"from .{model_name} import {class_name}\n"

        with open(os.path.join(self.models_dir, "__init__.py"), "w") as file:
            file.write(models_init_content)

        # Generate managers/__init__.py
        managers_init_content = """\"\"\"
Managers for TestZeus SDK.
\"\"\"

# Import all manager classes
from .base import BaseManager
"""

        for collection in valid_collections:
            collection_name = collection.get("name")
            model_name = self._to_snake_case(collection_name)
            class_name = self._to_pascal_case(model_name)

            # Check if manager file exists
            if os.path.exists(os.path.join(self.managers_dir, f"{model_name}_manager.py")):
                managers_init_content += f"from .{model_name}_manager import {class_name}Manager\n"

        with open(os.path.join(self.managers_dir, "__init__.py"), "w") as file:
            file.write(managers_init_content)


def main():
    """
    Main entry point for schema generator
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sdk_root = os.path.dirname(os.path.dirname(script_dir))

    schema_path = os.path.join(sdk_root, "schema.json")
    output_dir = os.path.join(sdk_root, "testzeus_sdk")

    generator = SchemaGenerator(schema_path, output_dir)
    generator.generate_all()
    print(f"Generated models and managers from schema at {schema_path}")


if __name__ == "__main__":
    main()
