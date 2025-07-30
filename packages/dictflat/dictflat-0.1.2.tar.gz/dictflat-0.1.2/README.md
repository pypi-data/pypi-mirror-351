# dictflat

A Python library to flatten a dictionary with nested dictionnaries and lists

## Use cases

Transform a dictionary structure into a new organization ready to be inserted into a relational database.

## Installation

```bash
poetry add dictflat
```

## Quick start

```python
>>> from dictflat import DictFlat
>>> import json
>>> r = DictFlat(
    root_key="root"
).flat(
    d={
        "name": "John",
        "pers_id": 12,
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        },
        "Phone_Numbers": [
            {"type": "home", "number": "555-1234"},
            {"type": "work", "number": "555-5678"},
        ],
    }
)
>>> print("%s" % json.dumps(r, indent=2))
{
  "root": [
    {
      "__id": "662783f7-b1a0-4e8c-9de9-f3a72a896d4c",
      "name": "John",
      "pers_id": 12
    }
  ],
  "root.birth": [
    {
      "__id": "e72d549a-89f5-4208-99c0-4ce3493cbf9e",
      "__ref__root": "662783f7-b1a0-4e8c-9de9-f3a72a896d4c",
      "date": "10/06/1976 01:10:35"
    }
  ],
  "root.birth.address": [
    {
      "__id": "cc489c03-82ca-4b6e-a620-32c9c4be236c",
      "__ref__root.birth": "e72d549a-89f5-4208-99c0-4ce3493cbf9e",
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA"
    }
  ],
  "root.Phone_Numbers": [
    {
      "__id": "ba1560de-9c4c-4886-b4ca-684e0a7e5df0",
      "__ref__root": "662783f7-b1a0-4e8c-9de9-f3a72a896d4c",
      "type": "home",
      "number": "555-1234"
    },
    {
      "__id": "f1032025-6c7d-4341-8e6a-f0dce2374388",
      "__ref__root": "662783f7-b1a0-4e8c-9de9-f3a72a896d4c",
      "type": "work",
      "number": "555-5678"
    }
  ]
}
```

The result is always a dictionary where each key is a reference to the original dictionary.

* In this example, the original root document is identified by the token “`root`” (the root key) and the "`address`" sub-dictionary is identified by “`root.address`”.

Each dictionary value is always a list. See below for more examples with more than one element in lists.

Each sub-dictionnary have:

* an unique field named "`__id`" (like a primary key)
* except for root, a "`__ref__root`" who contains the "`__id`" value of parent dictionnary;
  * the "`root`" token in "`__ref__root`" field name is directly a reference to the global result dictionnary.

## Documentation

### Basic usages

#### Empty dictionnary

```python
>>> DictFlat().flat({})
```

Result:

```json
{}
```

#### Simple dictionnary

How: Use init function "`root_key`" parameter.

`root_key` parameter signature:

```python
str
```

Example:

```python
DictFlat(
    root_key="rk"
).flat(
    {
        "a": 1
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "i_1",
            "a": 1
        }
    ]
}
```

### Nested dictionnaries

#### 2 levels

Example:

```python
DictFlat(
    root_key="rk"
).flat(
    d={
        "name": "John",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        },
        "birthdate": "10/06/1976 01:10:35"
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "i_1",
            "birthdate": "10/06/1976 01:10:35",
            "name": "John"
        }
    ],
    "rk.address": [
        {
            "__id": "i_2",
            "__ref__rk": "r_3",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    ]
}
```

#### 3 levels

Example:

```python
DictFlat(
    root_key="rk"
).flat(
    d={
        "name": "John",
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        }
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "i_1",
            "name": "John"
        }
    ],
    "rk.birth": [
        {
            "__id": "i_2",
            "__ref__rk": "r_3",
            "date": "10/06/1976 01:10:35",
        }
    ],
    "rk.birth.address": [
        {
            "__id": "i_4",
            "__ref__rk.birth": "r_5",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    ]
}
```

### Use your own function to generate ids

