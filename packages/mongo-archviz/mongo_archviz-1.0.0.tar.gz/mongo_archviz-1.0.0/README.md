# mongo-archviz

## MongoDB Schema Report Generator
The **MongoDB Schema Report Generator** is a Python package that analyzes your MongoDB database and generates a report in a format compatible with [dbdiagram.io](https://dbdiagram.io/). This tool extracts collection schemas, infers field types, identifies indexes, and detects potential relationships between collections. It is especially useful for visualizing and documenting your database architecture.

## Features

- **Schema Extraction:** Infers field types by sampling documents from collections.
- **Index Analysis:** Retrieves and lists indexes defined on each collection.
- **Relationship Detection:** Identifies potential relationships based on naming conventions.
- **dbdiagram.io Format:** Outputs the entire schema in a format that can be directly imported into dbdiagram.io.
- **Customizable Report:** Option to generate the report as a string or save it directly to a file.

### Visual Enhancement Features *(PRO Users of DBDiagram Only)*
- **Smart Table Coloring**: Automatically assigns header colors to tables based on their relationships:
  - **Connected Tables**: Tables linked through foreign key relationships receive matching unique colors from a predefined color palette
  - **Standalone Tables**: Tables with no foreign key connections are colored black for easy identification
  - **Relationship Groups**: All tables within the same relationship chain share the same distinctive color
- **Reference Collections Grouping**: Automatically creates a "Reference_Collections" table group that contains all standalone tables (those with black headers), making it easy to identify and manage unconnected collections in your database schema

These visual enhancements are exclusively available for dbdiagram.io PRO plan users and significantly improve the readability and organization of complex database schemas by providing immediate visual context about table relationships and dependencies.

## Installation

You can install the package via pip (if published on PyPI):

```bash
pip install mongo-archviz
```

Alternatively, install from source:

```bash
git clone https://github.com/yourusername/mongo-archviz.git
cd mongo-archviz
pip install .
```

## Usage

Below is a quick example of how to use the package in your project:

```python
from pymongo import MongoClient
from mongo_archviz import MongoDBSchema

# Connect to your MongoDB instance
client = MongoClient("mongodb://localhost:27017")
db = client["your_database"]

# Initialize the schema extractor with an optional project description
schema_extractor = MongoDBSchema(db, project_description="Example project for MongoDB architecture visualization")

# Generate the report in dbdiagram.io format and print it
report = schema_extractor.generate_report()
print(report)

# Optionally, save the report to a file
schema_extractor.generate_report(output_file="db_report.txt")
```

### 🔧 Setup
---
Before using this package, ensure you have the required dependency:

```bash
pip install pymongo
```

And establish a connection to your MongoDB instance:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
```

Alternatively, you can use a typical function for connecting to MongoDB instance:

```python
from pymongo import MongoClient

def getMongoConnection():
    """
    Use this function get the Mongodb Connection
    :return:
    """
    try:
        global client
        if client is None:

            query_str = "mongodb://" + DB_USER + ":" + DB_PASSWORD + "@" + \
                        DB_HOSTNAME + ":" + DB_PORT + "/" + DB_NAME
            client = MongoClient(query_str, connect=False)

        db = client.get_database(constants.DB_NAME)
        return db
		
    except Exception as ex:
        print("Error connecting to Mongo server.")

db = getMongoConnection()
```

### 🚀 Initialize the Schema Extractor
___
```python
schema_parser = MongoDBSchema(
    db=db,
    known_collections=["logs", "temp"],
    exclude_col=True,
    project_description="My project analyzing MongoDB schema structure"
)
```
Parameters:
* **db (Database)**: Your MongoDB database object.
* **known_collections (List[str], optional)**: A list of collections to include or exclude, depending on exclude_col.
* **exclude_col (bool)**:
  * If **False**, only collections listed in known_collections will be processed.
  * If **True**, all collections except those in known_collections will be processed.
* **project_description (str)**: A description of the project. This is used in the generated documentation or diagrams.

---

### 📚 Get All Collections
```python
collections = schema_parser.get_all_collections()
print(collections)
```
Returns a list of collections after applying inclusion/exclusion logic.

### 🧬 Analyze a Collection Schema
```python
schema = schema_parser.get_collection_schema("users", sample_size=20)
print(schema)
```
Returns a dictionary with field names and their inferred data types by sampling recent documents.

### 🔍 Get Collection Indexes
```python
indexes = schema_parser.get_collection_indexes("users")
for idx in indexes:
    print(idx)
```
Returns a list of all index information for a collection.

### 🎨 Convert to dbdiagram.io Format
```python
dbdiagram_syntax = schema_parser.to_dbdiagram_format()
with open("schema.dbml", "w") as f:
    f.write(dbdiagram_syntax)
```
Outputs the full schema in [dbdiagram.io](https://dbdiagram.io/) compatible `.dbml` format, including:
* Table structures
* Relationships
* Project metadata
* Color-coded tables


## Documentation

The source code is well-documented with inline comments and docstrings. You can explore the code in the `src/mongo_archviz/schema.py` file for more details on how each method works.

## Testing

Unit tests are provided in the `tests/` directory. To run the tests, execute:

```bash
python -m unittest discover -s tests
```

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch:\
   ```git checkout -b feature/my-new-feature```
3. Commit your changes:\
   ```git commit -am 'Add new feature'```
4. Push the branch:\
  ```git push origin feature/my-new-feature```
5. Open a pull request on GitHub.

For more details, please refer to the [CONTRIBUTING.md](./CONTRIBUTING.md) file.

## Licence

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue on GitHub or contact rishialuri@gmail.com.

