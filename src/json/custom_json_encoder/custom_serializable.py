class CustomSerializeError(Exception):
    pass

class CustomSerializable:
    '''Custom JSON string representation of a Python data structure.

    >>> from json.custom_json_encoder import CustomSerializable
    >>> class Foo(CustomSerializable):
            def __init__(self, data):
                self.data
            def encode(self):
                return '@'.join(self.data)
    >>> a = Foo([1,2,3])
    >>> a.encode()
    '1@2@3'

    >>> import json
    >>> from json.custom_json_encoder import CustomJsonEncoder
    >>> json.dumps({"data": a}, cls=CustomJsonEncoder, custom_classes=[Foo])
    '{"data": 1@2@3}'
    '''

    def encode(self, defualt_iterencode):
        '''Return a custom JSON string representation of a Python data structure.

        >>> from json.custom_json_encoder import CustomSerializable
        >>> class Foo(CustomSerializable):
                def __init__(self, data):
                    self.data
                def encode(self):
                    return '@'.join(self.data)
        >>> a = Foo([1,2,3])
        >>> a.encode()
        '1@2@3'
        '''
        pass

    def try_yield(self, default_iterencode):
        try:
            self.encode(default_iterencode)
        except CustomSerializeError:
            return False
        return True
    
    def get_yield(self, buf, default_iterencode):
        yield buf + self.encode(default_iterencode)

