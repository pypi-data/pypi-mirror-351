# ya
Make filters with the mongo language

To install:	```pip install ya```

## Overview
The `ya` package provides a Python implementation for creating and applying filters based on a MongoDB-like query language. This allows users to filter dictionaries in Python similarly to how one might filter documents in a MongoDB collection using query operators like `$gt`, `$lt`, `$eq`, and more.

The package primarily revolves around constructing filter functions that can be applied to dictionaries to check if they match certain conditions. These conditions are specified in a way that closely resembles MongoDB's query syntax, making it intuitive for users familiar with MongoDB.

## Main Features
- **MongoDB-like Query Language**: Use familiar MongoDB operators to specify conditions.
- **Flexible Key Paths**: Supports nested dictionaries using dot notation in key paths.
- **Logical Operators**: Includes support for `$and`, `$or`, and `$nor` logical operations to combine multiple conditions.

## Installation
To install the `ya` package, run the following command:
```
pip install ya
```

## Usage Examples

### Basic Filtering
```python
from ya import dict_filt_from_mg_filt

# Define a filter
mg_filt = {'age': {'$gte': 18}}
filt = dict_filt_from_mg_filt(mg_filt)

# Apply the filter
print(filt({'name': 'Alice', 'age': 20}))  # Output: True
print(filt({'name': 'Bob', 'age': 17}))    # Output: False
```

### Complex Filtering with Logical Operators
```python
from ya import dict_filt_from_mg_filt

# Define a complex filter
mg_filt = {
    '$and': [
        {'age': {'$gte': 18}},
        {'age': {'$lte': 30}}
    ]
}
filt = dict_filt_from_mg_filt(mg_filt)

# Apply the filter
print(filt({'name': 'Charlie', 'age': 25}))  # Output: True
print(filt({'name': 'Dave', 'age': 31}))     # Output: False
```

### Nested Fields and Lists
```python
from ya import dict_filt_from_mg_filt

# Define a filter that uses nested fields and lists
mg_filt = {
    'details.education.degree': 'MSc',
    'hobbies': {'$in': ['hiking', 'reading']}
}
filt = dict_filt_from_mg_filt(mg_filt)

# Apply the filter
person = {
    'name': 'Eve',
    'details': {
        'education': {
            'degree': 'MSc'
        }
    },
    'hobbies': ['reading', 'painting']
}
print(filt(person))  # Output: True
```

## Function Documentation

### `dict_filt_from_mg_filt(mg_filt)`
Creates a filter function based on the specified MongoDB-like filter `mg_filt`. This function can be used to filter a list of dictionaries, returning `True` if a dictionary matches the filter conditions.

- **Parameters**:
  - `mg_filt`: A dictionary specifying the MongoDB-like query conditions.
- **Returns**:
  - A function that takes a dictionary and returns `True` if it matches the conditions specified in `mg_filt`.

### `mg_filt_kv_to_func(key_path, val_condition)`
Converts a key-value pair into a filter function. This function is used internally to handle individual conditions within a larger query.

- **Parameters**:
  - `key_path`: The path to the value in the dictionary (supports nested paths).
  - `val_condition`: The condition that the value at `key_path` should meet.
- **Returns**:
  - A function that takes a dictionary and returns `True` if the value at `key_path` meets `val_condition`.

This package is ideal for applications requiring filtering of complex data structures in a way that is both expressive and familiar to those who use MongoDB.