# ruff: noqa: F403, F405
from shua.struct import * 

def main():
    class Header(BinaryStruct):
        version: UInt8
        length: UInt16
    
    class Packet(BinaryStruct):
        header: Header
        payload: BytesField = BytesField(length=lambda ctx: ctx['header']['length'])

    payload = b"Hello World!"
    pkt = Packet(
        header=Header(version=1,length=len(payload)),
        payload=payload
    )

    print("Original packet:")
    print(pkt)
    
    data = pkt.build()
    
    print("\nBuilt data:", data.hex())

    parsed_pkt = Packet.parse(data)
    print("\nParsed packet:")
    print(parsed_pkt)

    print("\nField values:")
    print("Version:", parsed_pkt.header.version)
    assert parsed_pkt.header.version == pkt.header.version
    print("Length:", parsed_pkt.header.length)
    assert parsed_pkt.header.length == pkt.header.length
    print("Payload:", parsed_pkt.payload)
    assert parsed_pkt.payload == pkt.payload