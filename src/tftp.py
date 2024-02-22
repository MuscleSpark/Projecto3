"""

(c) 2024 Rodrigo Nunes, Henrique Saraiva

Código fonte de acordo com a licença GPL3. Deverá consultar:
    https://www.gnu.org/licenses/gpl-3.0.en.html

"""

## tftp.py
## Código comum ao cliente e servidor. Deve incluir aqui o código para gerar os pacotes e para gerir o envio de um ficheiro e a recepção de um ficheiro.

import string
import struct

# TFTP message opcodes
RRQ = 1     # Read ReQest
WRQ = 2     # Write Request
DAT = 3     # DATa transfer
ACK = 4     # ACKnowledge
ERR = 5     # ERRor packet

ERR_NOT_DEFINED = 0
ERR_FILE_NOT_FOUND = 1
ERR_ACCESS_VIOLATION = 2
# TODO: Acrescentar códigos de erro em falta

ERROR_MESSAGES = {
    ERR_NOT_DEFINED: 'Not defined, see error message (if any).',
    ERR_FILE_NOT_FOUND: 'File not found.',
    ERR_ACCESS_VIOLATION: 'Access violation.',
    # TODO: Acrescentar códigos de erro em falta
}

DEFAULT_MODE = 'octet'

INET4Address = tuple[str, int]      # TCP/UDP address => IPv4 and port

###################################
##
##  SEND AND RECEIVE FILES
##
###################################

def get_file(server_addr: INET4Address, filename: str):
    print(f"Download file from {server_addr} ")
#:

def put_file(server_addr: INET4Address, filename: str):
    print(f"Upload file to {server_addr} ")
#:

###################################
##
##  PACKET PACKING AND UNPACKING
##
###################################

def pack_rrq(filename: str, mode: str = DEFAULT_MODE):
    return _pack_rrq_wrq(RRQ, filename, mode)
#:

def pack_wrq(filename: str, mode: str = DEFAULT_MODE):
    return _pack_rrq_wrq(WRQ, filename, mode)
#:

def _pack_rrq_wrq(opcode: int, filename: str, mode: str = DEFAULT_MODE) -> bytes:
    if not is_ascii_printable(filename):
        raise TFTPValueError(f"Invalid filename: {filename}. Not ASCII printable.")
    
    filename_bytes = filename.encode() + b'\x00'
    mode_bytes = mode.encode() + b'\x00'
    fmt = f'!H{len(filename_bytes)}s{len(mode_bytes)}s'

    return struct.pack(fmt, RRQ, filename_bytes, mode_bytes)
#:

def unpack_rrq(packet) -> tuple[str, str]:
    return _unpack_rrq_wrq(RRQ, packet)
#:

def unpack_wrq(packet) -> tuple[str, str]:
    return _unpack_rrq_wrq(WRQ, packet)
#:

def _unpack_rrq_wrq(opcode: int, packet: bytes) -> tuple[str, str]:
    received_opcode = unpack_opcode(packet)
    if opcode != received_opcode:
        raise TFTPValueError(f'Invalid opcode: {received_opcode}. Expected opcode: {opcode}')
    delim_pos = packet.index(b'\x00', 2)
    filename = packet[2: delim_pos].decode()
    mode = packet[delim_pos+1:-1].decode()
    return filename, mode
#:

def unpack_opcode(packet: bytes) -> int:
    opcode, *_ = struct.unpack('!H', packet[:2])
    if opcode not in (RRQ, WRQ, DAT, ACK, ERR):
        raise TFTPValueError(f"Invalid opcode {opcode}")
    return opcode
#:

# struct RRQ {
#     unsigned short int opcode;
#     unsigned char* filename;
#     unsigned char* filename;
# };

# struct DAT {
#     unsigned short int opcode;
#     unsigned short int block_number;
#     unsigned char data[512];
# };

###################################
##
##  ERRORS AND EXCEPTIONS
##
###################################

class TFTPValueError(ValueError):
    pass
#:

###################################
##
##  COMMON UTILITIES
##
###################################

def is_ascii_printable(txt: str) -> bool:
    return set(txt).issubset(string.printable)
#:

