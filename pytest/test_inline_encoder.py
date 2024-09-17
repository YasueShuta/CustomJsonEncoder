from cjenc import CJEnc, CustomSerializable
from cjenc.sample import Inline
import json

def test_custom_json_encoder():
    class Foo(CustomSerializable):
        def __init__(self, data):
            self.data = data
        
        def encode(self, current_indent_level, default_iterencode):
            return ''.join(default_iterencode(self.data, current_indent_level, _local_separator=' | '))
        
    a = Foo([1,2,3])
    # print(''.join(list(CustomJSONEncoder(custom_classes=[Foo]).iterencode(a))))
    print(json.dumps({"data": a}, cls=CJEnc, custom_classes=[Foo]))

def test_inline_encoder():
    a = [1,2,3,4,5]
    b = {"a": "apple", "b": "banana", "c": "candy"}
    print("Without Inline:")
    print(json.dumps({"list": a, "dict": b}, indent=2))

    print("\nWith Inline")
    print(json.dumps({"list": Inline(a), "dict": Inline(b)},
                     indent=2, cls=CJEnc, custom_classes=[Inline]))
    
    print("\n")
    print(json.dumps({"list": Inline(a, separator=' + '),
                      "dict1": Inline({"dict2": b}, key_separator=' = ')}, indent=2,
                     cls=CJEnc, custom_classes=[Inline]))

    


if __name__ == "__main__":
    # test_custom_json_encoder()
    test_inline_encoder()

