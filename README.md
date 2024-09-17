# CJEnc; Customizable JSON Encoder

Customizable JSON encoder for json module of python.

Pythonの標準モジュールであるjsonのdump, loadで使えるカスタムJSONエンコーダーです。

cjenc.sample内のクラスや、オリジナルのクラスを追加して、defaultによるカスタマイズだけでは実現できない独自のJSON形式を出力するサポートをします。

## How to Use

<pre>
Shell:

$ pip install customizable_json_encoder
</pre>

<pre>
Python:

import json
import cjenc import CJEnc
import cjenc.sample import Inline

data = {"status": "OK", "data": [1,2,3,4,5]}

# default json indent
print(json.dumps(data, indent=2))
# {
#   "status": "OK",
#   "data": [
#     1,
#     2,
#     3,
#     4,
#     5
#   ]
# }

# use Inline class

data["data"] = Inline(data["data"], separator=", ")
print(json.dumps(data, indent=2, cls=CJEnc))
# {
#   "status": "OK",
#   "data": [1, 2, 3, 4, 5]   
# }
</pre>
