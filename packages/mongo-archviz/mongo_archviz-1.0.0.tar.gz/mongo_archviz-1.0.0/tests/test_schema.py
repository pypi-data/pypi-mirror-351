import unittest
from pymongo import MongoClient
from mongo_archviz import MongoDBSchema

# Use mongomock for testing without a real MongoDB instance
try:
    from mongomock import MongoClient as MockClient
except ImportError:
    raise ImportError("Please install mongomock for testing: pip install mongomock")


class TestMongoDBSchema(unittest.TestCase):
    def setUp(self):
        # Create a mock MongoDB instance
        self.client = MockClient()
        self.db = self.client["test_db"]

        # Insert test documents into a test collection
        self.db.test_collection.insert_many([
            {"_id": 1, "name": "Alice", "age": 30, "created_at": "2025-03-30T12:00:00"},
            {"_id": 2, "name": "Bob", "age": 25, "created_at": "2025-03-30T12:05:00"},
        ])
        self.schema_extractor = MongoDBSchema(self.db)

    def test_get_all_collections(self):
        collections = self.schema_extractor.get_all_collections()
        self.assertIn("test_collection", collections)

    def test_generate_report(self):
        report = self.schema_extractor.generate_report()
        self.assertIsInstance(report, str)
        self.assertIn("Table test_collection", report)


if __name__ == '__main__':
    unittest.main()
