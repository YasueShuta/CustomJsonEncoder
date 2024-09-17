from .custom_serializable import CustomSerializable, CustomSerializeError

class Inline(CustomSerializable):
    '''Print items in oneline, even if indent is set.

    >>> import json
    >>> from custom_json_encoder import CustomJSONEncoder
    >>> from custom_json_encoder.sample import Inline
    >>> a = [1,2,3]
    >>> b = {'a': 'apple', 'b': 'banana'}
    
    Without Inline
    >>> print(json.dumps({"list": a, "dict": b}, indent=2))
    {
      "list": [
        1,
        2,
        3
      ],
      "dict": {
        "a": "apple",
        "b": "banana"
      }
    }

    With Oneline
    >>> print(json.dumps({"list": Inline(a), "dict": Oneline(b)}, indent=2, cls=CustomJSONEncoder, custom_classes=[Inline]))
    {
      "list": [1, 2, 3],
      "dict": {: "apple", : "banana", : "candy"}
    }
    '''
    def __init__(self, data, separator=', ', key_separator=': '):
        self.data = data
        self.separator = separator
        self.key_separator = key_separator
    
    def iterencode(self, current_indent_level, default_iterencode):
        try:
            if isinstance(self.data, (list, tuple)):
                yield '['
                for i,v in enumerate(self.data):
                    if i > 0:
                        yield self.separator
                    yield from default_iterencode(Inline(v, self.separator, self.key_separator),
                                                  current_indent_level, self.separator)
                yield ']'
            elif isinstance(self.data, dict):
                yield '{'
                for i, (k,v) in enumerate(self.data.items()):
                    if i > 0:
                        yield self.separator
                    yield from default_iterencode(k, current_indent_level, self.separator)
                    yield self.key_separator
                    yield from default_iterencode(Inline(v, self.separator, self.key_separator),
                                                  current_indent_level, self.separator)
                yield '}'
            else:
                yield from default_iterencode(self.data,
                                              _current_indent_level=current_indent_level,
                                              _local_separator=self.separator)
        except:
            yield from default_iterencode(self.data,
                                          current_indent_level, self.separator)
