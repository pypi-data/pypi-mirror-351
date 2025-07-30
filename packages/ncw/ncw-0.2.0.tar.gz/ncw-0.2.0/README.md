# ncw

_Nested collections wrapper_

Classes to access and/or modify data in nested collections,
i.e. possibly deep nested dicts or lists of str, int, float, bool, or None.

## Installation

Install from PyPI

``` bash
pip install ncw
```


## Example Usage

The **Structure** class prevents accidental changes to the underlying data structure
by preventing direct access.
All returned substructures are deep copies of the internally stored substructures.

The **MutableStructure** class allows changes (ie. deletions and updates)
to the underlying data structure, and returns the internally stored substructures themselves.

Please note that both classes make a deep copy of the data structure at initialization time
(thus preventing accidental changes to the original data through the instance).

``` pycon
>>> serialized = '{"herbs": {"common": ["basil", "oregano", "parsley", "thyme"], "disputed": ["anise", "coriander"]}}'
>>>
>>> import json
>>> from ncw import Structure, MutableStructure
>>>
>>> readonly = Structure.from_json_string(serialized)
>>> readonly["herbs"]
{'common': ['basil', 'oregano', 'parsley', 'thyme'], 'disputed': ['anise', 'coriander']}
>>> readonly["herbs.common"]
['basil', 'oregano', 'parsley', 'thyme']
>>> readonly["herbs", "common"]
['basil', 'oregano', 'parsley', 'thyme']
>>> readonly["herbs", "common", 1]
'oregano'
>>> readonly["herbs.common.1"]
'oregano'
>>> readonly["herbs.common.1"] = "marjoram"
Traceback (most recent call last):
  File "<python-input-9>", line 1, in <module>
    readonly["herbs.common.1"] = "marjoram"
    ~~~~~~~~^^^^^^^^^^^^^^^^^^
TypeError: 'Structure' object does not support item assignment
>>>
>>> original_data = json.loads(serialized)
>>> writable = MutableStructure(original_data)
>>> writable.data == original_data
True
>>> writable.data is original_data
False
>>> writable["herbs.common.1"]
'oregano'
>>> writable["herbs.common.1"] = "marjoram"
>>> del writable["herbs", "common", 2]
>>> writable["herbs.common"]
['basil', 'marjoram', 'thyme']
>>>
```