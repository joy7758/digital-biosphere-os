import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from validator.object_schema_validator import ObjectSchemaValidator, SchemaRegistryError


class TestObjectSchemaValidator(unittest.TestCase):
    def test_load_schemas_handles_io_error(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            with self.assertRaisesRegex(SchemaRegistryError, "Cannot load local schema: common-object-schema.yaml"):
                ObjectSchemaValidator(schema_directory=temp_path)

    def test_load_schemas_handles_decode_error(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # create file that throws UnicodeError or DecodeError
            test_file = temp_path / "common-object-schema.yaml"
            with open(test_file, 'wb') as f:
                f.write(b'\x81')

            with self.assertRaisesRegex(SchemaRegistryError, "Cannot load local schema: common-object-schema.yaml"):
                ObjectSchemaValidator(schema_directory=temp_path)

    def test_load_schemas_handles_json_decode_error(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # create file that throws json.JSONDecodeError
            test_file = temp_path / "common-object-schema.yaml"
            with open(test_file, 'w') as f:
                f.write('invalid json')

            with self.assertRaisesRegex(SchemaRegistryError, "Cannot load local schema: common-object-schema.yaml"):
                ObjectSchemaValidator(schema_directory=temp_path)

if __name__ == '__main__':
    unittest.main()
