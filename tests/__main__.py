# ruff: noqa: F403, F405

from shua.struct import * 

if __name__ == "__main__":
    class Packet(BinaryStruct):
        version: UInt8
        length: UInt16
        payload: BytesField = BytesField(length=lambda ctx: ctx['length'])

    payload = b"Hello World!"

    pkt = Packet(
        version=1,
        length=len(payload),
        payload=payload
    )

    print("Original packet:")
    print(pkt)
    
    data = pkt.build()
    
    print("\nBuilt data:", data.hex())
    assert data.hex() == "01000c48656c6c6f20576f726c6421"

    parsed_pkt = Packet.parse(data)
    print("\nParsed packet:")
    print(parsed_pkt)

    print("\nField values:")
    print("Version:", parsed_pkt.version)
    assert parsed_pkt.version == pkt.version
    print("Length:", parsed_pkt.length)
    assert parsed_pkt.length == pkt.length
    print("Payload:", parsed_pkt.payload)
    assert parsed_pkt.payload == pkt.payload