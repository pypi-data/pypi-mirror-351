# orjson-less pickledb
A fork of pickledb that pretty much just replaces this line:
```python
import orjson
```
With the following:
```python
import json as orjson
```

 \
The `option` argument was also removed from the `save` method due to it being flags passed to orjson's `dumps` implementation that weren't being used by pickledb itself.

Why? \
Because orjson refuses to support PyPy with the reason being that it *"uses private undocumented functions in cpython's API"* (See [#90](https://github.com/ijl/orjson/issues/90#issuecomment-2380389948)).

Forked from commit [46ab99ffad71ea4fd8c29adcb3aea076e24a1865](https://github.com/patx/pickledb/commit/46ab99ffad71ea4fd8c29adcb3aea076e24a1865) (version 1.3.2).