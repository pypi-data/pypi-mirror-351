from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, 
    QDoubleSpinBox, QComboBox, QCheckBox, QPushButton, QScrollArea, 
    QTextEdit, QDateEdit, QTimeEdit, QDateTimeEdit, QFrame, QMessageBox,
    QStackedWidget, QListView
)
from PySide6.QtCore import Qt, QDate, QTime, QDateTime, Signal
from PySide6.QtGui import QRegularExpressionValidator, QStandardItem, QStandardItemModel
import json
import re
from typing import Any, Dict, List, Optional, Union, Callable
from urllib.parse import urlparse
import ipaddress
import email.utils
import os



class ValidationError(Exception):
    """Custom validation error class (not an Exception)"""
    def __init__(self, message: str, path: str = "", schema_path: str = ""):
        self.message = message
        self.path = path
        self.schema_path = schema_path
        
    def __str__(self):
        return self.message


class SchemaResolver:
    """
    Handles JSON Schema resolution including $ref, $defs, and recursive schemas.
    Supports Draft 2020-12 features.
    """
    
    def __init__(self, root_schema: Dict[str, Any]):
        self.root_schema = root_schema
        self.refs_cache = {}
        self.resolution_stack = []
        self.composition_depth = 0
        self.max_depth = 50
        self._creation_depth = 0
    
    def reset_creation_depth(self):
        """Reset the creation depth counter"""
        self._creation_depth = 0
        
    def resolve_schema(self, schema: Union[Dict[str, Any], bool], current_path: str = "#") -> Dict[str, Any]:
        """Enhanced resolution with depth tracking"""
        if len(self.resolution_stack) > self.max_depth:
            raise ValidationError(f"Maximum schema resolution depth exceeded at {current_path}")
        self.resolution_stack.append(current_path)

        try:
            if isinstance(schema, bool):
                return {"type": "object"} if schema else {"not": {}}

            if not isinstance(schema, dict):
                return {}

            if "$ref" in schema:
                return self._resolve_ref(schema["$ref"], current_path)

            resolved = dict(schema)

            # Handle composition keywords
            if "allOf" in schema:
                resolved = self._merge_all_of(schema["allOf"], resolved, current_path)

            if "oneOf" in schema:
                resolved["oneOf"] = [
                    self.resolve_schema(sub_schema, f"{current_path}/oneOf/{i}")
                    for i, sub_schema in enumerate(schema["oneOf"])
                ]

            if "anyOf" in schema:
                resolved["anyOf"] = [
                    self.resolve_schema(sub_schema, f"{current_path}/anyOf/{i}")
                    for i, sub_schema in enumerate(schema["anyOf"])
                ]

            if "items" in schema:
                resolved["items"] = self.resolve_schema(schema["items"], f"{current_path}/items")

            if "properties" in schema:
                resolved["properties"] = {
                    prop_name: self.resolve_schema(prop_schema, f"{current_path}/properties/{prop_name}")
                    for prop_name, prop_schema in schema["properties"].items()
                }

            return resolved
        finally:
            self.resolution_stack.pop()
        
    def _merge_all_of(self, all_of_schemas: List[Dict], base_schema: Dict, current_path: str) -> Dict[str, Any]:
        """Enhanced allOf merging with support for nested compositions"""
        result = dict(base_schema)
        
        # Remove allOf from result to avoid infinite loops
        if "allOf" in result:
            del result["allOf"]
        
        for i, sub_schema in enumerate(all_of_schemas):
            resolved_sub = self.resolve_schema(sub_schema, f"{current_path}/allOf/{i}")
            result = self._deep_merge_schemas(result, resolved_sub)
            
        return result
        
    def _deep_merge_schemas(self, schema1: Dict, schema2: Dict) -> Dict[str, Any]:
        """Enhanced schema merging with better composition handling"""
        result = dict(schema1)
        
        for key, value in schema2.items():
            if key in result:
                if key == "properties":
                    # Merge properties recursively
                    merged_props = dict(result[key])
                    for prop_name, prop_schema in value.items():
                        if prop_name in merged_props:
                            # If both have the same property, merge them with allOf
                            merged_props[prop_name] = {
                                "allOf": [merged_props[prop_name], prop_schema]
                            }
                        else:
                            merged_props[prop_name] = prop_schema
                    result[key] = merged_props
                elif key == "required":
                    # Union of required arrays
                    result[key] = list(set(result[key] + value))
                elif key in ["allOf", "anyOf", "oneOf"]:
                    # Combine composition arrays
                    result[key] = result[key] + value
                elif key == "items":
                    # For array items, use allOf to merge
                    result[key] = {"allOf": [result[key], value]}
                else:
                    # Override other properties
                    result[key] = value
            else:
                result[key] = value
                
        return result

    def _resolve_ref(self, ref: str, current_path: str) -> Dict[str, Any]:
        """
        Resolve a $ref reference in the schema.
        Supports internal references (e.g., #/definitions/...) and external references (e.g., file paths or URLs).
        """
        if ref in self.refs_cache:
            return self.refs_cache[ref]

        if ref in self.resolution_stack:
            # Circular reference detected, return a placeholder
            return {"$ref": ref}

        self.resolution_stack.append(ref)
        try:
            if ref.startswith("#"):
                # Internal reference
                resolved = self._resolve_internal_ref(ref)
            else:
                # External reference
                resolved = self._resolve_external_ref(ref)

            # Cache the resolved reference
            self.refs_cache[ref] = resolved
            return resolved
        finally:
            self.resolution_stack.pop()

    def _resolve_internal_ref(self, ref: str) -> Dict[str, Any]:
        """
        Resolve an internal reference (e.g., #/definitions/...).
        """
        parts = ref.lstrip("#/").split("/")
        schema = self.root_schema
        for part in parts:
            if not isinstance(schema, dict) or part not in schema:
                raise ValidationError(f"Invalid internal $ref: {ref}")
            schema = schema[part]
        return self.resolve_schema(schema, ref)

    def _resolve_external_ref(self, ref: str) -> Dict[str, Any]:
        """
        Resolve an external reference (e.g., file paths or URLs).
        """
        parsed_url = urlparse(ref)
        if parsed_url.scheme in ["http", "https"]:
            # Handle HTTP/HTTPS references
            return self._fetch_remote_schema(ref)
        elif os.path.isfile(parsed_url.path):
            # Handle file references
            return self._load_local_schema(parsed_url.path, parsed_url.fragment)
        else:
            raise ValidationError(f"Unsupported external $ref: {ref}")

    def _fetch_remote_schema(self, url: str) -> Dict[str, Any]:
        """
        Fetch a remote schema via HTTP/HTTPS.
        """
        import requests
        try:
            response = requests.get(url)
            response.raise_for_status()
            schema = response.json()
            return self.resolve_schema(schema, url)
        except Exception as e:
            raise ValidationError(f"Failed to fetch remote schema from {url}: {e}")

    def _load_local_schema(self, file_path: str, fragment: str) -> Dict[str, Any]:
        """
        Load a local schema from a file and resolve the fragment if provided.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            if fragment:
                return self._resolve_internal_ref(f"#{fragment}")
            return self.resolve_schema(schema, file_path)
        except Exception as e:
            raise ValidationError(f"Failed to load local schema from {file_path}: {e}")


class SchemaValidator:
    """
    Comprehensive JSON Schema Draft 2020-12 validator
    """
    
    # Format validators
    FORMAT_VALIDATORS = {
        'email': lambda v: email.utils.parseaddr(v)[1] != '',
        'uri': lambda v: urlparse(v).scheme != '',
        'uuid': lambda v: bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v, re.I)),
        'date': lambda v: bool(re.match(r'^\d{4}-\d{2}-\d{2}$', v)),
        'time': lambda v: bool(re.match(r'^\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)?$', v)),
        'date-time': lambda v: bool(re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)?$', v)),
        'ipv4': lambda v: bool(re.match(r'^(\d{1,3}\.){3}\d{1,3}$', v)) and all(0 <= int(x) <= 255 for x in v.split('.')),
        'ipv6': lambda v: SchemaValidator._validate_ipv6(v),
        'hostname': lambda v: bool(re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', v)),
    }
    
    def __init__(self, resolver: SchemaResolver):
        self.resolver = resolver
        
    @staticmethod
    def _validate_ipv6(value: str) -> bool:
        try:
            ipaddress.IPv6Address(value)
            return True
        except ipaddress.AddressValueError:
            return False
            
    def validate(self, data: Any, schema: Dict[str, Any], path: str = "") -> List[ValidationError]:
        errors = []

        try:
            if isinstance(schema, dict) and "if" in schema:
                # Skip resolving full schema — let conditional handler do it
                self._validate_conditional(data, schema, path, errors)
            else:
                resolved_schema = self.resolver.resolve_schema(schema)
                self._validate_value(data, resolved_schema, path, errors)
        except ValidationError as e:
            errors.append(ValidationError(str(e), path))

        return errors

    def _validate_value(self, data: Any, schema: Dict[str, Any], path: str, errors: List[ValidationError]):
        """Core validation logic"""
        
        # Handle type validation
        if "type" in schema:
            self._validate_type(data, schema["type"], path, errors)
            
        # Handle const
        if "const" in schema:
            if data != schema["const"]:
                errors.append(ValidationError(f"Value must be {schema['const']}", path))
                
        # Handle enum
        if "enum" in schema:
            if data not in schema["enum"]:
                errors.append(ValidationError(f"Value must be one of {schema['enum']}", path))
                
        # Type-specific validations
        if isinstance(data, str):
            self._validate_string(data, schema, path, errors)
        elif isinstance(data, (int, float)):
            self._validate_number(data, schema, path, errors)
        elif isinstance(data, list):
            self._validate_array(data, schema, path, errors)
        elif isinstance(data, dict):
            self._validate_object(data, schema, path, errors)
        
        # Conditional validation
        if "if" in schema:
            self._validate_conditional(data, schema, path, errors)

        # Handle composition keywords
        if "allOf" in schema:
            self._validate_all_of(data, schema["allOf"], path, errors)
        if "anyOf" in schema:
            self._validate_any_of(data, schema["anyOf"], path, errors)
        if "oneOf" in schema:
            self._validate_one_of(data, schema["oneOf"], path, errors)
        if "not" in schema:
            self._validate_not(data, schema["not"], path, errors)
            
    def _validate_type(self, data: Any, type_def: Union[str, List[str]], path: str, errors: List[ValidationError]):
        """Validate JSON Schema type"""
        valid_types = type_def if isinstance(type_def, list) else [type_def]
        
        type_map = {
            "null": type(None),
            "boolean": bool,
            "integer": int,
            "number": (int, float),
            "string": str,
            "array": list,
            "object": dict
        }
        
        for valid_type in valid_types:
            expected_type = type_map.get(valid_type)
            if expected_type and isinstance(data, expected_type):
                if valid_type == "integer" and isinstance(data, float) and not data.is_integer():
                    continue
                return
                
        errors.append(ValidationError(f"Expected type {type_def}, got {type(data).__name__}", path))
        
    def _validate_string(self, data: str, schema: Dict, path: str, errors: List[ValidationError]):
        """String-specific validation"""
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append(ValidationError(f"String too short (min: {schema['minLength']})", path))
            
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            errors.append(ValidationError(f"String too long (max: {schema['maxLength']})", path))
            
        if "pattern" in schema:
            if not re.search(schema["pattern"], data):
                errors.append(ValidationError(f"String does not match pattern: {schema['pattern']}", path))
                
        if "format" in schema:
            format_name = schema["format"]
            validator = self.FORMAT_VALIDATORS.get(format_name)
            if validator and not validator(data):
                errors.append(ValidationError(f"Invalid format: {format_name}", path))
                
    def _validate_number(self, data: Union[int, float], schema: Dict, path: str, errors: List[ValidationError]):
        """Number-specific validation"""
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(ValidationError(f"Number too small (min: {schema['minimum']})", path))
            
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(ValidationError(f"Number too large (max: {schema['maximum']})", path))
            
        if "exclusiveMinimum" in schema and data <= schema["exclusiveMinimum"]:
            errors.append(ValidationError(f"Number must be > {schema['exclusiveMinimum']}", path))
            
        if "exclusiveMaximum" in schema and data >= schema["exclusiveMaximum"]:
            errors.append(ValidationError(f"Number must be < {schema['exclusiveMaximum']}", path))
            
        if "multipleOf" in schema and data % schema["multipleOf"] != 0:
            errors.append(ValidationError(f"Number must be multiple of {schema['multipleOf']}", path))
            
    def _validate_array(self, data: List, schema: Dict, path: str, errors: List[ValidationError]):
        """Array-specific validation"""
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append(ValidationError(f"Array too short (min: {schema['minItems']})", path))
            
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            errors.append(ValidationError(f"Array too long (max: {schema['maxItems']})", path))
            
        if "uniqueItems" in schema and schema["uniqueItems"]:
            if len(data) != len(set(str(item) for item in data)):
                errors.append(ValidationError("Array items must be unique", path))
                
        # Validate items
        if "items" in schema:
            items_schema = schema["items"]
            for i, item in enumerate(data):
                self._validate_value(item, items_schema, f"{path}[{i}]", errors)
                
    def _validate_object(self, data: Dict, schema: Dict, path: str, errors: List[ValidationError]):
        """Object-specific validation with improved nested conditional handling"""
        if not isinstance(data, dict):
            errors.append(ValidationError(f"Expected object, got {type(data).__name__}", path))
            return

        # Track active schema and properties
        active_properties = {}
        active_required = set()

        # Handle conditional schema first
        if "if" in schema:
            temp_validator = SchemaValidator(self.resolver)
            condition_errors = temp_validator.validate(data, schema["if"])
            condition_met = not bool(condition_errors)
            
            # Select and apply active branch
            if condition_met and "then" in schema:
                active_branch = schema["then"]
            elif not condition_met and "else" in schema:
                active_branch = schema["else"]
            else:
                active_branch = {}

            # Update active properties and required fields
            if isinstance(active_branch, dict):
                active_properties.update(active_branch.get("properties", {}))
                active_required.update(active_branch.get("required", []))

        # Add base properties and required fields
        active_properties.update(schema.get("properties", {}))
        active_required.update(schema.get("required", []))

        # Validate only properties that are in the active schema
        for prop_name, prop_value in data.items():
            if prop_name in active_properties:
                prop_schema = active_properties[prop_name]
                prop_path = f"{path}.{prop_name}" if path else prop_name

                # Handle nested conditionals
                if "if" in prop_schema:
                    nested_validator = SchemaValidator(self.resolver)
                    nested_condition = nested_validator.validate(data, prop_schema["if"])
                    is_active = not bool(nested_condition)

                    # Validate against appropriate nested branch
                    if is_active and "then" in prop_schema:
                        self._validate_value(prop_value, prop_schema["then"], prop_path, errors)
                    elif not is_active and "else" in prop_schema:
                        self._validate_value(prop_value, prop_schema["else"], prop_path, errors)
                else:
                    self._validate_value(prop_value, prop_schema, prop_path, errors)

        # Only validate required fields from the active schema
        for prop_name in active_required:
            if prop_name not in data:
                prop_schema = active_properties.get(prop_name, {})
                # Skip if this is a conditional property that isn't active
                if "if" in prop_schema:
                    nested_validator = SchemaValidator(self.resolver)
                    nested_condition = nested_validator.validate(data, prop_schema["if"])
                    if bool(nested_condition):  # Skip if condition isn't met
                        continue
                errors.append(ValidationError(f"Required property '{prop_name}' is missing", path))

    def _validate_conditional(self, data: Any, schema: Dict[str, Any], path: str, errors: List[ValidationError]):
        """Handle if/then/else conditional validation correctly"""
        if_schema = schema["if"]
        then_schema = schema.get("then")
        else_schema = schema.get("else")

        # Check if 'if' schema passes (use a new resolver/validator to avoid mutation)
        condition_validator = SchemaValidator(self.resolver)
        condition_errors = condition_validator.validate(data, if_schema, path)

        # Apply only the active branch schema
        if not condition_errors and then_schema:
            self._validate_value(data, then_schema, path, errors)
        elif condition_errors and else_schema:
            self._validate_value(data, else_schema, path, errors)

    def _validate_all_of(self, data: Any, schemas: List[Dict], path: str, errors: List[ValidationError]):
        """Validate allOf - all schemas must pass"""
        for i, sub_schema in enumerate(schemas):
            sub_errors = self.validate(data, sub_schema, path)
            if sub_errors:
                errors.extend(sub_errors)
                
    def _validate_any_of(self, data: Any, schemas: List[Dict], path: str, errors: List[ValidationError]):
        """Validate anyOf - at least one schema must pass"""
        for sub_schema in schemas:
            sub_errors = self.validate(data, sub_schema, path)
            if not sub_errors:
                return  # Found valid schema
        errors.append(ValidationError("Value does not match any of the expected schemas", path))
        
    def _validate_one_of(self, data: Any, schemas: List[Dict], path: str, errors: List[ValidationError]):
        """Validate oneOf - exactly one schema must pass"""
        valid_count = 0
        for sub_schema in schemas:
            sub_errors = self.validate(data, sub_schema, path)
            if not sub_errors:
                valid_count += 1
                
        if valid_count == 0:
            errors.append(ValidationError("Value does not match any of the expected schemas", path))
        elif valid_count > 1:
            errors.append(ValidationError("Value matches more than one schema (oneOf violation)", path))
            
    def _validate_not(self, data: Any, schema: Dict, path: str, errors: List[ValidationError]):
        """Validate not - schema must not pass"""
        sub_errors = self.validate(data, schema, path)
        if not sub_errors:
            errors.append(ValidationError("Value matches forbidden schema", path))


class ErrorDisplayWidget(QWidget):
    """Widget to display validation errors"""
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.error_label = QLabel()
        self.error_label.setProperty("class", "error")
        self.error_label.setWordWrap(True)
        self.layout.addWidget(self.error_label)
        
        self.hide()
        
    def show_errors(self, errors: List[ValidationError]):
        if errors:
            error_text = "\n".join([f"• {error.message}" for error in errors[:5]])
            if len(errors) > 5:
                error_text += f"\n... and {len(errors) - 5} more errors"
            self.error_label.setText(error_text)
            if self.parent() is not None:
                self.show()
        else:
            self.hide()


class BaseFormWidget(QWidget):
    """Base class for all form widgets with validation support"""
    
    valueChanged = Signal()
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator, path: str = ""):
        super().__init__()
        self.schema = schema
        self.resolver = resolver
        self.validator = validator
        self.path = path
        self.errors = []
        
        # Create error display
        self.error_widget = ErrorDisplayWidget()
        
    def get_value(self) -> Any:
        """Get the current value from the widget"""
        raise NotImplementedError
        
    def set_value(self, value: Any):
        """Set the widget value"""
        raise NotImplementedError
        
    def validate_value(self) -> List[ValidationError]:
        """Validate current value against schema"""
        try:
            value = self.get_value()
            if value is None and self.schema.get("type") == "array":
                value = []
            return self.validator.validate(value, self.schema, self.path)
        except Exception as e:
            return [ValidationError(str(e), self.path)]
            
    def update_validation(self):
        """Update validation display"""
        self.errors = self.validate_value()
        self.error_widget.show_errors(self.errors)
        self.valueChanged.emit()


class MultiSelectComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(QStandardItemModel(self))
        self.setView(QListView())
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setPlaceholderText("Select options")
        self.model().dataChanged.connect(self.on_data_changed)

    def addItems(self, items):
        for item in items:
            if isinstance(item, tuple):
                text, value = item
            else:
                text = value = item
            std_item = QStandardItem(text)
            std_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            std_item.setData(value, Qt.UserRole)
            std_item.setCheckState(Qt.Unchecked)
            self.model().appendRow(std_item)

    def on_data_changed(self, topLeft, bottomRight, roles):
        if Qt.CheckStateRole in roles:
            self.update_text()

    def update_text(self):
        selected = [
            self.model().item(i).text()
            for i in range(self.model().rowCount())
            if self.model().item(i).checkState() == Qt.Checked
        ]
        self.lineEdit().setText(", ".join(selected))

    def get_selected_items(self):
        return [
            self.model().item(i).text()
            for i in range(self.model().rowCount())
            if self.model().item(i).checkState() == Qt.Checked
        ]

    def get_selected_values(self):
        return [
            self.model().item(i).data(Qt.UserRole)
            for i in range(self.model().rowCount())
            if self.model().item(i).checkState() == Qt.Checked
        ]

    def set_selected_items(self, selected_texts):
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            item.setCheckState(Qt.Checked if item.text() in selected_texts else Qt.Unchecked)
        self.update_text()

    def clear_selection(self):
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            item.setCheckState(Qt.Unchecked)
        self.update_text()


class StringWidget(BaseFormWidget):
    """Widget for string type with format support"""
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator, path: str = ""):
        super().__init__(schema, resolver, validator, path)
        
        layout = QVBoxLayout(self)
        
        if path:
            if "title" in schema:
                title_label = QLabel(schema["title"])
                title_label.setProperty("class", "title")
                layout.addWidget(title_label)
            if "description" in schema:
                desc_label = QLabel(schema["description"])
                desc_label.setProperty("class", "description")
                desc_label.setWordWrap(True)
                layout.addWidget(desc_label)

        # Determine widget type based on format
        format_type = schema.get("format", "")
        
        if format_type == "date":
            self.widget = QDateEdit()
            self.widget.setCalendarPopup(True)
            if "default" in schema:
                try:
                    default_date = QDate.fromString(str(schema["default"]), Qt.ISODate)
                    self.widget.setDate(default_date)
                except:
                    pass
        elif format_type == "time":
            self.widget = QTimeEdit()
            if "default" in schema:
                try:
                    default_time = QTime.fromString(str(schema["default"]), Qt.ISODate)
                    self.widget.setTime(default_time)
                except:
                    pass
        elif format_type == "date-time":
            self.widget = QDateTimeEdit()
            self.widget.setCalendarPopup(True)
            if "default" in schema:
                try:
                    default_datetime = QDateTime.fromString(str(schema["default"]), Qt.ISODate)
                    self.widget.setDateTime(default_datetime)
                except:
                    pass
        else:
            # Regular text input
            multiline = schema.get("maxLength", 0) > 100 or format_type in ["uri", "email"] and schema.get("maxLength", 0) > 50
            
            if multiline:
                self.widget = QTextEdit()
                self.widget.setMaximumHeight(100)
            else:
                self.widget = QLineEdit()
                
            if "default" in schema:
                if isinstance(self.widget, QTextEdit):
                    self.widget.setPlainText(str(schema["default"]))
                else:
                    self.widget.setText(str(schema["default"]))
                    
            # Set validation
            if "pattern" in schema:
                if isinstance(self.widget, QLineEdit):
                    validator = QRegularExpressionValidator()
                    validator.setRegularExpression(schema["pattern"])
                    self.widget.setValidator(validator)
                    
            # Set length constraints
            if isinstance(self.widget, QLineEdit):
                if "maxLength" in schema:
                    self.widget.setMaxLength(schema["maxLength"])
                    
        layout.addWidget(self.widget)
        layout.addWidget(self.error_widget)
        
        # Connect change signals
        if hasattr(self.widget, 'textChanged'):
            self.widget.textChanged.connect(self.update_validation)
        elif hasattr(self.widget, 'dateChanged'):
            self.widget.dateChanged.connect(self.update_validation)
        elif hasattr(self.widget, 'timeChanged'):
            self.widget.timeChanged.connect(self.update_validation)
        elif hasattr(self.widget, 'dateTimeChanged'):
            self.widget.dateTimeChanged.connect(self.update_validation)
            
    def get_value(self) -> str:
        if isinstance(self.widget, QTextEdit):
            return self.widget.toPlainText()
        elif isinstance(self.widget, QLineEdit):
            return self.widget.text()
        elif isinstance(self.widget, QDateEdit):
            return self.widget.date().toString(Qt.ISODate)
        elif isinstance(self.widget, QTimeEdit):
            return self.widget.time().toString(Qt.ISODate)
        elif isinstance(self.widget, QDateTimeEdit):
            return self.widget.dateTime().toString(Qt.ISODate)
        return ""
        
    def set_value(self, value: str):
        if isinstance(self.widget, QTextEdit):
            self.widget.setPlainText(str(value))
        elif isinstance(self.widget, QLineEdit):
            self.widget.setText(str(value))
        elif isinstance(self.widget, QDateEdit):
            date = QDate.fromString(str(value), Qt.ISODate)
            if date.isValid():
                self.widget.setDate(date)
        elif isinstance(self.widget, QTimeEdit):
            time = QTime.fromString(str(value), Qt.ISODate)
            if time.isValid():
                self.widget.setTime(time)
        elif isinstance(self.widget, QDateTimeEdit):
            datetime = QDateTime.fromString(str(value), Qt.ISODate)
            if datetime.isValid():
                self.widget.setDateTime(datetime)


class NumberWidget(BaseFormWidget):
    """Widget for number/integer types"""
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator, path: str = ""):
        super().__init__(schema, resolver, validator, path)
        
        layout = QVBoxLayout(self)

        if path:
            if "title" in schema:
                title_label = QLabel(schema["title"])
                title_label.setProperty("class", "title")
                layout.addWidget(title_label)
            if "description" in schema:
                desc_label = QLabel(schema["description"])
                desc_label.setProperty("class", "description")
                desc_label.setWordWrap(True)
                layout.addWidget(desc_label)
        
        is_integer = schema.get("type") == "integer"
        
        if is_integer:
            self.widget = QSpinBox()
            self.widget.setMinimum(schema.get("minimum", -2147483648))
            self.widget.setMaximum(schema.get("maximum", 2147483647))
        else:
            self.widget = QDoubleSpinBox()
            self.widget.setMinimum(schema.get("minimum", -1e9))
            self.widget.setMaximum(schema.get("maximum", 1e9))
            self.widget.setDecimals(6)
            
        if "default" in schema:
            self.widget.setValue(schema["default"])
            
        if "multipleOf" in schema:
            self.widget.setSingleStep(schema["multipleOf"])
            
        layout.addWidget(self.widget)
        layout.addWidget(self.error_widget)
        
        self.widget.valueChanged.connect(self.update_validation)
        
    def get_value(self) -> Union[int, float]:
        return self.widget.value()
        
    def set_value(self, value: Union[int, float]):
        self.widget.setValue(value)


class BooleanWidget(BaseFormWidget):
    """Widget for boolean type"""
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator, path: str = ""):
        super().__init__(schema, resolver, validator, path)
        
        layout = QVBoxLayout(self)

        if path:
            if "title" in schema:
                title_label = QLabel(schema["title"])
                title_label.setProperty("class", "title")
                layout.addWidget(title_label)
            if "description" in schema:
                desc_label = QLabel(schema["description"])
                desc_label.setProperty("class", "description")
                desc_label.setWordWrap(True)
                layout.addWidget(desc_label)
        
        self.widget = QCheckBox()
        if "default" in schema:
            self.widget.setChecked(bool(schema["default"]))
            
        layout.addWidget(self.widget)
        layout.addWidget(self.error_widget)
        
        self.widget.toggled.connect(self.update_validation)
        
    def get_value(self) -> bool:
        return self.widget.isChecked()
        
    def set_value(self, value: bool):
        self.widget.setChecked(bool(value))


class EnumWidget(BaseFormWidget):
    """Widget for enum constraints"""
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator, path: str = ""):
        super().__init__(schema, resolver, validator, path)
        
        layout = QVBoxLayout(self)

        if path:
            if "title" in schema:
                title_label = QLabel(schema["title"])
                title_label.setProperty("class", "title")
                layout.addWidget(title_label)
            if "description" in schema:
                desc_label = QLabel(schema["description"])
                desc_label.setProperty("class", "description")
                desc_label.setWordWrap(True)
                layout.addWidget(desc_label)
        
        self.widget = QComboBox()
        self.widget.setEditable(False)
        
        # Handle dynamic options from external dictionary
        options_dict_key = schema.get("enumSource")
        if options_dict_key and isinstance(options_dict_key, str):
            # Get options from the root schema's optionsData
            options_data = resolver.root_schema.get("optionsData", {})
            enum_options = options_data.get(options_dict_key, [])
            
            # Add items from the dynamic source
            for item in enum_options:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    # Handle (value, label) tuples
                    self.widget.addItem(str(item[1]), item[0])
                else:
                    # Handle simple values
                    self.widget.addItem(str(item), item)
        else:
            for item in schema.get("enum", []):
                self.widget.addItem(str(item), item)
            
        if "default" in schema:
            index = self.widget.findData(schema["default"])
            if index >= 0:
                self.widget.setCurrentIndex(index)
                
        layout.addWidget(self.widget)
        layout.addWidget(self.error_widget)
        
        self.widget.currentIndexChanged.connect(self.update_validation)
        
    def get_value(self) -> Any:
        return self.widget.currentData()
        
    def set_value(self, value: Any):
        index = self.widget.findData(value)
        if index >= 0:
            self.widget.setCurrentIndex(index)


class ConstWidget(BaseFormWidget):
    """Widget for const values"""
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator, path: str = ""):
        super().__init__(schema, resolver, validator, path)
        
        layout = QVBoxLayout(self)

        if path:
            if "title" in schema:
                title_label = QLabel(schema["title"])
                title_label.setProperty("class", "title")
                layout.addWidget(title_label)
            if "description" in schema:
                desc_label = QLabel(schema["description"])
                desc_label.setProperty("class", "description")
                desc_label.setWordWrap(True)
                layout.addWidget(desc_label)
        
        self.const_value = schema["const"]
        self.widget = QLabel(str(self.const_value))
        self.widget.setStyleSheet("color: gray; font-style: italic;")
        
        layout.addWidget(self.widget)
        layout.addWidget(self.error_widget)
        
    def get_value(self) -> Any:
        return self.const_value
        
    def set_value(self, value: Any):
        pass  # Const values cannot be changed


class ArrayWidget(BaseFormWidget):
    """Widget for array type with full Draft 2020-12 support"""
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator, path: str = ""):
        super().__init__(schema, resolver, validator, path)
        
        layout = QVBoxLayout(self)
        
        # Add title/description if specified
        if path:
            if "title" in schema:
                title_label = QLabel(schema["title"])
                title_label.setProperty("class", "title")
                layout.addWidget(title_label)
                
            if "description" in schema:
                desc_label = QLabel(schema["description"])
                desc_label.setProperty("class", "description")
                desc_label.setWordWrap(True)
                layout.addWidget(desc_label)

        self.items_schema = schema.get("items", {})
        self.min_items = schema.get("minItems", 0)
        self.max_items = schema.get("maxItems", float('inf'))
        self.item_widgets = []
        
        # Check if this is an enum array
        is_enum_array = "enum" in self.items_schema or "enumSource" in self.items_schema
        
        if is_enum_array:
            # Create multi-select combo for enum arrays
            self.widget = MultiSelectComboBox()
            
            # Handle dynamic options from external dictionary
            options_dict_key = self.items_schema.get("enumSource")
            if options_dict_key and isinstance(options_dict_key, str):
                # Get options from root schema's optionsData
                options_data = resolver.root_schema.get("optionsData", {})
                enum_options = options_data.get(options_dict_key, [])
                
                # Add items from dynamic source
                for item in enum_options:
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        # Handle (value, label) tuples
                        self.widget.addItems([(item[0], str(item[1]))])
                    else:
                        # Handle simple values
                        self.widget.addItems([str(item)])
            else:
                # Add static enum items
                enum_items = self.items_schema.get("enum", [])
                self.widget.addItems([str(item) for item in enum_items])
                    
            # Set default values if any
            if "default" in schema:
                default_values = schema["default"]
                if isinstance(default_values, list):
                    self.widget.set_selected_items([str(v) for v in default_values])
                
            # Connect to data changed signal
            self.widget.model().dataChanged.connect(self.update_validation)
            
            layout.addWidget(self.widget)
            
        else:
            # Header with controls
            header = QWidget()
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add button
            self.add_button = QPushButton("Add Item")
            self.add_button.clicked.connect(self.add_item)
            header_layout.addWidget(self.add_button)
            
            layout.addWidget(header)
            
            self.items_widget = QWidget()
            self.items_layout = QVBoxLayout(self.items_widget)
            self.items_layout.addStretch()
            
            layout.addWidget(self.item_widgets)
            
            self.item_widgets = []
            
            # Add default/initial items
            if "default" in schema:
                for item in schema["default"]:
                    self.add_item(item)
            elif self.min_items > 0:
                for _ in range(self.min_items):
                    self.add_item()
                    
            self.update_controls()
        
        layout.addWidget(self.error_widget)
        
    def add_item(self, value: Any = None):
        """Add a new item to the array"""
        if len(self.item_widgets) >= self.max_items:
            return
            
        # Container for item
        container = QWidget()
        container.setProperty("class", "array-item")
        item_layout = QHBoxLayout(container)
        
        # Index label
        index = len(self.item_widgets)
        index_label = QLabel(f"#{index + 1}")
        index_label.setProperty("class", "array-index")
        item_layout.addWidget(index_label)
        
        # Create item widget
        item_widget = SchemaWidgetFactory.create_widget(
            self.items_schema,
            self.resolver,
            self.validator,
            f"{self.path}[{index}]"
        )
        
        if value is not None:
            try:
                item_widget.set_value(value)
            except Exception as e:
                print(f"Error setting array item value: {e}")
                
        item_layout.addWidget(item_widget)
        
        # Remove button
        remove_button = QPushButton("×")
        remove_button.setProperty("class", "remove-button")
        remove_button.setMaximumWidth(30)
        remove_button.clicked.connect(lambda: self.remove_item(index))
        item_layout.addWidget(remove_button)
        
        # Insert before stretch
        self.items_layout.insertWidget(self.items_layout.count() - 1, container)
        self.item_widgets.append(item_widget)
        
        item_widget.valueChanged.connect(self.update_validation)
        self.update_controls()
        self.update_validation()
        
    def remove_item(self, index: int):
        """Remove an item from the array"""
        if index < 0 or index >= len(self.item_widgets):
            return
            
        if len(self.item_widgets) <= self.min_items:
            return
            
        # Remove widget
        container = self.item_widgets[index].parent()
        self.items_layout.removeWidget(container)
        container.deleteLater()
        
        # Remove from list
        del self.item_widgets[index]
        
        # Update remaining indices
        self.update_indices()
        self.update_controls()
        self.update_validation()
        
    def update_indices(self):
        """Update index labels and remove button connections"""
        for i, widget in enumerate(self.item_widgets):
            container = widget.parent()
            layout = container.layout()
            
            # Update index label
            index_label = layout.itemAt(0).widget()
            if isinstance(index_label, QLabel):
                index_label.setText(f"#{i + 1}")
            
            # Update remove button
            remove_button = layout.itemAt(2).widget()
            if isinstance(remove_button, QPushButton):
                remove_button.clicked.disconnect()
                remove_button.clicked.connect(lambda checked, idx=i: self.remove_item(idx))
    
    def update_controls(self):
        """Update button states based on constraints"""
        current_items = len(self.item_widgets)
        self.add_button.setEnabled(current_items < self.max_items)
        
        # Update remove buttons
        for widget in self.item_widgets:
            container = widget.parent()
            layout = container.layout()
            remove_button = layout.itemAt(2).widget()
            if isinstance(remove_button, QPushButton):
                remove_button.setEnabled(current_items > self.min_items)
    
    def get_value(self) -> List[Any]:
        """Get array values"""
        if hasattr(self, 'widget') and isinstance(self.widget, MultiSelectComboBox):
            return self.widget.get_selected_values()
            
        # Handle regular array items
        values = []
        for widget in self.item_widgets:
            if hasattr(widget, 'get_value'):
                try:
                    value = widget.get_value()
                    if value is not None:
                        values.append(value)
                except Exception as e:
                    print(f"Error getting array item value: {e}")
        return values

    def set_value(self, value: List[Any]):
        """Set array values"""
        if not isinstance(value, list):
            return
            
        if hasattr(self, 'widget') and isinstance(self.widget, MultiSelectComboBox):
            self.widget.set_selected_items([str(v) for v in value])
            return
            
        # Regular array handling
        while self.item_widgets:
            self.remove_item(0)
            
        for item in value:
            self.add_item(item)


class ObjectWidget(BaseFormWidget):
    """Widget for object type with full property support"""
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator, path: str = ""):
        super().__init__(schema, resolver, validator, path)
        
        self.property_widgets = {}
        self.conditional_widgets = []
        self._update_count = 0
        self.max_updates = 10
        
        layout = QVBoxLayout(self)
        
        # Create form for properties
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        if not properties:
            empty_label = QLabel("(No properties defined)")
            empty_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(empty_label)
        
        for prop_name, prop_schema in properties.items():
            is_pattern_key = re.fullmatch(r"\^.*\$", prop_name)

            if is_pattern_key:
                # Handle dynamic keys from actual data
                try:
                    existing_data = self.get_value()
                    print(f"[Debug] Fetched value for pattern object: {existing_data}")
                except Exception:
                    print(f"[Debug] Failed to get value")
                    existing_data = {}

                if not isinstance(existing_data, dict) or not existing_data:
                    print("[Debug] No data found for dynamic keys, skipping render.")
                    continue

                for dynamic_key, value in existing_data.items():
                    print(f"[Debug] Rendering dynamic key: {dynamic_key}")
                    prop_path = f"{path}.{dynamic_key}" if path else dynamic_key
                    label = QLabel(f"Effect: {dynamic_key}")
                    layout.addWidget(label)

                    def make_value_provider():
                        return lambda: self.get_value()

                    prop_widget = SchemaWidgetFactory.create_widget(
                        prop_schema, resolver, validator, prop_path,
                        parent_value_provider=make_value_provider()
                    )

                    prop_widget.set_value(value)
                    layout.addWidget(prop_widget)
                    self.property_widgets[dynamic_key] = prop_widget

                    if isinstance(prop_widget, ConditionalWidget):
                        self.conditional_widgets.append(prop_widget)

                    prop_widget.valueChanged.connect(self._on_property_changed)

                continue  # skip literal pattern key

            else:
                # Keep your existing else block untouched
                prop_path = f"{path}.{prop_name}" if path else prop_name
                show_label = "title" not in prop_schema and "description" not in prop_schema

                if show_label:
                    label_text = self._get_property_label(prop_name, prop_schema, prop_name in required)
                    label = QLabel(label_text)
                    if prop_name in required:
                        label.setProperty("class", "required")
                    layout.addWidget(label)

                def make_value_provider():
                    return lambda: self.get_value()

                prop_widget = SchemaWidgetFactory.create_widget(
                    prop_schema, resolver, validator, prop_path,
                    parent_value_provider=make_value_provider()
                )

                layout.addWidget(prop_widget)
                self.property_widgets[prop_name] = prop_widget

                if isinstance(prop_widget, ConditionalWidget):
                    self.conditional_widgets.append(prop_widget)

                prop_widget.valueChanged.connect(self._on_property_changed)

        
        # Set default values
        if "default" in schema and isinstance(schema["default"], dict):
            for prop_name, value in schema["default"].items():
                if prop_name in self.property_widgets:
                    self.property_widgets[prop_name].set_value(value)

    def _on_property_changed(self):
        """Handle property value changes with correct context for all conditionals"""
        if self._update_count >= self.max_updates:
            return

        self._update_count += 1
        try:
            # Always use the full current object value as parent context
            current_data = self.get_value()
            for conditional_widget in self.conditional_widgets:
                conditional_widget.update_condition(current_data)
        finally:
            self._update_count -= 1
            self.update_validation()

    def _get_safe_value(self, exclude_path: str) -> Dict[str, Any]:
        """Get value with improved nested handling"""
        if self._update_count >= self.max_updates:
            return {}
            
        self._update_count += 1
        try:
            result = {}
            # First collect all non-conditional values
            for prop_name, widget in self.property_widgets.items():
                if widget.path != exclude_path and not isinstance(widget, ConditionalWidget):
                    try:
                        value = widget.get_value()
                        if value is not None:
                            result[prop_name] = value
                    except Exception as e:
                        print(f"Error getting value for {prop_name}: {e}")
                        
            # Then handle conditionals in dependency order
            for widget in sorted(self.conditional_widgets, key=lambda w: len(w.path.split('.'))):
                if widget.path != exclude_path:
                    try:
                        value = widget.get_value()
                        if value is not None:
                            # Split path to handle nested properties
                            path_parts = widget.path.split('.')
                            current_dict = result
                            for part in path_parts[:-1]:
                                current_dict = current_dict.setdefault(part, {})
                            current_dict[path_parts[-1]] = value
                    except Exception as e:
                        print(f"Error getting conditional value for {widget.path}: {e}")
                        
            return result
        finally:
            self._update_count -= 1
    
    def _get_property_label(self, prop_name: str, prop_schema: Dict[str, Any], is_required: bool) -> str:
        """Generate a meaningful label for a property"""
        if "title" in prop_schema:
            label_text = prop_schema["title"]
        else:
            label_text = prop_name.replace('_', ' ').title()
        
        if is_required:
            label_text += " *"
        
        return label_text

    def _validate_object(self, data: Dict, schema: Dict, path: str, errors: List[ValidationError]):
        # Track active schema and properties
        active_properties = {}
        active_required = set()

        # Only validate required fields from the active schema
        for prop_name in active_required:
            if prop_name not in data:
                prop_schema = active_properties.get(prop_name, {})
                # Skip if this is a conditional property that isn't active
                if "if" in prop_schema:
                    nested_validator = SchemaValidator(self.resolver)
                    nested_condition = nested_validator.validate(data, prop_schema["if"])
                    if bool(nested_condition):  # Skip if condition isn't met
                        continue
                # Add to errors list instead of raising
                errors.append(ValidationError(f"Required property '{prop_name}' is missing", path))

    def get_value(self) -> Dict[str, Any]:
            result = {}
            for prop_name, widget in self.property_widgets.items():
                if widget is None or not hasattr(widget, 'get_value'):
                    continue
                    
                try:
                    # Check if widget is properly initialized
                    if not widget.isVisible() and isinstance(widget, (OneOfWidget, AnyOfWidget)):
                        continue
                        
                    value = widget.get_value()
                    if value is not None:
                        # Filter keys that are actually in the current schema
                        if prop_name in self.schema.get("properties", {}):
                            prop_schema = self.schema["properties"][prop_name]

                            # Handle conditional schemas
                            if "if" in prop_schema and isinstance(widget, ConditionalWidget):
                                try:
                                    active_value = value
                                    allowed_keys = set(widget._current_schema.get("properties", {}).keys()) if widget._current_schema else set()
                                    if isinstance(active_value, dict):
                                        active_value = {k: v for k, v in active_value.items() if k in allowed_keys}
                                    result[prop_name] = active_value
                                except Exception:
                                    pass
                            else:
                                result[prop_name] = value
                except Exception:
                    pass
                    
            if not result and "default" in self.schema:
                return self.schema["default"]
            return result

    
    def set_value(self, value: Dict[str, Any]):
        if not isinstance(value, dict):
            return
            
        for prop_name, prop_value in value.items():
            if prop_name in self.property_widgets:
                try:
                    self.property_widgets[prop_name].set_value(prop_value)
                except Exception as e:
                    print(f"Error setting value for {prop_name}: {e}")
        
        # After setting values
        self.schema = self.resolver.resolve_schema(self.schema)

        # Update conditionals after setting values
        current_data = self.get_value()
        for conditional_widget in self.conditional_widgets:
            conditional_widget.update_condition(current_data)


class OneOfWidget(BaseFormWidget):
    """Widget for oneOf schema composition with lazy widget creation"""
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator, path: str = ""):
        super().__init__(schema, resolver, validator, path)
        
        self.options = schema["oneOf"]
        self.current_widget = None
        self.current_index = -1
        
        layout = QVBoxLayout(self)

        # Add title/description
        if path:
            if "title" in schema:
                title_label = QLabel(schema["title"])
                title_label.setProperty("class", "title")
                layout.addWidget(title_label)
            if "description" in schema:
                desc_label = QLabel(schema["description"])
                desc_label.setProperty("class", "description")
                desc_label.setWordWrap(True)
                layout.addWidget(desc_label)
        
        # Create selector
        self.selector = QComboBox()
        for i, option in enumerate(self.options):
            title = self._generate_option_title(option, i)
            self.selector.addItem(title)
        
        layout.addWidget(QLabel("Select Option:"))
        layout.addWidget(self.selector)
        
        # Container for the current widget
        self.widget_container = QWidget()
        self.widget_layout = QVBoxLayout(self.widget_container)
        layout.addWidget(self.widget_container)
        
        layout.addWidget(self.error_widget)
        
        self.selector.currentIndexChanged.connect(self.on_selection_changed)
        
    def on_selection_changed(self, index: int):
        """Create and show widget only when option is selected"""
        if index == self.current_index:
            return
            
        self.current_index = index
        
        # Clean up previous widget
        if self.current_widget:
            self.widget_layout.removeWidget(self.current_widget)
            self.current_widget.setParent(None)
            self.current_widget.deleteLater()
            self.current_widget = None
            
        # Create new widget only if a valid option is selected
        if 0 <= index < len(self.options):
            option_schema = self.options[index]
            self.current_widget = SchemaWidgetFactory.create_widget(
                option_schema, 
                self.resolver,
                self.validator,
                f"{self.path}/oneOf[{index}]",
                parent_value_provider=lambda: self._get_parent_context()
            )
            self.widget_layout.addWidget(self.current_widget)
            self.current_widget.valueChanged.connect(self.update_validation)
            
        self.update_validation()
    
    def _generate_option_title(self, option: Dict[str, Any], index: int) -> str:
        """Generate enhanced option titles"""
        if "title" in option:
            return option["title"]
        
        if "const" in option:
            return f"Constant: {option['const']}"
        
        if "oneOf" in option:
            return f"Choice of {len(option['oneOf'])} options"
        
        if "anyOf" in option:
            return f"Any of {len(option['anyOf'])} options"
        
        if "allOf" in option:
            return f"Combined schema"
        
        if "if" in option:
            return f"Conditional schema"
        
        if "properties" in option and option.get("type") == "object":
            props = list(option["properties"].keys())
            if len(props) <= 3:
                prop_str = ", ".join(props)
                return f"Object ({prop_str})"
            return f"Object ({len(props)} properties)"
        
        if "items" in option and option.get("type") == "array":
            items_schema = option["items"]
            if "type" in items_schema:
                return f"Array of {items_schema['type']}"
            return "Array"
        
        if "type" in option:
            return f"Type: {option['type']}"
        
        return f"Option {index + 1}"
    
    def _get_parent_context(self) -> Dict[str, Any]:
        """Get context for nested conditionals"""
        try:
            return {"selectedOption": self.selector.currentIndex()}
        except:
            return {}
    
    def get_value(self) -> Any:
        """Get value from current widget"""
        if self.current_widget:
            try:
                value = self.current_widget.get_value()
                if isinstance(value, dict) and 0 <= self.current_index < len(self.options):
                    schema_option = self.options[self.current_index]
                    if "properties" in schema_option and "type" in schema_option["properties"]:
                        type_value = schema_option["properties"]["type"].get("const")
                        if type_value:
                            value["type"] = type_value
                return value
            except Exception as e:
                print(f"Error getting oneOf value: {e}")
        return None
    
    def set_value(self, value: Any):
        """Set value with lazy widget creation"""
        best_match_index = -1
        best_match_score = float('inf')
        
        # Find best matching option
        for i, option_schema in enumerate(self.options):
            try:
                errors = self.validator.validate(value, option_schema)
                error_score = len(errors)
                
                if error_score < best_match_score:
                    best_match_score = error_score
                    best_match_index = i
                    
                if error_score == 0:
                    break
            except:
                continue
        
        # Set the best matching option
        if best_match_index >= 0:
            self.selector.setCurrentIndex(best_match_index)
            # Widget will be created by on_selection_changed
            if self.current_widget:
                self.current_widget.set_value(value)


class AnyOfWidget(BaseFormWidget):
    """Widget for anyOf schema composition"""
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator, path: str = ""):
        super().__init__(schema, resolver, validator, path)
        
        self.option_widgets = []
        self.checkboxes = []
        
        layout = QVBoxLayout(self)

        if path:
            if "title" in schema:
                title_label = QLabel(schema["title"])
                title_label.setProperty("class", "title")
                layout.addWidget(title_label)
            if "description" in schema:
                desc_label = QLabel(schema["description"])
                desc_label.setProperty("class", "description")
                desc_label.setWordWrap(True)
                layout.addWidget(desc_label)

        layout.addWidget(QLabel("Select one or more options:"))
        
        options = schema["anyOf"]
        for i, option in enumerate(options):
            # Better title generation
            title = option.get("title", f"Option {i + 1}")
            
            if "const" in option:
                title = f"Constant: {option['const']}"
            elif option.get("type") == "object":
                if "properties" in option:
                    props = list(option["properties"].keys())
                    if len(props) == 1:
                        title = props[0].replace("_", " ").title()
                    elif "email" in props:
                        title = "Email Contact"
                    elif "phone" in props:
                        title = "Phone Contact"
                    else:
                        title = f"Contact Info ({', '.join(props)})"
            elif "type" in option:
                title = option["type"].title()
                
            checkbox = QCheckBox(title)
            option_widget = SchemaWidgetFactory.create_widget(
                option, self.resolver, self.validator, f"{path}/anyOf[{i}]",
                parent_value_provider=lambda: self.get_value()
            )
            
            # Initially hidden
            option_widget.setVisible(False)
            
            self.checkboxes.append(checkbox)
            self.option_widgets.append(option_widget)
            
            layout.addWidget(checkbox)
            layout.addWidget(option_widget)
            
            checkbox.toggled.connect(option_widget.setVisible)
            checkbox.toggled.connect(self.update_validation)
            option_widget.valueChanged.connect(self.update_validation)
            
        layout.addWidget(self.error_widget)
    
    def _get_option_title(self, option: Dict[str, Any], index: int) -> str:
        """Generate a meaningful title for an option"""
        if "title" in option:
            return option["title"]
        
        if "const" in option:
            return f"Constant: {option['const']}"
        
        if "properties" in option and option.get("type") == "object":
            # List key properties
            props = list(option["properties"].keys())[:3]  # First 3 properties
            prop_str = ", ".join(props)
            if len(option["properties"]) > 3:
                prop_str += "..."
            return f"Object ({prop_str})"
        
        if "type" in option:
            return f"Type: {option['type']}"
        
        return f"Option {index + 1}"
        
    def get_value(self) -> Any:
        """Return value from the first enabled option (not a list)"""
        for i, (checkbox, widget) in enumerate(zip(self.checkboxes, self.option_widgets)):
            if checkbox.isChecked():
                return widget.get_value()
        return None
        
    def set_value(self, value: Any):
        # Try to find which option matches the value
        for i, widget in enumerate(self.option_widgets):
            try:
                widget.set_value(value)
                errors = widget.validate_value()
                if not errors:
                    self.checkboxes[i].setChecked(True)
                    return
            except:
                continue


class AllOfWidget(BaseFormWidget):
    """Widget for allOf schema composition"""
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator, path: str = ""):
        super().__init__(schema, resolver, validator, path)
        
        layout = QVBoxLayout(self)

        if path:
            if "title" in schema:
                title_label = QLabel(schema["title"])
                title_label.setProperty("class", "title")
                layout.addWidget(title_label)
            if "description" in schema:
                desc_label = QLabel(schema["description"])
                desc_label.setProperty("class", "description")
                desc_label.setWordWrap(True)
                layout.addWidget(desc_label)
        
        # Check if any of the allOf schemas contain oneOf/anyOf
        self.has_nested_compositions = any(
            any(key in sub_schema for key in ["oneOf", "anyOf", "if"])
            for sub_schema in schema.get("allOf", [])
        )
        
        if self.has_nested_compositions:
            # Handle complex allOf with nested compositions
            self._create_complex_allof_widget(schema, layout)
        else:
            # Simple allOf - merge schemas and create single widget
            merged_schema = self.resolver.resolve_schema(schema)
            self.merged_widget = SchemaWidgetFactory.create_widget(
                merged_schema, self.resolver, self.validator, path
            )
            layout.addWidget(self.merged_widget)
            self.merged_widget.valueChanged.connect(self.update_validation)
        
        layout.addWidget(self.error_widget)
    
    def _create_complex_allof_widget(self, schema: Dict[str, Any], layout: QVBoxLayout):
        """Create widget for allOf with nested compositions"""
        self.sub_widgets = []
        all_of_schemas = schema["allOf"]
        
        # Create a container for all sub-widgets
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Create widgets for each allOf schema
        for i, sub_schema in enumerate(all_of_schemas):
            sub_path = f"{self.path}/allOf[{i}]"
            
            # Add separator for visual clarity
            if i > 0:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setProperty("class", "allof-separator")
                container_layout.addWidget(separator)
            
            # Create widget for this sub-schema
            sub_widget = SchemaWidgetFactory.create_widget(
                sub_schema, self.resolver, self.validator, sub_path,
                parent_value_provider=lambda: self.get_combined_value()
            )
            
            container_layout.addWidget(sub_widget)
            self.sub_widgets.append(sub_widget)
            sub_widget.valueChanged.connect(self._on_sub_widget_changed)
        
        layout.addWidget(container)
        self.merged_widget = None  # Not used in complex mode
    
    def _on_sub_widget_changed(self):
        """Handle changes in sub-widgets"""
        # Update other sub-widgets that might have conditionals
        combined_value = self.get_combined_value()
        
        for widget in self.sub_widgets:
            if isinstance(widget, ConditionalWidget):
                widget.update_condition(combined_value)
        
        self.update_validation()
    
    def get_combined_value(self) -> Dict[str, Any]:
        """Get combined value from all sub-widgets"""
        if hasattr(self, 'sub_widgets'):
            combined = {}
            for widget in self.sub_widgets:
                try:
                    value = widget.get_value()
                    if isinstance(value, dict):
                        combined.update(value)
                except:
                    pass
            return combined
        return {}
    
    def get_value(self) -> Any:
        if self.merged_widget:
            return self.merged_widget.get_value()
        else:
            return self.get_combined_value()
    
    def set_value(self, value: Any):
        if self.merged_widget:
            self.merged_widget.set_value(value)
        else:
            # Set value on all sub-widgets
            for widget in self.sub_widgets:
                try:
                    widget.set_value(value)
                except:
                    pass


class ConditionalWidget(BaseFormWidget):
    """Enhanced conditional widget with deep nesting support"""
    
    def __init__(self, schema: Dict[str, Any], resolver: SchemaResolver, validator: SchemaValidator,
                 path: str = "", parent_value_provider: Optional[Callable[[], Any]] = None):
        super().__init__(schema, resolver, validator, path)
        
        # Add nesting depth tracking first
        self._nesting_depth = getattr(resolver, '_creation_depth', 0)
        self.max_nesting = 20

        # Initialize state tracking with better defaults
        self._last_condition_result = None
        self._last_parent_data = None  # Changed from {} to None
        self._current_value = None
        self._is_updating = False
        self._update_count = 0
        self.max_updates = 10
        self._schema_state = None  # Add schema state tracking
        
        # Schema handling
        self.if_schema = schema.get("if", {})
        self.then_schema = schema.get("then", {})
        self.else_schema = schema.get("else", {})
        self._parent_value_provider = parent_value_provider
        
        self.layout = QVBoxLayout(self)
        self.active_widget = None
        self._current_schema = None
        
        # Start with default widget
        self._create_default_widget()

    def _get_parent_value(self) -> Any:
        """Safely get parent value with recursion protection"""
        if self._parent_value_provider and self._update_count < self.max_updates:
            self._update_count += 1
            try:
                return self._parent_value_provider()
            except Exception as e:
                print(f"Error getting parent value: {e}")
            finally:
                self._update_count -= 1
        return None

    def _create_default_widget(self):
        """Create initial widget with better schema selection"""
        # Choose the most appropriate default schema
        default_schema = self.then_schema if self.then_schema else self.else_schema
        if not default_schema:
            default_schema = {"type": "string", "title": "Conditional Field"}
            
        self._create_widget_for_schema(default_schema)
    
    def _select_target_schema(self, condition_met: Optional[bool]) -> Dict[str, Any]:
        """Select appropriate schema based on condition result"""
        # Add empty default schemas if not provided
        if condition_met and self.then_schema:
            return self.then_schema
        elif condition_met is False and self.else_schema:
            return self.else_schema
        elif condition_met and not self.then_schema:
            return {"type": "object", "properties": {}}  # Empty schema if no 'then' branch
        elif condition_met is False and not self.else_schema:
            return {"type": "object", "properties": {}}  # Empty schema if no 'else' branch
        return self.then_schema if self.then_schema else self.else_schema

    def _evaluate_condition(self, data: Any) -> Optional[bool]:
        """Improved condition evaluation with better missing field handling"""
        if not self.if_schema:
            return True
            
        try:
            # Ensure we have a dict to work with
            eval_data = data.copy() if isinstance(data, dict) else {"value": data}
            
            # Handle missing required fields
            if "required" in self.if_schema:
                required_fields = self.if_schema["required"]
                missing_fields = [f for f in required_fields if f not in eval_data]
                if missing_fields:
                    return False  # Changed from None to False for clearer state handling
            
            # Validate against if schema
            temp_validator = SchemaValidator(self.resolver)
            validation_errors = temp_validator.validate(eval_data, self.if_schema)
            return len(validation_errors) == 0
            
        except Exception as e:
            print(f"Error evaluating condition at {self.path}: {e}")
            return False  # Changed from None to False for clearer state handling
        
    def validate_value(self) -> List[ValidationError]:
        """Override validation to only validate the active schema"""
        try:
            value = self.get_value()
            
            # Only validate against the current active schema
            if self._current_schema:
                return self.validator.validate(value, self._current_schema, self.path)
            return []
            
        except Exception as e:
            return [ValidationError(str(e), self.path)]

    def update_condition(self, parent_data: Any = None):
        """Enhanced condition update with better state management"""
        if self._is_updating or self._update_count >= self.max_updates:
            return

        self._is_updating = True
        self._update_count += 1

        try:
            if parent_data is None:
                parent_data = self._get_parent_value() or {}

            current_data = dict(parent_data) if isinstance(parent_data, dict) else {"value": parent_data}

            # Compare states using schema-aware comparison
            current_state = self._get_state_hash(current_data)
            if current_state == self._schema_state:
                return

            self._schema_state = current_state
            self._last_parent_data = current_data

            # Evaluate condition with improved handling
            condition_met = self._evaluate_condition(current_data)
            if condition_met != self._last_condition_result:
                self._last_condition_result = condition_met
                target_schema = self._select_target_schema(condition_met)
                # Preserve the previous value, if any
                old_value = self.get_value()

                if target_schema != self._current_schema:
                    self._current_schema = target_schema
                    self._create_widget_for_schema(target_schema)
                    try:
                        # Check if old_value validates with the new schema
                        new_errors = self.validator.validate(old_value, target_schema, self.path) if old_value is not None else ["No value"]
                        if old_value is not None and not new_errors:
                            self.active_widget.set_value(old_value)
                        else:
                            # Clear value (or you can supply a default) if it doesn't conform
                            self.active_widget.set_value("")
                    except Exception as e:
                        print(f"Error during schema switch/set_value at {self.path}: {e}")
                print(f"Switching schema at {self.path}: condition_met={condition_met}")

        except Exception as e:
            print(f"Exception in update_condition at {self.path}: {e}")
        finally:
            self._is_updating = False
            self._update_count -= 1
            self.update_validation()

    def _create_widget_for_schema(self, schema: Dict[str, Any]):
        """Create widget with better cleanup"""
        # Clean up old widget
        if self.active_widget:
            self.layout.removeWidget(self.active_widget)
            self.active_widget.setParent(None)
            self.active_widget.deleteLater()
            self.active_widget = None
        
        try:
            # Create new widget with nesting depth check
            if self._nesting_depth > self.max_nesting:
                self.active_widget = ConstWidget(
                    {"const": "Maximum nesting depth exceeded"},
                    self.resolver,
                    self.validator,
                    self.path
                )
            else:
                self.active_widget = SchemaWidgetFactory.create_widget(
                    schema,
                    self.resolver,
                    self.validator,
                    self.path,
                    parent_value_provider=self._parent_value_provider
                )
            
            self.layout.addWidget(self.active_widget)
            
            # Connect change signal
            if hasattr(self.active_widget, 'valueChanged'):
                self.active_widget.valueChanged.connect(self.update_validation)
                
        except Exception as e:
            print(f"Error creating conditional widget: {e}")
            self.active_widget = None
    
    def _get_state_hash(self, data: Any) -> str:
        """Generate a stable hash of the current state"""
        try:
            # Only include relevant fields for condition
            if isinstance(data, dict) and self.if_schema.get("required"):
                filtered_data = {
                    k: v for k, v in data.items() 
                    if k in self.if_schema["required"]
                }
                return json.dumps(filtered_data, sort_keys=True)
            return json.dumps(data, sort_keys=True)
        except:
            return str(data)

    def get_value(self) -> Any:
        """Get value with state caching"""
        if self.active_widget and hasattr(self.active_widget, "get_value"):
            try:
                self._current_value = self.active_widget.get_value()
                return self._current_value
            except Exception as e:
                print(f"Error getting conditional value at {self.path}: {e}")
        return self._current_value
    
    def set_value(self, value: Any):
        """Set value with state tracking"""
        if self.active_widget and hasattr(self.active_widget, "set_value"):
            try:
                self._current_value = value
                self.active_widget.set_value(value)
            except Exception as e:
                print(f"Error setting conditional value at {self.path}: {e}")


class SchemaWidgetFactory:
    """
    Enhanced factory for creating widgets from JSON Schema definitions
    Supports full Draft 2020-12 specification
    """
    
    @staticmethod
    def create_widget(schema: Dict[str, Any], resolver: SchemaResolver, 
                    validator: SchemaValidator, path: str = "", 
                    parent_value_provider: Optional[Callable[[], Any]] = None) -> BaseFormWidget:
        """Create appropriate widget for schema with better error handling"""
        
        try:
            # Reset creation depth at top level
            if not path:
                resolver.reset_creation_depth()
            
            # Track creation depth
            resolver._creation_depth += 1
            if resolver._creation_depth > 20:
                return ConstWidget(
                    {"const": "Maximum widget creation depth exceeded"},
                    resolver,
                    validator,
                    path
                )
            
            # Handle boolean schemas
            if isinstance(schema, bool):
                schema = {"type": "object"} if schema else {"not": {}}
                
            if not isinstance(schema, dict):
                return ConstWidget({"const": "Invalid schema"}, resolver, validator, path)
            
            # Handle if/then/else conditionals FIRST (highest priority)
            if "if" in schema:
                return ConditionalWidget(schema, resolver, validator, path, parent_value_provider)
            
            # Resolve schema for other cases
            resolved_schema = resolver.resolve_schema(schema)
            
            # Handle const
            if "const" in resolved_schema:
                return ConstWidget(resolved_schema, resolver, validator, path)
                
            # Handle enum
            if "enum" in resolved_schema:
                return EnumWidget(resolved_schema, resolver, validator, path)
                
            # Handle composition keywords BEFORE type resolution
            # Use original schema to preserve composition structure
            if "oneOf" in schema:
                print(f"Creating OneOfWidget for schema at {path}")
                return OneOfWidget(schema, resolver, validator, path)
                
            if "anyOf" in schema:
                return AnyOfWidget(schema, resolver, validator, path)
                
            if "allOf" in schema:
                return AllOfWidget(schema, resolver, validator, path)
                
            # Handle type-based widgets
            schema_type = resolved_schema.get("type")
            
            if schema_type == "string":
                return StringWidget(resolved_schema, resolver, validator, path)
            elif schema_type in ["integer", "number"]:
                return NumberWidget(resolved_schema, resolver, validator, path)
            elif schema_type == "boolean":
                return BooleanWidget(resolved_schema, resolver, validator, path)
            elif schema_type == "array":
                return ArrayWidget(resolved_schema, resolver, validator, path)
            elif schema_type == "object":
                return ObjectWidget(resolved_schema, resolver, validator, path)
            elif schema_type == "null":
                return ConstWidget({"const": None}, resolver, validator, path)
                
            # Handle multiple types
            if isinstance(schema_type, list):
                type_schemas = []
                for t in schema_type:
                    type_schema = dict(resolved_schema)
                    type_schema["type"] = t
                    type_schemas.append(type_schema)
                multi_type_schema = {"oneOf": type_schemas}
                return OneOfWidget(multi_type_schema, resolver, validator, path)
            
            # Better fallback for schemas without explicit type
            if not schema_type:
                # Try to infer from other properties
                if "properties" in resolved_schema:
                    inferred_schema = dict(resolved_schema)
                    inferred_schema["type"] = "object"
                    return ObjectWidget(inferred_schema, resolver, validator, path)
                elif "items" in resolved_schema:
                    inferred_schema = dict(resolved_schema)
                    inferred_schema["type"] = "array"
                    return ArrayWidget(inferred_schema, resolver, validator, path)
                elif "enum" in resolved_schema:
                    return EnumWidget(resolved_schema, resolver, validator, path)
                else:
                    # Default to string input
                    return StringWidget({"type": "string"}, resolver, validator, path)
                    
        except Exception as e:
            print(f"Error creating widget for schema at {path}: {e}")
            error_schema = {"const": f"Schema Error: {str(e)}"}
            return ConstWidget(error_schema, resolver, validator, path)
        finally:
            # Always decrease creation depth when exiting
            resolver._creation_depth -= 1
        
        # Final fallback - should rarely reach here now
        return StringWidget({"type": "string", "title": "Unknown Schema"}, resolver, validator, path)


class JsonSchemaForm(QWidget):
    """
    Main JSON Schema form with full Draft 2020-12 support
    """
    
    def __init__(self, schema: Dict[str, Any], data: Dict[str, any] = None, title: str = "JSON Schema Form", toolbar: bool = False):
        super().__init__()
        
        self.setWindowTitle(title)
        self.setMinimumSize(800, 600)

        # Store Data Dictionary
        if data is not None:
            schema["optionsData"] = data
        
        # Initialize components
        self.resolver = SchemaResolver(schema)
        self.validator = SchemaValidator(self.resolver)
        
        # Main layout with better spacing
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        if "title" in schema:
            title_label = QLabel(schema["title"])
            title_label.setProperty("class", "title")
            layout.addWidget(title_label)
            
        # Description
        if "description" in schema:
            desc_label = QLabel(schema["description"])
            desc_label.setProperty("class", "description")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
            
        # Form widget in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        
        self.form_widget = SchemaWidgetFactory.create_widget(
            schema, self.resolver, self.validator
        )
        form_layout.addWidget(self.form_widget)
        form_layout.addStretch()
        
        scroll_area.setWidget(form_container)
        layout.addWidget(scroll_area)
        
        # Modern button bar
        if toolbar:
            button_bar = QWidget()
            button_layout = QHBoxLayout(button_bar)
            
            self.validate_button = QPushButton("🔍 Validate")
            self.validate_button.clicked.connect(self.validate_form)
            
            self.get_data_button = QPushButton("📋 Get Data")
            self.get_data_button.clicked.connect(self.show_data)
            
            self.clear_button = QPushButton("🗑️ Clear")
            self.clear_button.clicked.connect(self.clear_form)
            
            button_layout.addStretch()
            button_layout.addWidget(self.validate_button)
            button_layout.addWidget(self.get_data_button)
            button_layout.addWidget(self.clear_button)
            
            layout.addWidget(button_bar)
        
    def get_form_data(self) -> Any:
        """Get current form data"""
        return self.form_widget.get_value()
        
    def set_form_data(self, data: Any):
        """Set form data"""
        self.form_widget.set_value(data)
        
    def validate_form(self):
        """Validate entire form and show results in a message box"""
        errors = self.form_widget.validate_value()
        self.form_widget.update_validation()
        if errors:
            msg = "\n".join([f"• {e.message}" for e in errors])
            QMessageBox.warning(self, "Validation Errors", msg)
        else:
            QMessageBox.information(self, "Validation", "No validation errors found.")

    def show_data(self):
        """Show current form data in a message box"""
        try:
            data = self.get_form_data()
            json_text = json.dumps(data, indent=2, default=str)
            QMessageBox.information(self, "Form Data", json_text)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get form data: {e}")

    def clear_form(self):
        """Clear all form data with confirmation"""
        reply = QMessageBox.question(
            self,
            "Clear Form",
            "Are you sure you want to clear all form data?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            old_widget = self.form_widget
            self.form_widget = SchemaWidgetFactory.create_widget(
                self.resolver.root_schema, self.resolver, self.validator
            )
            layout = self.layout()
            layout.replaceWidget(old_widget, self.form_widget)
            old_widget.deleteLater()