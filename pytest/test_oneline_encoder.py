from custom_json_encoder import CustomJSONEncoder, CustomSerializable
from custom_json_encoder.sample import Oneline
import json

def test_custom_json_encoder():
    class Foo(CustomSerializable):
        def __init__(self, data):
            self.data = data
        
        def encode(self, current_indent_level, default_iterencode):
            return ''.join(default_iterencode(self.data, current_indent_level, _local_separator=' | '))
        
    a = Foo([1,2,3])
    # print(''.join(list(CustomJSONEncoder(custom_classes=[Foo]).iterencode(a))))
    print(json.dumps({"data": a}, cls=CustomJSONEncoder, custom_classes=[Foo]))

def test_oneline_encoder():
    a = [1,2,3,4,5]
    b = {"a": "apple", "b": "banana", "c": "candy"}
    print("With Oneline:")
    print(json.dumps({"list": a, "dict": b}, indent=2))

    print("\nWith Oneline")
    print(json.dumps({"list": Oneline(a), "dict": Oneline(b)},
                     indent=2, cls=CustomJSONEncoder, custom_classes=[Oneline]))
    
    print("\n")
    print(json.dumps({"list": Oneline(a, separator=' + '),
                      "dict1": Oneline({"dict2": b}, key_separator=' = ')}, indent=2,
                     cls=CustomJSONEncoder, custom_classes=[Oneline]))

    


if __name__ == "__main__":
    # test_custom_json_encoder()
    test_oneline_encoder()

