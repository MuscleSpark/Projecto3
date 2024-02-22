"""

(c) 2024 Rodrigo Nunes, Henrique Saraiva

Código fonte de acordo com a licença GPL3. Deverá consultar:
    https://www.gnu.org/licenses/gpl-3.0.en.html

"""

## tftp.py
## Código comum ao cliente e servidor. Deve incluir aqui o código para gerar os pacotes e para gerir o envio de um ficheiro e a recepção de um ficheiro.

import string
import struct
from socket import socket, AF_INET, SOCK_DGRAM

###################################
##
## PROTOCOL CONSTANTS AND TYPES
##
###################################

MAX_DATA_LEN = 512              # bytes
MAX_BLOCK_NUMBER = 2**16-1      # 0...

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

def unpack_rrq(packet: bytes) -> tuple[str, str]:
    return _unpack_rrq_wrq(RRQ, packet)
#:

def unpack_wrq(packet: bytes) -> tuple[str, str]:
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

##############################################

def pack_dat(block_number: int, data: bytes) -> bytes:
    if not 0 <= block_number <= MAX_BLOCK_NUMBER:
        raise TFTPValueError(f'Invalid block {block_number} larger than allowed /{MAX_BLOCK_NUMBER}')
    if len(data) > MAX_DATA_LEN:
        raise TFTPValueError(f'Data size {block_number} larger than allowed /{MAX_DATA_LEN}')
    fmt = f'!HH{len(data)}s'
    return struct.pack(fmt, DAT, block_number, data)
#:

def unpack_dat(packet: bytes) -> tuple[int, bytes]:
    opcode, block_number = struct.unpack('!HH', packet[:4])
    if opcode != DAT:
        raise TFTPValueError(f'Invalid opcode {opcode}. Expecting {DAT=}.')
    return block_number, packet[4:]
#:

def pack_ack(block_number: int) -> bytes:
    if not 0 <= block_number <= MAX_BLOCK_NUMBER:
        raise TFTPValueError(f'Invalid block {block_number} larger than allowed /{MAX_BLOCK_NUMBER}')
    return struct.pack(f'!HH', ACK, block_number)
#:

def pack_ack(packet: bytes) -> int:
    opcode, block_number = struct.unpack('!HH', packet)
    if opcode != ACK:
        raise TFTPValueError(f'Invalid opcode {opcode}. Expecting {ACK=}.')
    return block_number
#:

#############################################

def pack_err(error_code: int, error_msg: str | None = None) -> bytes:
    if error_msg not in ERROR_MESSAGES:
        raise TFTPValueError(f'Invalid error code {error_code}')
    if error_msg is None:
        error_msg = ERROR_MESSAGES[error_code]
    error_msg_bytes = error_msg.encode() + b'\x00'
    fmt = f'!HH{len(error_msg_bytes)}s'
    return struct.pack(fmt, ERR, error_code, error_msg_bytes)
#:

def unpack_err(opcode: int, packet: bytes) -> tuple[str, str]:
    opcode, error_code = struct.unpack('!HH', packet[:4])
    if opcode != ERR:
        raise TFTPValueError(f'Invalid opcode: {opcode}. Expected opcode: {ERR=}')
    return error_code, packet[4:-1].decode()
#:

#############################################

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

