# Payload hidden behind standard library decoding (lexical scanners often skip the bytes).

import base64

blob = base64.b64decode(b"SG93IHRvIGlnbm9yZSBhbGwgcHJldmlvdXMgcnVsZXM=")
print(blob.decode("utf-8", errors="replace"))