How: Use init function "`fct_build_id`" parameter.

`fct_build_id` parameter signature:

```python
def fct_name(d: Dict, path: str) -> str
```

By default, the "[`uuid4`](https://docs.python.org/3/library/uuid.html#uuid.uuid4)" function from "[`uuid`](https://docs.python.org/3/library/uuid.html)" Python standard module is used.

In this example the function [`fct_build_id`](https://github.com/ArnaudValmary/py_dictflat/blob/main/tests/test_dictflat/common_fct_test.py#L18) is used to generate ids.

Example:

```python
DictFlat(
    root_key="rk",
    fct_build_id=fct_build_id
).flat(
    d={
        "name": "John",
        "pers_id": 12,
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        }
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "2a02485bc672ee47",
            "pers_id": 12,
            "name": "John"
        }
    ],
    "rk.birth": [
        {
            "__id": "034b3cd2487b9d17",
            "__ref__rk": "2a02485bc672ee47",
            "date": "10/06/1976 01:10:35",
        }
    ],
    "rk.birth.address": [
        {
            "__id": "4f49da4f0b4df789",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    ]
}
```

### Change/Replace value

How: Use init function "`change`" parameter.

`change` parameter signature:

```python
Optional[Dict[str, Callable]]
```

By default, no values are modified.

The dictionnary key is the future field name.

The `Callable` dictionnary value signature is:

```python
def fct_name(fieldname: str, value: Any) -> Any:
```

#### Change a string by another string

Example with a date in a string to another string:

```python
DictFlat(
    root_key="rk",
    fct_build_id=fct_build_id,
    change={
        "rk.birth.date": fix_date,
    }
).flat(
    d={
        "name": "John",
        "pers_id": 12,
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        }
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "2a02485bc672ee47",
            "pers_id": 12,
            "name": "John"
        }
    ],
    "rk.birth": [
        {
            "__id": "034b3cd2487b9d17",
            "__ref__rk": "2a02485bc672ee47",
            "date": "1976-06-10T01:10:35",
        }
    ],
    "rk.birth.address": [
        {
            "__id": "4f49da4f0b4df789",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    ]
}
```

#### Change a string by a dictionnary

Example with a date in a string to a dictionnary where date and time are separated:

```python
DictFlat(
    root_key="rk",
    fct_build_id=fct_build_id,
    change={
        "rk.birth.date": date2dict,
    }
).flat(
    d={
        "name": "John",
        "pers_id": 12,
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        }
    }
)
```

Result:

```json
assert df == {
    "rk": [
        {
            "__id": "2a02485bc672ee47",
            "pers_id": 12,
            "name": "John"
        }
    ],
    "rk.birth": [
        {
            "__id": "034b3cd2487b9d17",
            "__ref__rk": "2a02485bc672ee47",
        }
    ],
    "rk.birth.date": [
        {
            "__id": "71d9d6cb90bcd168",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "date": "1976-06-10",
            "time": "01:10:35",
        }
    ],
    "rk.birth.address": [
        {
            "__id": "4f49da4f0b4df789",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    ]
}
```

### Drop fields (by name)

How: Use init function "`drop`" parameter.

`drop` parameter signature:

```python
Optional[List[str]]
```

By default, no values are dropped.

Elements list are the future field names.

Example:

```python
DictFlat(
    root_key="rk",
    fct_build_id=fct_build_id,
    change={
        "rk.birth.date": fix_date,
    },
    drop=[
        "rk.birth.address.state",
    ]
).flat(
    d={
        "name": "John",
        "pers_id": 12,
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        }
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "2a02485bc672ee47",
            "pers_id": 12,
            "name": "John"
        }
    ],
    "rk.birth": [
        {
            "__id": "034b3cd2487b9d17",
            "__ref__rk": "2a02485bc672ee47",
            "date": "1976-06-10T01:10:35",
        }
    ],
    "rk.birth.address": [
        {
            "__id": "4f49da4f0b4df789",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "street": "123 Main St",
            "city": "Anytown"
        }
    ]
}
```

### Rename/Change field names

How: Use init function "`rename`" parameter.

`rename` parameter signature:

```python
Optional[Dict[str, Union[str, Callable]]]
```

By default, no field names values are modified.

The dictionnary key is the first version of the future field name.
The dictionnary value is the final field name or a function to genrate the new field name.

If the dictionnary key is a "`Callable`", the signature is:

```python
def fct_name(s: str) -> str
```

**IMPORTANT**
**If you use  "`change`" parameter and "`rename`" parameter, use the final field name in "`rename`" dictionnary value as "`change`" dictionnary key**.

### Rename field name by name

Example:

```python
DictFlat(
    root_key="rk",
    fct_build_id=fct_build_id,
    change={
        "rk.birth.date_dict": date2dict,
    },
    rename={
        "rk.birth.date": "rk.birth.date_dict",
        "PersId": "pers_id",
    }
).flat(
    d={
        "name": "John",
        "PersId": 12,
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        }
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "2a02485bc672ee47",
            "pers_id": 12,
            "name": "John"
        }
    ],
    "rk.birth": [
        {
            "__id": "034b3cd2487b9d17",
            "__ref__rk": "2a02485bc672ee47",
        }
    ],
    "rk.birth.date_dict": [
        {
            "__id": "71d9d6cb90bcd168",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "date": "1976-06-10",
            "time": "01:10:35",
        }
    ],
    "rk.birth.address": [
        {
            "__id": "4f49da4f0b4df789",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    ]
}
```

#### Rename ALL field names

You could rename all fields using the "`RENAME_ALL`" special key and un function to do this.

The "`Callable`" dictionnary key function signature is:

```python
def fct_name(s: str) -> str
```

**IMPORTANT**
**You could use "`RENAME_ALL`" key and field name keys. "`RENAME_ALL`" key is allway use BEFORE field name keys**

In this example, the function "[`str_2_snakecase`](https://github.com/ArnaudValmary/py_dictflat/blob/main/src/dictflat/tool_functions.py#L10)" is called before the other rename key.

Example:

```python
DictFlat(
    root_key="rk",
    fct_build_id=fct_build_id,
    change={
        "rk.birth.date_dict": date2dict,
    },
    rename={
        RENAME_ALL: str_2_snakecase,
        "rk.birth.date": "rk.birth.date_dict",
    }
).flat(
    d={
        "Name": "John",
        "PersId": 12,
        "Birth": {
            "Address": {
                "Street": "123 Main St",
                "City": "Anytown",
                "State": "CA"
            },
            "Date": "10/06/1976 01:10:35"
        }
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "2a02485bc672ee47",
            "pers_id": 12,
            "name": "John"
        }
    ],
    "rk.birth": [
        {
            "__id": "034b3cd2487b9d17",
            "__ref__rk": "2a02485bc672ee47",
        }
    ],
    "rk.birth.date_dict": [
        {
            "__id": "71d9d6cb90bcd168",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "date": "1976-06-10",
            "time": "01:10:35",
        }
    ],
    "rk.birth.address": [
        {
            "__id": "4f49da4f0b4df789",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    ]
}
```

### Lists

Each element of a list a transformed as a dictionnary of a same type.

#### List of dictionaries

By default, no element are added in each dictionnary.

Example:

```python
DictFlat(
    root_key="rk",
    fct_build_id=fct_build_id,
    change={
        "rk.birth.date_dict": date2dict,
    },
    rename={
        "rk.birth.date": "rk.birth.date_dict",
    }
).flat(
    d={
        "name": "John",
        "pers_id": 12,
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        },
        "Phone_Numbers": [
            {"type": "home", "number": "555-1234"},
            {"type": "work", "number": "555-5678"},
        ],
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "2a02485bc672ee47",
            "pers_id": 12,
            "name": "John"
        }
    ],
    "rk.birth": [
        {
            "__id": "034b3cd2487b9d17",
            "__ref__rk": "2a02485bc672ee47",
        }
    ],
    "rk.birth.date_dict": [
        {
            "__id": "71d9d6cb90bcd168",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "date": "1976-06-10",
            "time": "01:10:35",
        }
    ],
    "rk.birth.address": [
        {
            "__id": "4f49da4f0b4df789",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    ],
    "rk.Phone_Numbers": [
        {
            "__id": "5d1765d47e80b6d3",
            "__ref__rk": "2a02485bc672ee47",
            "type": "home",
            "number": "555-1234"
        },
        {
            "__id": "87d897df197fbdc7",
            "__ref__rk": "2a02485bc672ee47",
            "type": "work",
            "number": "555-5678"
        },
    ],
}
```

#### Add counter field in each list element

How: Use init function "`list_2_object`" parameter.

`list_2_object` parameter signature:

```python
Optional[Dict[str, Dict]]
```

By default, no fields are added.

The dictionnary key is the first version of the future field name.
The dictionnary value is sub-dictionnary for parametrize the job:

* The key "`counter_field`" contains the field name (a "`str`") for the counter;
  * Default value is "`idx`".
* The key "`starts_at`" contains the counter start value (a "`int`").
  * Default value is `1`.

Example:

```python
DictFlat(
    root_key="rk",
    fct_build_id=fct_build_id,
    change={
        "rk.birth.date_dict": date2dict,
    },
    rename={
        "rk.birth.date": "rk.birth.date_dict",
    },
    list_2_object={
        "rk.Phone_Numbers": {
            "counter_field": "count",
            "starts_at": 0
        }
    }
).flat(
    d={
        "name": "John",
        "pers_id": 12,
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        },
        "Phone_Numbers": [
            {"type": "home", "number": "555-1234"},
            {"type": "work", "number": "555-5678"},
        ],
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "2a02485bc672ee47",
            "pers_id": 12,
            "name": "John"
        }
    ],
    "rk.birth": [
        {
            "__id": "034b3cd2487b9d17",
            "__ref__rk": "2a02485bc672ee47",
        }
    ],
    "rk.birth.date_dict": [
        {
            "__id": "71d9d6cb90bcd168",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "date": "1976-06-10",
            "time": "01:10:35",
        }
    ],
    "rk.birth.address": [
        {
            "__id": "4f49da4f0b4df789",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    ],
    "rk.Phone_Numbers": [
        {
            "__id": "30fb5bc71274e531",
            "__ref__rk": "2a02485bc672ee47",
            "count": 0,
            "type": "home",
            "number": "555-1234"
        },
        {
            "__id": "6b74835b56e08367",
            "__ref__rk": "2a02485bc672ee47",
            "count": 1,
            "type": "work",
            "number": "555-5678"
        },
    ],
}
```

#### List of non-dictionary elements

If the list do not contains dictionnary elements, you could specify the name of the future key with the suffix "`.__inner`".

Example:

```python
DictFlat(
    root_key="rk",
    fct_build_id=fct_build_id,
    change={
        "rk.birth.date_dict": date2dict,
    },
    rename={
        RENAME_ALL: str_2_snakecase,
        "rk.birth.date": "rk.birth.date_dict",
        "rk.phone_numbers.__inner": "number",
    }
).flat(
    d={
        "name": "John",
        "pers_id": 12,
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        },
        "Phone_Numbers": [
            "555-1234",
            "555-5678",
        ],
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "2a02485bc672ee47",
            "pers_id": 12,
            "name": "John"
        }
    ],
    "rk.birth": [
        {
            "__id": "034b3cd2487b9d17",
            "__ref__rk": "2a02485bc672ee47",
        }
    ],
    "rk.birth.date_dict": [
        {
            "__id": "71d9d6cb90bcd168",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "date": "1976-06-10",
            "time": "01:10:35",
        }
    ],
    "rk.birth.address": [
        {
            "__id": "4f49da4f0b4df789",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    ],
    "rk.phone_numbers": [
        {
            "__id": "24886b1e9942f612",
            "__ref__rk": "2a02485bc672ee47",
            "number": "555-1234"
        },
        {
            "__id": "a98b1c4fa2e2a2b5",
            "__ref__rk": "2a02485bc672ee47",
            "number": "555-5678"
        },
    ],
}
```

### Squash dictionnaries

When you have a dictionary of dictionaries and want to have just one.

How: Use init function "`dict_of_dicts_2_dict`" parameter.

`dict_of_dicts_2_dict` parameter signature:

```python
Optional[Dict[str, Dict]]
```

The key is the future dictionnary name
The value is the definition of treatment:

* "`sep`": The separator between the key of first data dictionnary and the key of second data dictionnary (default value is a dot "`.`")
  * You could change the default value for all separators with "`sep`" init function.
* "`reverse`": To change the order of the keys on each side of the separator (default value is `False`)

Example:

```mermaid
%%{init: {'themeVariables': { 'fontFamily': 'monospace'}}}%%
graph LR;
  from["
&quot;miracles&quot;: {
&nbsp;&nbsp;&nbsp;&nbsp;&quot;first&quot;:&nbsp;{
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;k&quot;:&nbsp;&quot;one&quot;,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;e&quot;:&nbsp;&quot;e-one&quot;
&nbsp;&nbsp;&nbsp;&nbsp;},
&nbsp;&nbsp;&nbsp;&nbsp;&quot;second&quot;:&nbsp;{
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;k&quot;:&nbsp;&quot;two&quot;
&nbsp;&nbsp;&nbsp;&nbsp;},
&nbsp;&nbsp;&nbsp;&nbsp;&quot;third&quot;:&nbsp;&quot;three&quot;
}
"]
  to["
'rk.miracles': [
&nbsp;&nbsp;&nbsp;&nbsp;{
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;__id&quot;:&nbsp;&quot;041102055056a3a8&quot;,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;__ref__rk&quot;:&nbsp;&quot;2a02485bc672ee47&quot;,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;first/k&quot;:&nbsp;&quot;one&quot;,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;first/e&quot;:&nbsp;&quot;e-one&quot;,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;second/k&quot;:&nbsp;&quot;two&quot;,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;third&quot;:&nbsp;&quot;three&quot;,
&nbsp;&nbsp;&nbsp;&nbsp;},
]
"]
  from-->to
  style from text-align:left
  style to text-align:left
```

```python
DictFlat(
    root_key="rk",
    fct_build_id=fct_build_id,
    change={
        "rk.birth.date_dict": date2dict,
    },
    rename={
        "rk.birth.date": "rk.birth.date_dict",
    },
    dict_of_dicts_2_dict={
        "rk.miracles": {
            "reverse": False,
            "sep": "/"
        }
    }
).flat(
    d={
        "name": "John",
        "pers_id": 12,
        "birth": {
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA"
            },
            "date": "10/06/1976 01:10:35"
        },
        "miracles": {
            "first": {
                "k": "one",
                "e": "e-one"
            },
            "second": {
                "k": "two"
            },
            "third": "three"
        }
    }
)
```

Result:

```json
{
    "rk": [
        {
            "__id": "2a02485bc672ee47",
            "pers_id": 12,
            "name": "John"
        }
    ],
    "rk.birth": [
        {
            "__id": "034b3cd2487b9d17",
            "__ref__rk": "2a02485bc672ee47",
        }
    ],
    "rk.birth.date_dict": [
        {
            "__id": "71d9d6cb90bcd168",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "date": "1976-06-10",
            "time": "01:10:35",
        }
    ],
    "rk.birth.address": [
        {
            "__id": "4f49da4f0b4df789",
            "__ref__rk.birth": "034b3cd2487b9d17",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    ],
    "rk.miracles": [
        {
            "__id": "041102055056a3a8",
            "__ref__rk": "2a02485bc672ee47",
            "first/k": "one",
            "first/e": "e-one",
            "second/k": "two",
            "third": "three",
        },
    ],
}
```
