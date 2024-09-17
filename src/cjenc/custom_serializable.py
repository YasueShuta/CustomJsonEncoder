class CustomSerializeError(Exception):
    pass

class CustomSerializable:
    '''Custom JSON string representation of a Python data structure.

    >>> from cjenc import CustomSerializable
    >>> class Foo(CustomSerializable):
            def __init__(self, data):
                self.data
            def encode(self):
                return '@'.join(self.data)
    >>> a = Foo([1,2,3])
    >>> a.encode()
    '1@2@3'

    >>> import json
    >>> from cjenc import CJEnc
    >>> json.dumps({"data": a}, cls=CJEnc, custom_classes=[Foo])
    '{"data": 1@2@3}'
    '''

    def __init__(self, data):
        self.data = data

    def encode(self, _current_indent_level, default_iterencode):
        '''Return a custom JSON string representation of a Python data structure.

        >>> from cjenc import CustomSerializable
        >>> class Foo(CustomSerializable):
                def __init__(self, data):
                    self.data
                def encode(self, *args):
                    return '@'.join(self.data)
        >>> a = Foo([1,2,3])
        >>> a.encode()
        '1@2@3'
        '''
        pass

    def iterencode(self, current_indent_level, default_iterencode):
        try:
            yield self.encode(current_indent_level, default_iterencode)
        except CustomSerializeError:
            yield from default_iterencode(self.data, current_indent_level)
    
    def get_yield(self, buf, current_indent_level, default_iterencode):
        yield from (buf + i for i in self.iterencode(current_indent_level, default_iterencode))

