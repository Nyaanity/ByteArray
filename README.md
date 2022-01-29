## Read & write hex streams
##### Example
```py
data = b"\x01\xff\xff\xff\xff\x8c\x80\x00\x00\x20"


first_byte = ByteArray(data).readByte()  # out: 01
```
