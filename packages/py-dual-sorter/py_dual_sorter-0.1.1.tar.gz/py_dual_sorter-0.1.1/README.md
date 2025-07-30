* website: <https://arrizza.com/py-dual-sorter.html>
* installation: see <https://arrizza.com/setup-common.html>

## Summary

This project is for content that needs to be iterated in two different ways.
It allows two keys ("left" and "right") to be defined at the same time.

## How to use

#### load()

Use ```load(path)``` to load a json file.
Use ```load(path, validate=True)``` to check for duplicate keys.

Sample json content is:

```text
[
    [
        "left3",    # <== the "left" key
        "right2",   # <== the "right" key
        "infoA"     # <== info for this entry & keys; Can be "null" if there is no info
    ],
    [
        "left2",
        "right3",
        null
    ],
]
```

#### save()

Use ```save(path)``` to save the current content to a json file.

#### add()

Use ```add(left, right, info)``` to add a new entry.
The left and right keys have to be unique, otherwise an exception is thrown.

Note that info is optional ```add(left, right)``` or explicitly set to None.

#### all_by_left() and all_by_right()

To iterate in sorted order by the left key, use:

```python
pds = PyDualSorter()
pds.load('path/to/file')
for left, right, info in pds.all_by_left():
    print(f'left key is  {left}')
    print(f'right key is {left}')
    print(f'info is      {info}')
```

To iterate in sorted order by the right key, use:

```python
pds = PyDualSorter()
pds.load('path/to/file')
for left, right, info in pds.all_by_left():   # <== note that left key is still present
    print(f'left key is  {left}')
    print(f'right key is {left}')
    print(f'info is      {info}')
```

#### is_left() and is_right()

Use ```is_left(val)``` to check if a value is a left key.
Use ```is_right(val)``` to check if a value is a right key.

#### get_left_info() and get_right_info()

Use ```info = pds.get_left_info(left)``` to get the info associated with the given left key.
Use ```info = pds.get_right_info(right)``` to get the info associated with the given right key.

#### get_left() and get_right()

Use ```right = pds.get_right(left)``` to get the matching right key for the given left key.
Use ```left = pds.get_left(right)``` to get the matching left key for the given right key.
