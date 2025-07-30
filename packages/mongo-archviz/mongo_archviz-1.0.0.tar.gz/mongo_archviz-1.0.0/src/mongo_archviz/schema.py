"""
MongoDB Schema Report Generator.

This module provides functionality to analyze MongoDB databases and generate
schema reports compatible with dbdiagram.io format. It extracts collection schemas,
identifies relationships, and provides visual enhancements for database visualization.

Features:
- Schema extraction from MongoDB collections
- Relationship detection between collections
- Index analysis and documentation
- Color-coded table visualization (PRO plan)
- Automatic table grouping for standalone collections
"""

from __future__ import annotations

import datetime
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pymongo.database import Database

"""
This module provides tools to introspect a MongoDB schema 
and generate dbdiagram.io-compatible definitions.
"""


class MongoDBSchema:
    """Parses a MongoDB database and generates schema documentation."""

    def __init__(
            self,
            db: Database,
            known_collections: Optional[list] = None,
            exclude_col: Optional[bool] = None,
            project_description: str = None,
    ):
        """
        Initialize the MongoDB Schema Extractor with a database connection.

        Args:
        db (pymongo.database.Database): A pymongo database connection object.

        known_collections (Optional[list]): List of collection names either to exclude
        from report or include-only in report. Will depend on `exclude_col`.

        exclude_col (Optional[bool]): If False, given `known_collections` will be
        excluded from get_all_collections(). If True, only the `known_collections
        will be considered in get_all_collections(). Wont be used if `known_collections` is none.

        project_description (str): Project description of the Database
        """
        self.db = db
        self.collections_info = {}
        self.relationships = []
        self.known_collections = None
        self.exclude_col = None
        if known_collections is not None:
            self.known_collections = (
                known_collections
            )
            self.exclude_col = (
                exclude_col
                if exclude_col is not None
                else True
            )
        self.project_description = (
            project_description
            if project_description is not None
            else "No Description"
        )
        self.project_name = self.db.name

        # Color mapping for related tables
        self.table_colors = {}
        self.color_palette = [
            "#FF6B6B",
            "#4ECDC4",
            "#45B7D1",
            "#96CEB4",
            "#FECA57",
            "#FF9FF3",
            "#54A0FF",
            "#5F27CD",
            "#00D2D3",
            "#FF9F43",
            "#6C5CE7",
            "#A29BFE",
            "#FD79A8",
            "#FDCB6E",
            "#6C5CE7",
        ]
        self.current_color_index = 0

    def get_all_collections(self) -> List[str]:
        """
        Retrieve all collection names in the database.

        Returns:
            List[str]: List of all collection names in the connected database
        """
        if (
                self.exclude_col is not None
                and not self.exclude_col
        ):
            # Use Known Collections to generate report
            if self.known_collections is not None:
                return self.known_collections
        tmp_cols_list = (
            self.db.list_collection_names()
        )
        if self.known_collections is None:
            return tmp_cols_list
        if self.exclude_col:
            return list(
                set(tmp_cols_list)
                - set(self.known_collections)
            )
        return self.known_collections

    def get_collection_schema(
            self,
            collection_name: str,
            sample_size: int = 10,
    ) -> Dict[str, str]:
        """
        Infer the schema of a collection by sampling the most recent documents.

        Args:
            collection_name (str): Name of the collection to analyze
            sample_size (int): Number of recent documents to sample (default: 50)

        Returns:
            Dict[str, str]: Dictionary mapping field names to their inferred data types
        """
        collection = self.db[collection_name]

        # Get the latest documents (most recent first)
        cursor = collection.find().sort([("_id", -1)]).limit(sample_size)
        documents = list(cursor)

        if not documents:
            return {}

        schema = {}

        # Track potential foreign keys for relationship detection
        potential_foreign_keys = set()

        # First pass: collect all fields and their possible types
        field_types = defaultdict(set)

        for doc in documents:
            self._extract_field_types(
                doc,
                field_types,
                "",
                potential_foreign_keys,
            )

        # Second pass: determine the most appropriate type for each field
        for field, types in field_types.items():
            schema[
                field
            ] = self._determine_field_type(types)

            # Check if this might be a foreign key reference
            if (
                    field.endswith("_id")
                    and len(types) == 1
                    and "objectId" in types
            ):
                potential_foreign_keys.add(field)

        # Store the schema and potential foreign keys for later relationship analysis
        self.collections_info[collection_name] = {
            "schema": schema,
            "potential_foreign_keys": potential_foreign_keys,
        }

        return schema

    def _extract_field_types(
            self,
            doc: Dict[str, Any],
            field_types: Dict[str, Set[str]],
            prefix: str,
            foreign_keys: Set[str],
    ) -> None:
        """
        Recursively extract field types from a document.

        Args:
            doc (Dict[str, Any]): Document or subdocument to analyze
            field_types (Dict[str, Set[str]]): Dictionary to collect field types
            prefix (str): Prefix for nested fields
            foreign_keys (Set[str]): Set to collect potential foreign key fields
        """
        for key, value in doc.items():
            field_name = (
                f"{prefix}{key}"
                if prefix
                else key
            )

            # Skip internal MongoDB fields for clarity (except _id which is important)
            if (
                    field_name.startswith("_")
                    and field_name != "_id"
            ):
                continue

            # Determine the type
            if value is None:
                field_types[field_name].add(
                    "null"
                )
            elif isinstance(value, str):
                field_types[field_name].add(
                    "string"
                )
            elif isinstance(value, bool):
                field_types[field_name].add(
                    "boolean"
                )
            elif isinstance(value, int):
                field_types[field_name].add("int")
            elif isinstance(value, float):
                field_types[field_name].add(
                    "decimal"
                )
            elif isinstance(
                    value, datetime.datetime
            ):
                field_types[field_name].add(
                    "timestamp"
                )
            elif isinstance(value, datetime.date):
                field_types[field_name].add(
                    "date"
                )
            elif isinstance(value, list):
                field_types[field_name].add(
                    "array"
                )
                # If array has elements, analyze first element for array type - Not required as of now
                # if value and all(isinstance(x, dict) for x in value):
                #     # For embedded documents in arrays, we'll treat them as separate tables
                #     self._extract_field_types(value[0], field_types, f"{field_name}.", foreign_keys)
            elif isinstance(value, dict):
                field_types[field_name].add(
                    "object"
                )
                # Recursively process nested documents - Not required as of now
                # self._extract_field_types(value, field_types, f"{field_name}.", foreign_keys)
            else:
                # Handle other types like ObjectId
                type_name = type(value).__name__
                if type_name == "ObjectId":
                    field_types[field_name].add(
                        "objectId"
                    )
                    # Check if this might be a foreign key
                    if field_name.endswith("_id"):
                        foreign_keys.add(
                            field_name
                        )
                else:
                    field_types[field_name].add(
                        type_name
                    )

    def _determine_field_type(
            self, types: Set[str]
    ) -> str:
        """
        Determine the most appropriate field type based on observed types.

        Args:
            types (Set[str]): Set of observed types for a field

        Returns:
            str: Determined field type suitable for dbdiagram.io
        """
        # Remove "null" if there are other types (signifying optional fields)
        if len(types) > 1 and "null" in types:
            types.remove("null")

        data_type = None

        # Map MongoDB types to dbdiagram.io compatible types
        if "objectId" in types:
            data_type = "varchar(24)"  # ObjectId as varchar
        elif "string" in types:
            data_type = "varchar(255)"
        elif "int" in types:
            data_type = "int"
        elif (
                "decimal" in types or "float" in types
        ):
            data_type = "decimal(10, 2)"
        elif "boolean" in types:
            data_type = "boolean"
        elif (
                "timestamp" in types
                or "datetime" in types
        ):
            data_type = "timestamp"
        elif "date" in types:
            data_type = "date"
        elif "array" in types:
            data_type = "json"  # Arrays represented as JSON in SQL
        elif "object" in types:
            data_type = (
                "json"  # Nested documents as JSON
            )
        return (
            "varchar(255)"
            if data_type is None
            else data_type
        )

    def get_collection_indexes(
            self, collection_name: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all indexes defined on a collection.

        Args:
            collection_name (str): Name of the collection to analyze

        Returns:
            List[Dict[str, Any]]: List of index information dictionaries
        """
        collection = self.db[collection_name]
        indexes = list(collection.list_indexes())

        # Store index information
        if (
                collection_name
                in self.collections_info
        ):
            self.collections_info[
                collection_name
            ]["indexes"] = indexes
        else:
            self.collections_info[
                collection_name
            ] = {"indexes": indexes}

        return indexes

    def analyze_database(
            self,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze the entire database: collections, schemas, and indexes.

        This method runs a complete analysis of all collections in the database,
        inferring schemas, extracting indexes, and detecting relationships.

        Returns:
            Dict[str, Dict[str, Any]]: Complete database analysis results
        """
        collections = self.get_all_collections()

        for collection_name in collections:
            # Get schema and indexes
            self.get_collection_schema(
                collection_name
            )
            self.get_collection_indexes(
                collection_name
            )

        # Detect relationships between collections
        self._detect_relationships()

        # Assign colors to tables based on relationships
        self._assign_table_colors()

        return self.collections_info

    def _detect_relationships(self) -> None:
        """
        Detect potential relationships between collections based on field naming.

        This method analyzes field names across collections to identify potential
        foreign key relationships. It looks for naming patterns like 'collection_id'
        that typically indicate references between collections.
        """
        # For each collection with potential foreign keys
        for (
                source_collection,
                info,
        ) in self.collections_info.items():
            if (
                    "potential_foreign_keys"
                    not in info
            ):
                continue

            for foreign_key in info[
                "potential_foreign_keys"
            ]:
                # Extract the referenced collection name from the foreign key
                if (
                        foreign_key == "_id"
                ):  # Skip primary key
                    continue

                # Try to find the referenced collection
                if foreign_key.endswith("_id"):
                    # Remove "_id" suffix
                    ref_base = foreign_key[:-3]

                    # Try some common pluralization patterns
                    potential_refs = [
                        ref_base,  # singular (e.g., 'user_id' -> 'user')
                        f"{ref_base}s",  # simple plural (e.g., 'user_id' -> 'users')
                        ref_base[:-1] + "ies"
                        if ref_base.endswith("y")
                        else None,
                        # e.g., 'category_id' -> 'categories'
                    ]

                    # Look for matching collections
                    for ref_collection in filter(
                            None, potential_refs
                    ):
                        if (
                                ref_collection
                                in self.collections_info
                        ):
                            self.relationships.append(
                                {
                                    "source": source_collection,
                                    "source_field": foreign_key,
                                    "target": ref_collection,
                                    "target_field": "_id",  # Assuming standard MongoDB _id field
                                }
                            )
                            break

    def _assign_table_colors(self) -> None:
        """
        Assign colors to tables based on their relationships.
        Tables with foreign key relationships get the same unique color.
        Standalone tables get black color.
        """
        # Find all tables involved in relationships
        connected_tables = set()
        relationship_groups = []

        # Group tables by their relationships
        for rel in self.relationships:
            source = rel["source"]
            target = rel["target"]
            connected_tables.add(source)
            connected_tables.add(target)

            # Find if either source or target is already in a group
            found_group = None
            for group in relationship_groups:
                if (
                        source in group
                        or target in group
                ):
                    found_group = group
                    break

            if found_group:
                found_group.update(
                    [source, target]
                )
            else:
                relationship_groups.append(
                    {source, target}
                )

        # Merge overlapping groups
        merged_groups = []
        for group in relationship_groups:
            merged = False
            for merged_group in merged_groups:
                if (
                        group & merged_group
                ):  # If there's any intersection
                    merged_group.update(group)
                    merged = True
                    break
            if not merged:
                merged_groups.append(group)

        # Assign colors to relationship groups
        for group in merged_groups:
            color = self._get_next_color()
            for table in group:
                self.table_colors[table] = color

        # Assign black color to standalone tables
        all_tables = set(
            self.collections_info.keys()
        )
        standalone_tables = (
                all_tables - connected_tables
        )
        for table in standalone_tables:
            self.table_colors[table] = "#000000"

    def _get_next_color(self) -> str:
        """Get the next color from the color palette."""
        color = self.color_palette[
            self.current_color_index
            % len(self.color_palette)
            ]
        self.current_color_index += 1
        return color

    def to_dbdiagram_format(self) -> str:
        """
        Convert the database schema to dbdiagram.io compatible format.

        Returns:
            str: Complete database schema in dbdiagram.io compatible syntax
        """
        output = []
        # Process Project Name
        project_line = []
        project_line.append(f"Project {self.project_name} {{")
        project_line.append(
            "\tdatabase_type: 'MongoDB'"
        )
        project_line.append(
            f"\tNote: '{self.project_description}'"
        )
        project_line.append("}")
        output.append("\n".join(project_line))

        # Process each collection as a table
        for (
                collection_name,
                info,
        ) in self.collections_info.items():
            # Get the color for this table
            table_color = self.table_colors.get(
                collection_name, "#000000"
            )

            table_lines = [
                f"Table {collection_name} [headercolor: {table_color}]{{"
            ]
            # Add fields from schema
            if "schema" in info:
                # Ensure _id is always first
                if "_id" in info["schema"]:
                    table_lines.append(
                        f"  _id {info['schema']['_id']} [primary key]"
                    )

                # Add all other fields
                for field, field_type in info[
                    "schema"
                ].items():
                    if (
                            field != "_id"
                    ):  # Skip _id as we've already added it
                        table_lines.append(
                            f"  {field} {field_type}"
                        )

            # Add indexes
            if "indexes" in info:
                index_lines = []
                for index in info["indexes"]:
                    # Skip the default _id index
                    if (
                            index.get("name")
                            == "_id_"
                    ):
                        continue

                    key_fields = []
                    for key, _ in index.get(
                            "key", {}
                    ).items():
                        key_fields.append(key)

                    if key_fields:
                        index_line = f"    ({', '.join(key_fields)})"
                        if index.get("unique"):
                            index_line += (
                                " [unique]"
                            )
                        index_lines.append(
                            index_line
                        )

                if index_lines:
                    table_lines.append(
                        "  Indexes {"
                    )
                    table_lines.extend(
                        index_lines
                    )
                    table_lines.append("  }")

            table_lines.append("}")
            output.append("\n".join(table_lines))

        # Add relationships
        if self.relationships:
            output.append("// Relationships")
            for rel in self.relationships:
                output.append(
                    f"Ref: {rel['source']}.{rel['source_field']} > {rel['target']}.{rel['target_field']}"
                )

        # Add TableGroup for standalone tables (black color tables)
        standalone_tables = [
            table
            for table, color in self.table_colors.items()
            if color == "#000000"
        ]
        if standalone_tables:
            output.append("// Table Groups")
            table_group_lines = [
                "TableGroup Reference_Collections {"
            ]
            for table in standalone_tables:
                table_group_lines.append(
                    f"  {table}"
                )
            table_group_lines.append("}")
            output.append(
                "\n".join(table_group_lines)
            )

        return "\n\n".join(output)

    def generate_report(
            self, output_file: Optional[str] = None
    ) -> str:
        """
        Generate a complete database report and optionally save to a file.

        This method runs a full database analysis if not already done, then
        converts the results to dbdiagram.io format and optionally saves to a file.

        Args:
            output_file (Optional[str]): Path to save the report, or None to return as string

        Returns:
            str: Complete database report in dbdiagram.io format
        """
        # Ensure we have analyzed the database
        if not self.collections_info:
            self.analyze_database()

        # Convert to dbdiagram.io format
        diagram_code = self.to_dbdiagram_format()

        # Save to file if requested
        if output_file:
            with Path(output_file).open("w", encoding="utf-8") as f_diagram:
                f_diagram.write(diagram_code)

        return diagram_code
