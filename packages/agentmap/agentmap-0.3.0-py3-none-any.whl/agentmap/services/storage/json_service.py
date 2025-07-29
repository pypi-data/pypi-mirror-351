"""
JSON Storage Service implementation for AgentMap.

This module provides a concrete implementation of the storage service
for JSON files, with support for path-based operations and nested documents.
"""
import os
import json
import contextlib
from collections.abc import Generator
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO, Union

from agentmap.services.storage.base import BaseStorageService
from agentmap.services.storage.types import StorageResult, WriteMode


class JSONStorageService(BaseStorageService):
    """
    JSON storage service implementation.
    
    Provides storage operations for JSON files with support for
    path-based access, nested documents, and query filtering.
    """
    
    # NOTE: This method is included for backward compatibility
    # The base class uses health_check(), but some code expects is_healthy()
    def is_healthy(self) -> bool:
        """
        Check if the service is healthy and ready to use.
        
        Returns:
            True if the service is healthy, False otherwise
        """
        return self.health_check()
    
    def _initialize_client(self) -> Any:
        """
        Initialize JSON client.
        
        For JSON operations, we don't need a complex client.
        Just ensure base directory exists and return a simple config.
        
        Returns:
            Configuration dict for JSON operations
        """
        base_dir = self._config.get_option("base_directory", "./data")
        encoding = self._config.get_option("encoding", "utf-8")
        
        # Ensure base directory exists
        os.makedirs(base_dir, exist_ok=True)
        
        return {
            "base_directory": base_dir,
            "encoding": encoding,
            "indent": self._config.get_option("indent", 2)
        }
    
    def _perform_health_check(self) -> bool:
        """
        Perform health check for JSON storage.
        
        Checks if base directory is accessible and we can perform
        basic JSON operations.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            base_dir = self.client["base_directory"]
            
            # Check if directory exists and is writable
            if not os.path.exists(base_dir):
                return False
            
            if not os.access(base_dir, os.W_OK):
                return False
            
            # Test basic JSON operation
            test_data = {"test": [1, 2, 3]}
            test_str = json.dumps(test_data)
            test_parsed = json.loads(test_str)
            
            if test_parsed.get("test")[0] != 1:
                return False
            
            return True
        except Exception as e:
            self._logger.debug(f"JSON health check failed: {e}")
            return False
    
    def _get_file_path(self, collection: str) -> str:
        """
        Get full file path for a collection.
        
        Args:
            collection: Collection name (can be relative or absolute path)
            
        Returns:
            Full file path
        """
        if os.path.isabs(collection):
            return collection
        
        base_dir = self.client["base_directory"]
        
        # Ensure .json extension
        if not collection.lower().endswith('.json'):
            collection = f"{collection}.json"
        
        return os.path.join(base_dir, collection)
    
    def _ensure_directory_exists(self, file_path: str) -> None:
        """
        Ensure the directory for a file path exists.
        
        Args:
            file_path: Path to file
        """
        directory = os.path.dirname(os.path.abspath(file_path))
        os.makedirs(directory, exist_ok=True)
    
    @contextlib.contextmanager
    def _open_json_file(self, file_path: str, mode: str = 'r') -> Generator[TextIO, None, None]:
        """
        Context manager for safely opening JSON files.
        
        Args:
            file_path: Path to the JSON file
            mode: File open mode ('r' for reading, 'w' for writing)
            
        Yields:
            File object
                
        Raises:
            FileNotFoundError: If the file doesn't exist (in read mode)
            PermissionError: If the file can't be accessed
            IOError: For other file-related errors
        """
        try:
            # Ensure directory exists for write operations
            if 'w' in mode:
                self._ensure_directory_exists(file_path)
                
            with open(file_path, mode, encoding=self.client["encoding"]) as f:
                yield f
        except FileNotFoundError:
            if 'r' in mode:
                self._logger.debug(f"JSON file not found: {file_path}")
                raise
            else:
                # For write mode, create the file
                self._ensure_directory_exists(file_path)
                with open(file_path, 'w', encoding=self.client["encoding"]) as f:
                    yield f
        except (PermissionError, IOError) as e:
            self._logger.error(f"File access error for {file_path}: {str(e)}")
            raise
    
    def _read_json_file(self, file_path: str, **kwargs) -> Any:
        """
        Read and parse a JSON file.
        
        Args:
            file_path: Path to the JSON file
            **kwargs: Additional json.load parameters
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file contains invalid JSON
        """
        try:
            with self._open_json_file(file_path, 'r') as f:
                return json.load(f, **kwargs)
        except FileNotFoundError:
            self._logger.debug(f"JSON file not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in {file_path}: {str(e)}"
            self._logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _write_json_file(self, file_path: str, data: Any, **kwargs) -> None:
        """
        Write data to a JSON file.
        
        Args:
            file_path: Path to the JSON file
            data: Data to write
            **kwargs: Additional json.dump parameters
            
        Raises:
            PermissionError: If the file can't be written
            TypeError: If the data contains non-serializable objects
        """
        try:
            # Extract indent from client config if not provided
            indent = kwargs.pop('indent', self.client.get('indent', 2))
            
            with self._open_json_file(file_path, 'w') as f:
                json.dump(data, f, indent=indent, **kwargs)
            self._logger.debug(f"Successfully wrote to {file_path}")
        except TypeError as e:
            error_msg = f"Cannot serialize to JSON: {str(e)}"
            self._logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _apply_path(self, data: Any, path: str) -> Any:
        """
        Extract data from a nested structure using dot notation.
        
        Args:
            data: Data structure to traverse
            path: Dot-notation path (e.g., "user.address.city")
            
        Returns:
            Value at the specified path or None if not found
        """
        if not path:
            return data
            
        components = path.split('.')
        current = data
        
        for component in components:
            if current is None:
                return None
                
            # Handle arrays with numeric indices
            if component.isdigit() and isinstance(current, list):
                index = int(component)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            # Handle dictionaries
            elif isinstance(current, dict):
                current = current.get(component)
            else:
                return None
                
        return current
    
    def _update_path(self, data: Any, path: str, value: Any) -> Any:
        """
        Update data at a specified path.
        
        Args:
            data: Data structure to modify
            path: Dot-notation path (e.g., "user.address.city")
            value: New value to set
            
        Returns:
            Updated data structure
        """
        if not path:
            return value
            
        # Make a copy to avoid modifying original
        if isinstance(data, dict):
            result = data.copy()
        elif isinstance(data, list):
            result = data.copy()
        else:
            # If data is not a container, start with empty dict
            result = {}
            
        components = path.split('.')
        current = result
        
        # Navigate to the parent of the target
        for i, component in enumerate(components[:-1]):
            # Handle array indices
            if component.isdigit() and isinstance(current, list):
                index = int(component)
                # Extend the list if needed
                while len(current) <= index:
                    current.append({})
                    
                # Create a nested structure if needed
                if current[index] is None:
                    if i < len(components) - 2 and components[i+1].isdigit():
                        current[index] = []  # Next level is array
                    else:
                        current[index] = {}  # Next level is dict
                        
                current = current[index]
                
            # Handle dictionary keys
            else:
                # Create nested structure if needed
                if not isinstance(current, dict):
                    if isinstance(current, list):
                        # We can't modify the structure type
                        return result
                    else:
                        # Replace with dict
                        current = {}
                        
                # Create the next level if it doesn't exist
                if component not in current:
                    if i < len(components) - 2 and components[i+1].isdigit():
                        current[component] = []  # Next level is array
                    else:
                        current[component] = {}  # Next level is dict
                        
                current = current[component]
        
        # Set the value at the final path component
        last_component = components[-1]
        
        # Handle array indices
        if last_component.isdigit() and isinstance(current, list):
            index = int(last_component)
            # Extend the list if needed
            while len(current) <= index:
                current.append(None)
            current[index] = value
        # Handle dictionary keys
        elif isinstance(current, dict):
            current[last_component] = value
        # Can't set the value in this structure
        else:
            return result
            
        return result
    
    def _delete_path(self, data: Any, path: str) -> Any:
        """
        Delete data at a specified path.
        
        Args:
            data: Data structure to modify
            path: Dot-notation path (e.g., "user.address.city")
            
        Returns:
            Updated data structure with value removed
        """
        if not path or data is None:
            return data
            
        # Make a copy to avoid modifying original
        if isinstance(data, dict):
            result = data.copy()
        elif isinstance(data, list):
            result = data.copy()
        else:
            # Cannot delete from non-container
            return data
            
        components = path.split('.')
        
        # Special case: direct key in dict
        if len(components) == 1 and isinstance(result, dict):
            if components[0] in result:
                del result[components[0]]
            return result
            
        # Special case: direct index in list
        if len(components) == 1 and components[0].isdigit() and isinstance(result, list):
            index = int(components[0])
            if 0 <= index < len(result):
                result.pop(index)
            return result
            
        # For nested paths, navigate to the parent
        current = result
        for i, component in enumerate(components[:-1]):
            # Handle array indices
            if component.isdigit() and isinstance(current, list):
                index = int(component)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    # Path doesn't exist
                    return result
            # Handle dictionary keys
            elif isinstance(current, dict) and component in current:
                current = current[component]
            else:
                # Path doesn't exist
                return result
                
        # Delete from parent
        last_component = components[-1]
        
        # Handle array indices
        if last_component.isdigit() and isinstance(current, list):
            index = int(last_component)
            if 0 <= index < len(current):
                current.pop(index)
        # Handle dictionary keys
        elif isinstance(current, dict) and last_component in current:
            del current[last_component]
            
        return result
    
    def _find_document_by_id(self, data: Any, document_id: str, id_field: str = 'id') -> Optional[Dict]:
        """
        Find a document by ID in different data structures.
        
        Args:
            data: JSON data structure
            document_id: Document ID to find
            id_field: Field name to use as document identifier
            
        Returns:
            Document data or None if not found
        """
        if not data:
            return None
            
        if isinstance(data, dict):
            # Direct key lookup
            if document_id in data:
                return data[document_id]
            
            # Search for document with matching ID field
            for key, value in data.items():
                if isinstance(value, dict) and value.get(id_field) == document_id:
                    return value
        
        elif isinstance(data, list):
            # Find in array by id field
            for item in data:
                if isinstance(item, dict) and item.get(id_field) == document_id:
                    return item
        
        return None
    
    def _ensure_id_in_document(self, data: Any, document_id: str, id_field: str = 'id') -> dict:
        """
        Ensure the document has the correct ID field.
        
        Args:
            data: Document data
            document_id: Document ID
            id_field: Field name to use as document identifier
            
        Returns:
            Document with ID field
        """
        if not isinstance(data, dict):
            return {id_field: document_id, "value": data}
        
        result = data.copy()
        result[id_field] = document_id
        return result
    
    def _create_initial_structure(self, data: Any, document_id: str, id_field: str = 'id') -> Any:
        """
        Create an initial data structure for a document.
        
        Args:
            data: Document data
            document_id: Document ID
            id_field: Field name to use as document identifier
            
        Returns:
            New data structure
        """
        if isinstance(data, dict):
            # For dict data, create a list with ID field
            doc_with_id = data.copy()
            doc_with_id[id_field] = document_id
            return [doc_with_id]
        else:
            # For other data, use a dict with document ID as key
            return {document_id: data}
    
    def _add_document_to_structure(
        self, 
        data: Any, 
        doc_data: Any, 
        document_id: str,
        id_field: str = 'id'
    ) -> Any:
        """
        Add a document to an existing data structure.
        
        Args:
            data: Current data structure
            doc_data: Document data
            document_id: Document ID
            id_field: Field name to use as document identifier
            
        Returns:
            Updated data structure
        """
        if isinstance(data, dict):
            # Add to dictionary
            data[document_id] = doc_data
            return data
        
        elif isinstance(data, list):
            # Add to list with ID
            if isinstance(doc_data, dict):
                # Make sure document has ID
                doc_with_id = doc_data.copy()
                doc_with_id[id_field] = document_id
                data.append(doc_with_id)
            else:
                # Wrap non-dict data
                data.append({id_field: document_id, "value": doc_data})
            return data
        
        else:
            # Create new structure
            return self._create_initial_structure(doc_data, document_id, id_field)
    
    def _update_document_in_structure(
        self,
        data: Any,
        doc_data: Any,
        document_id: str,
        id_field: str = 'id'
    ) -> tuple[Any, bool]:
        """
        Update a document in an existing data structure.
        
        Args:
            data: Current data structure
            doc_data: Document data
            document_id: Document ID
            id_field: Field name to use as document identifier
            
        Returns:
            Tuple of (updated data, whether document was created)
        """
        # Find existing document
        doc = self._find_document_by_id(data, document_id, id_field)
        created_new = False
        
        if doc is None:
            # Document not found, add it
            created_new = True
            data = self._add_document_to_structure(data, doc_data, document_id, id_field)
        else:
            # Document exists, update it
            if isinstance(data, dict):
                # Dictionary with direct keys
                if document_id in data:
                    data[document_id] = doc_data
                else:
                    # Find and update by ID field
                    for key, value in data.items():
                        if isinstance(value, dict) and value.get(id_field) == document_id:
                            data[key] = self._ensure_id_in_document(doc_data, document_id, id_field)
                            break
            
            elif isinstance(data, list):
                # List of documents
                for i, item in enumerate(data):
                    if isinstance(item, dict) and item.get(id_field) == document_id:
                        data[i] = self._ensure_id_in_document(doc_data, document_id, id_field)
                        break
        
        return data, created_new
    
    def _merge_documents(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two documents recursively.
        
        Args:
            doc1: First document
            doc2: Second document
            
        Returns:
            Merged document
        """
        if not isinstance(doc1, dict) or not isinstance(doc2, dict):
            return doc2
            
        result = doc1.copy()
        
        for key, value in doc2.items():
            # If both values are dicts, merge recursively
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_documents(result[key], value)
            # Otherwise, overwrite or add
            else:
                result[key] = value
                
        return result
    
    def _apply_query_filter(self, data: Any, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply query filtering to document data.
        
        Args:
            data: Document data
            query: Query parameters
            
        Returns:
            Dict with filtered data and metadata
        """
        # Extract special query parameters
        limit = query.pop("limit", None)
        offset = query.pop("offset", 0)
        sort_field = query.pop("sort", None)
        sort_order = query.pop("order", "asc").lower()
        
        # Handle empty data
        if data is None:
            return {"data": None, "count": 0, "is_collection": False}
            
        # Handle different data structures
        if isinstance(data, list):
            # Apply field filtering
            result = data
            if query:  # Only filter if there are query parameters remaining
                result = [
                    item for item in result 
                    if isinstance(item, dict) and 
                    all(
                        item.get(field) == value 
                        for field, value in query.items()
                    )
                ]
            
            # Apply sorting
            if sort_field and result:
                reverse = (sort_order == "desc")
                result.sort(
                    key=lambda x: x.get(sort_field) if isinstance(x, dict) else None,
                    reverse=reverse
                )
            
            # Apply pagination
            if offset and isinstance(offset, int) and offset > 0:
                result = result[offset:]
                
            if limit and isinstance(limit, int) and limit > 0:
                result = result[:limit]
                
            return {
                "data": result,
                "count": len(result),
                "is_collection": True
            }
            
        elif isinstance(data, dict):
            # Filter based on field values
            result = {}
            for key, value in data.items():
                if isinstance(value, dict) and all(
                    value.get(field) == query_value 
                    for field, query_value in query.items()
                ):
                    result[key] = value
            
            # Apply pagination to keys
            keys = list(result.keys())
            
            if offset and isinstance(offset, int) and offset > 0:
                keys = keys[offset:]
                
            if limit and isinstance(limit, int) and limit > 0:
                keys = keys[:limit]
                
            # Rebuild filtered dictionary
            if offset or limit:
                result = {k: result[k] for k in keys}
                
            return {
                "data": result,
                "count": len(result),
                "is_collection": True
            }
            
        # Other data types can't be filtered
        return {
            "data": data,
            "count": 0,
            "is_collection": False
        }
    
    def read(
        self, 
        collection: str, 
        document_id: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
        path: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Read data from JSON file.
        
        Args:
            collection: JSON file name/path
            document_id: Document ID to read
            query: Query parameters for filtering
            path: Dot-notation path for nested access
            **kwargs: Additional parameters
            
        Returns:
            Document data based on query and path
        """
        try:
            file_path = self._get_file_path(collection)
            
            if not os.path.exists(file_path):
                self._logger.debug(f"JSON file does not exist: {file_path}")
                return {} if document_id is None else None
            
            # Extract service-specific parameters
            format_type = kwargs.pop('format', 'raw')
            id_field = kwargs.pop('id_field', 'id')
            
            # Read the JSON file
            data = self._read_json_file(file_path, **kwargs)
            
            # Apply document_id filter
            if document_id is not None:
                doc = self._find_document_by_id(data, document_id, id_field)
                if doc is None:
                    return None
                
                # Apply path extraction if needed
                if path:
                    return self._apply_path(doc, path)
                
                return doc
            
            # Apply path extraction (at collection level)
            if path:
                data = self._apply_path(data, path)
                if data is None:
                    return None
            
            # Apply query filters
            if query:
                filtered_result = self._apply_query_filter(data, query)
                data = filtered_result.get("data", data)
            
            # Return format based on request
            if format_type == 'records' and isinstance(data, dict):
                return list(data.values())
            else:
                return data
                
        except Exception as e:
            self._handle_error("read", e, collection=collection, document_id=document_id)
    
    def write(
        self,
        collection: str,
        data: Any,
        document_id: Optional[str] = None,
        mode: WriteMode = WriteMode.WRITE,
        path: Optional[str] = None,
        **kwargs
    ) -> StorageResult:
        """
        Write data to JSON file.
        
        Args:
            collection: JSON file name/path
            data: Data to write
            document_id: Document ID
            mode: Write mode (write, append, update, merge)
            path: Dot-notation path for nested updates
            **kwargs: Additional parameters
            
        Returns:
            StorageResult with operation details
        """
        try:
            file_path = self._get_file_path(collection)
            
            # Extract service-specific parameters
            id_field = kwargs.pop('id_field', 'id')
            
            file_existed = os.path.exists(file_path)
            
            if mode == WriteMode.WRITE:
                # Simple write operation (overwrite file)
                if document_id is not None:
                    # If document ID provided, create with initial structure
                    self._write_json_file(
                        file_path, 
                        self._create_initial_structure(data, document_id, id_field),
                        **kwargs
                    )
                else:
                    # Direct write
                    self._write_json_file(file_path, data, **kwargs)
                
                return self._create_success_result(
                    "write",
                    collection=collection,
                    file_path=file_path,
                    created_new=not file_existed
                )
            
            # Handle updating existing files
            current_data = None
            if file_existed:
                try:
                    current_data = self._read_json_file(file_path)
                except (FileNotFoundError, ValueError):
                    current_data = None
            
            # Use appropriate structure if file doesn't exist or has invalid data
            if current_data is None:
                if document_id is not None:
                    current_data = self._create_initial_structure(data, document_id, id_field)
                else:
                    current_data = [] if isinstance(data, list) else {}
            
            if mode == WriteMode.UPDATE:
                # Update operation
                if path:
                    # Path-based update
                    if document_id:
                        # Update path in specific document
                        doc = self._find_document_by_id(current_data, document_id, id_field)
                        if doc is None:
                            # Document not found, create it
                            new_doc = {id_field: document_id}
                            new_doc = self._update_path(new_doc, path, data)
                            current_data = self._add_document_to_structure(
                                current_data, new_doc, document_id, id_field
                            )
                        else:
                            # Update existing document
                            updated_doc = self._update_path(doc, path, data)
                            current_data = self._update_document_in_structure(
                                current_data, updated_doc, document_id, id_field
                            )[0]
                    else:
                        # Update path in entire file
                        current_data = self._update_path(current_data, path, data)
                else:
                    # Direct document update
                    if document_id is not None:
                        # Update specific document
                        current_data, created_new = self._update_document_in_structure(
                            current_data, data, document_id, id_field
                        )
                    else:
                        # Update entire file
                        current_data = data
                
                self._write_json_file(file_path, current_data, **kwargs)
                return self._create_success_result(
                    "update",
                    collection=collection,
                    file_path=file_path,
                    created_new=not file_existed
                )
            
            elif mode == WriteMode.APPEND:
                # Append operation
                if isinstance(current_data, list) and isinstance(data, list):
                    # Append to list
                    current_data.extend(data)
                elif isinstance(current_data, list):
                    # Append single item to list
                    current_data.append(data)
                elif isinstance(current_data, dict) and isinstance(data, dict):
                    # Merge dictionaries
                    current_data.update(data)
                elif document_id is not None:
                    # Add document with ID
                    current_data = self._add_document_to_structure(
                        current_data, data, document_id, id_field
                    )
                else:
                    # Can't append to incompatible structures
                    return self._create_error_result(
                        "append",
                        "Cannot append to incompatible data structure",
                        collection=collection
                    )
                
                self._write_json_file(file_path, current_data, **kwargs)
                return self._create_success_result(
                    "append",
                    collection=collection,
                    file_path=file_path
                )
            
            elif mode == WriteMode.MERGE:
                # Merge operation
                if path:
                    # Path-based merge
                    if document_id:
                        # Merge at path in specific document
                        doc = self._find_document_by_id(current_data, document_id, id_field)
                        if doc is None:
                            # Document not found, create it
                            new_doc = {id_field: document_id}
                            new_doc = self._update_path(new_doc, path, data)
                            current_data = self._add_document_to_structure(
                                current_data, new_doc, document_id, id_field
                            )
                        else:
                            # Get current value at path
                            current_value = self._apply_path(doc, path)
                            
                            # Merge if both are dictionaries
                            if isinstance(current_value, dict) and isinstance(data, dict):
                                merged_value = self._merge_documents(current_value, data)
                                updated_doc = self._update_path(doc, path, merged_value)
                                current_data = self._update_document_in_structure(
                                    current_data, updated_doc, document_id, id_field
                                )[0]
                            else:
                                # Otherwise, just update
                                updated_doc = self._update_path(doc, path, data)
                                current_data = self._update_document_in_structure(
                                    current_data, updated_doc, document_id, id_field
                                )[0]
                    else:
                        # Merge at path in entire file
                        current_value = self._apply_path(current_data, path)
                        
                        # Merge if both are dictionaries
                        if isinstance(current_value, dict) and isinstance(data, dict):
                            merged_value = self._merge_documents(current_value, data)
                            current_data = self._update_path(current_data, path, merged_value)
                        else:
                            # Otherwise, just update
                            current_data = self._update_path(current_data, path, data)
                else:
                    # Direct document merge
                    if document_id is not None:
                        # Merge specific document
                        doc = self._find_document_by_id(current_data, document_id, id_field)
                        if doc is None:
                            # Document not found, create it
                            current_data = self._add_document_to_structure(
                                current_data, data, document_id, id_field
                            )
                        else:
                            # Merge with existing document
                            if isinstance(doc, dict) and isinstance(data, dict):
                                merged_doc = self._merge_documents(doc, data)
                                current_data = self._update_document_in_structure(
                                    current_data, merged_doc, document_id, id_field
                                )[0]
                            else:
                                # Can't merge incompatible types, overwrite
                                current_data = self._update_document_in_structure(
                                    current_data, data, document_id, id_field
                                )[0]
                    else:
                        # Merge entire file
                        if isinstance(current_data, dict) and isinstance(data, dict):
                            current_data = self._merge_documents(current_data, data)
                        else:
                            # Can't merge incompatible types, overwrite
                            current_data = data
                
                self._write_json_file(file_path, current_data, **kwargs)
                return self._create_success_result(
                    "merge",
                    collection=collection,
                    file_path=file_path
                )
            
            else:
                return self._create_error_result(
                    "write",
                    f"Unsupported write mode: {mode}",
                    collection=collection
                )
                
        except Exception as e:
            self._handle_error("write", e, collection=collection, mode=mode.value)
    
    def delete(
        self,
        collection: str,
        document_id: Optional[str] = None,
        path: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> StorageResult:
        """
        Delete from JSON file.
        
        Args:
            collection: JSON file name/path
            document_id: Document ID to delete
            path: Dot-notation path to delete
            query: Query for batch delete
            **kwargs: Additional parameters
            
        Returns:
            StorageResult with operation details
        """
        try:
            file_path = self._get_file_path(collection)
            
            # Extract service-specific parameters
            id_field = kwargs.pop('id_field', 'id')
            
            if not os.path.exists(file_path):
                return self._create_error_result(
                    "delete",
                    f"File not found: {file_path}",
                    collection=collection
                )
            
            # Read current data
            current_data = self._read_json_file(file_path)
            if current_data is None:
                return self._create_error_result(
                    "delete",
                    f"Invalid JSON data in file: {file_path}",
                    collection=collection
                )
            
            # Handle deleting entire file
            if document_id is None and path is None and not query:
                os.remove(file_path)
                return self._create_success_result(
                    "delete",
                    collection=collection,
                    file_path=file_path,
                    file_deleted=True
                )
            
            # Handle deleting specific path
            if path:
                if document_id:
                    # Delete path in specific document
                    doc = self._find_document_by_id(current_data, document_id, id_field)
                    if doc is None:
                        return self._create_error_result(
                            "delete",
                            f"Document with ID '{document_id}' not found",
                            collection=collection,
                            document_id=document_id
                        )
                    
                    # Delete path in document
                    updated_doc = self._delete_path(doc, path)
                    current_data = self._update_document_in_structure(
                        current_data, updated_doc, document_id, id_field
                    )[0]
                else:
                    # Delete path in entire file
                    current_data = self._delete_path(current_data, path)
                
                self._write_json_file(file_path, current_data)
                return self._create_success_result(
                    "delete",
                    collection=collection,
                    file_path=file_path,
                    path=path
                )
            
            # Handle deleting document by ID
            if document_id is not None:
                deleted = False
                
                if isinstance(current_data, dict):
                    # Remove from dictionary
                    if document_id in current_data:
                        del current_data[document_id]
                        deleted = True
                    else:
                        # Look for document with matching ID field
                        keys_to_delete = []
                        for key, value in current_data.items():
                            if isinstance(value, dict) and value.get(id_field) == document_id:
                                keys_to_delete.append(key)
                                deleted = True
                        
                        for key in keys_to_delete:
                            del current_data[key]
                
                elif isinstance(current_data, list):
                    # Remove from list
                    original_length = len(current_data)
                    current_data = [
                        item for item in current_data 
                        if not (isinstance(item, dict) and item.get(id_field) == document_id)
                    ]
                    deleted = len(current_data) < original_length
                
                if not deleted:
                    return self._create_error_result(
                        "delete",
                        f"Document with ID '{document_id}' not found",
                        collection=collection,
                        document_id=document_id
                    )
                
                self._write_json_file(file_path, current_data)
                return self._create_success_result(
                    "delete",
                    collection=collection,
                    file_path=file_path,
                    document_id=document_id
                )
            
            # Handle batch delete with query
            if query and isinstance(current_data, list):
                original_length = len(current_data)
                
                # Apply query filters
                filtered_result = self._apply_query_filter(current_data, query)
                filtered_data = filtered_result.get("data", [])
                
                # Keep track of deleted documents
                deleted_ids = []
                for item in current_data:
                    if isinstance(item, dict) and item.get(id_field) and item not in filtered_data:
                        deleted_ids.append(item.get(id_field))
                
                # Write back the filtered data
                self._write_json_file(file_path, filtered_data)
                
                return self._create_success_result(
                    "delete",
                    collection=collection,
                    file_path=file_path,
                    total_affected=original_length - len(filtered_data),
                    deleted_ids=deleted_ids
                )
            
            return self._create_error_result(
                "delete",
                "Invalid delete operation",
                collection=collection
            )
            
        except Exception as e:
            self._handle_error("delete", e, collection=collection)
    
    def exists(
        self, 
        collection: str, 
        document_id: Optional[str] = None,
        path: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Check if JSON file, document, or path exists.
        
        Args:
            collection: JSON file name/path
            document_id: Document ID to check
            path: Dot-notation path to check
            **kwargs: Additional parameters
            
        Returns:
            True if exists, False otherwise
        """
        try:
            file_path = self._get_file_path(collection)
            
            if not os.path.exists(file_path):
                return False
            
            # Extract service-specific parameters
            id_field = kwargs.pop('id_field', 'id')
            
            # Check file existence only
            if document_id is None and path is None:
                return True
            
            # Read the file
            data = self._read_json_file(file_path)
            if data is None:
                return False
            
            # Check document existence
            if document_id is not None:
                doc = self._find_document_by_id(data, document_id, id_field)
                if doc is None:
                    return False
                
                # Check path in document
                if path:
                    value = self._apply_path(doc, path)
                    return value is not None
                
                return True
            
            # Check path existence in file
            if path:
                value = self._apply_path(data, path)
                return value is not None
            
            return True
            
        except Exception as e:
            self._logger.debug(f"Error checking existence: {e}")
            return False
    
    def count(
        self,
        collection: str,
        query: Optional[Dict[str, Any]] = None,
        path: Optional[str] = None,
        **kwargs
    ) -> int:
        """
        Count documents or items in JSON file.
        
        Args:
            collection: JSON file name/path
            query: Optional query parameters for filtering
            path: Optional path for nested counting
            **kwargs: Additional parameters
            
        Returns:
            Count of items
        """
        try:
            file_path = self._get_file_path(collection)
            
            if not os.path.exists(file_path):
                return 0
            
            # Read the file
            data = self._read_json_file(file_path)
            if data is None:
                return 0
            
            # Apply path extraction
            if path:
                data = self._apply_path(data, path)
                if data is None:
                    return 0
            
            # Apply query filtering
            if query:
                filtered_result = self._apply_query_filter(data, query)
                data = filtered_result.get("data", data)
                return filtered_result.get("count", 0)
            
            # Count based on data type
            if isinstance(data, list):
                return len(data)
            elif isinstance(data, dict):
                return len(data)
            else:
                return 1  # Scalar values count as 1
            
        except Exception as e:
            self._logger.debug(f"Error counting items: {e}")
            return 0
    
    def list_collections(self, **kwargs) -> List[str]:
        """
        List all JSON files in the base directory.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            List of JSON file names
        """
        try:
            base_dir = self.client["base_directory"]
            
            if not os.path.exists(base_dir):
                return []
            
            json_files = []
            for item in os.listdir(base_dir):
                if item.lower().endswith('.json'):
                    json_files.append(item)
            
            return sorted(json_files)
            
        except Exception as e:
            self._logger.debug(f"Error listing collections: {e}")
            return []
