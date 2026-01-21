import socket
import struct
import time
import sys

# Configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 33535

# Client expected format (from estapar_integration_service.py)
RESPONSE_FORMAT = (
    "<"  # Little-endian
    # rspHeader (45 bytes)
    "H"  # rspFiller (2 bytes, unsigned short) - Ignored
    "I"  # rspType (4 bytes, unsigned int)
    "15s"  # rspSignature (15 bytes, string)
    "16s"  # rspCompanySign (16 bytes, string)
    "I"  # rspTmt (4 bytes, unsigned int) - Timestamp
    "I"  # rspSeqNo (4 bytes, unsigned int) - Sequence number matched
    # rspData (566 bytes)
    "I"  # rspTermld (4 bytes, unsigned int)
    "64s"  # rspCardld (64 bytes, string)
    "I"  # rspStatus (4 bytes, unsigned int)
    "128s"  # rspOpDisplayTxt (128 bytes, string)
    "128s"  # rspCustDisplayTxt (128 bytes, string)
    "128s"  # rspPrinterLineTxt (128 bytes, string)
    "I"  # rspEntryTimeStamp (4 bytes, unsigned int)
    "H"  # rspVehicleType (2 bytes, unsigned short)
    "H"  # rspRUF_1 (2 bytes, unsigned short) - Reserved
    "I"  # rspRUF_2 (4 bytes, unsigned int) - Reserved
)

def run_test():
    print(f"Submitting request to {SERVER_IP}:{SERVER_PORT}...")
    
    # Construct a raw request that the server accepts
    # Based on server logic: receives 2 bytes size, then payload.
    # cmdType needs to be 0x0000000F or 0x00000010 at offset 4 of the payload (excluding size bytes??)
    # Server: msg_process(mensagem) where mensagem = tamanho + payload
    # Server unpacks: cmdType = struct.unpack("<I", mensagem[4:8])[0]
    # So valid payload: [2 bytes size] [2 bytes filler?] [4 bytes cmdType] ...
    
    # Let's craft a minimal valid message
    # Size: H (2 bytes)
    # Payload: 
    #   Offset 0-1: Size (sent separately in code, but msg_process receives it concatenated)
    #   Offset 2-3: Filler? Server reads mensagem[4:8].
    #   Wait, server implementation:
    #     tamanho = conn.recv(2)
    #     msg_size...
    #     mensagem = ...
    #     msg_process(tamanho + mensagem)
    #     Inside msg_process(msg):
    #       cmdType = struct.unpack("<I", msg[4:8])[0]
    #       So if msg starts at index 0.
    #       Indices 0,1 are size.
    #       Indices 2,3 are ignored?
    #       Indices 4,5,6,7 are cmdType.
    
    # Let's send a validation command: 0x0000000F (cmdConsult)
    cmd_type = 0x0000000F
    
    # Construct payload
    # We need enough bytes so msg[25:89] exists for card_id
    # 2 bytes size + 2 bytes filler + 4 bytes cmdType = 8 bytes.
    # We need up to 89 bytes.
    # Let's clean build:
    # [Size: 2] [Filler: 2] [CmdType: 4] [Padding until 25] [CardID: 64] ...
    # Total size needs to be calculable.
    
    payload = bytearray(100) # Ensure enough size
    # Filler
    payload[0:2] = b'\x00\x00' # Indices 2,3 in msg_process terms (since 0,1 are size)
    # CmdType
    struct.pack_into("<I", payload, 2, cmd_type) # Indices 4-7
    
    # Card ID at msg[25:89].
    # If msg starts with Size(2), then index 25 is payload index 23.
    card_id = b"TESTCARD123456"
    payload[23:23+len(card_id)] = card_id
    
    # CmdSeqNo at msg[28:32].
    # msg index 28 => payload index 26.
    seq_no = 12345
    struct.pack_into("<I", payload, 26, seq_no)

    # Calculate size
    msg_size = len(payload)
    size_bytes = struct.pack("<H", msg_size)
    
    full_message = size_bytes + payload
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((SERVER_IP, SERVER_PORT))
        
        # Send size then payload
        s.sendall(full_message)
        
        # Receive response
        # 1. Read size
        resp_size_data = s.recv(2)
        if not resp_size_data:
            print("Failed to receive response size")
            sys.exit(1)
            
        resp_size = struct.unpack("<H", resp_size_data)[0]
        print(f"Received response size header: {resp_size}")
        
        # 2. Read payload
        resp_payload = b""
        while len(resp_payload) < resp_size:
            chunk = s.recv(resp_size - len(resp_payload))
            if not chunk:
                break
            resp_payload += chunk
            
        print(f"Received payload size: {len(resp_payload)}")
        
        expected_struct_size = struct.calcsize(RESPONSE_FORMAT)
        print(f"Client expected struct size: {expected_struct_size}")
        
        # Now try to unpack with CLIENT format
        unpacked = struct.unpack(RESPONSE_FORMAT, resp_payload)
        
        # Check specific fields
        # unpack returns tuple: (rspFiller, rspType, rspSignature, ..., rspSeqNo, rspTermId, ..., rspStatus, ...)
        # Index 4: rspTmt
        # Index 5: rspSeqNo
        # Index 6: rspTermId (This was the missing one!)
        # Index 8: rspStatus
        
        rsp_seq_no = unpacked[5]
        rsp_status = unpacked[8]
        
        print(f"Unpacked SeqNo: {rsp_seq_no} (Expected: {seq_no})")
        print(f"Unpacked Status: {rsp_status} (Expected: 0 for Success)")
        
        if rsp_seq_no == seq_no and rsp_status == 0:
            print("SUCCESS: Response matches client expectations!")
        else:
            print("FAILURE: Data unpacked but content is incorrect.")
            sys.exit(1)
            
    except Exception as e:
        print(f"TEST FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        s.close()

if __name__ == "__main__":
    run_test()
