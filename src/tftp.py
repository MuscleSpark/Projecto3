"""

(c) 2024 Rodrigo Nunes, Henrique Saraiva

Código fonte de acordo com a licença GPL3. Deverá consultar:
    https://www.gnu.org/licenses/gpl-3.0.en.html

"""

## tftp.py
## Código comum ao cliente e servidor. Deve incluir aqui o código para gerar os pacotes e para gerir o envio de um ficheiro e a recepção de um ficheiro.

import socket
import string
import struct
import ipaddress
import re
from enum import IntEnum

###################################
##
## PROTOCOL CONSTANTS AND TYPES
##
###################################

MAX_DATA_LEN = 512              # bytes
MAX_BLOCK_NUMBER = 2**16-1      # 0...65535
INACTIVITY_TIMEOUT = 25.0       # seconds
DEFAULT_MODE = 'octet'
DEFAULT_BUFFER_SIZE = 8192      # bytes

class TFTPOpcode(IntEnum):
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

INET4Address = tuple[str, int]      # TCP/UDP address => IPv4 and port

###################################
##
##  SEND AND RECEIVE FILES
##
###################################

# sock.sendto(rrq, server_addr)
# packet, addr = sock.recvfrom(8192)
# ack = pack:ack(1)
# sock.sendto(ack, addr)
# packet, addr = sock.recvfrom(8192)

# sock.settimeout(value)
# sock.close()

def get_file(server_addr: INET4Address, filename: str):
    """
    Get the remote file given by 'filename' through a TFTP RRQ connection to remote server at 'server_addr'.
    """
    print(f"Download file {filename} from {server_addr} ")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(INACTIVITY_TIMEOUT)
        with open (filename, 'wb') as out_file:
            rrq = pack_rrq(filename)
            next_block_number = 1
            sock.sendto(rrq, server_addr)

            while True:
                packet, server_addr = sock.recvfrom(DEFAULT_BUFFER_SIZE)
                opcode = unpack_opcode(packet)

                match opcode:
                    case TFTPOpcode.DAT:
                        block_number, data = unpack_dat(packet)
                        if block_number not in (next_block_number, next_block_number -1):
                            err_msg = (
                                f"Unexpected block number: {block_number}. Expecting one of "
                                f"{next_block_number} or {next_block_number - 1}"
                            )
                            raise ProtocolError(error_msg)

                        if block_number == next_block_number:
                            out_file.write(data)
                            next_block_number += 1

                        ack = pack_ack(block_number)
                        sock.sendto(ack, server_addr)

                        if len(data) < MAX_DATA_LEN:
                            print(f"Download finished.")
                            break

                    case TFTPOpcode.ERR:
                        error_code, error_msg = unpack_err(packet)
                        raise Err(error_code, error_msg)
                    
                    case _:
                        err_msg = f"Invalid packet opcode: {opcode}. Expecting {TFTPOpcode.DAT=}."
                        raise ProtocolError(err_msg)

#:

def put_file(server_addr: INET4Address, filename: str):
    print(f"Upload file {filename} to {server_addr} ")
#:

###################################
##
##  PACKET PACKING AND UNPACKING
##
###################################

#####
# Pack RRQ/WRQ
#####

def pack_rrq(filename: str, mode: str = DEFAULT_MODE):
    return _pack_rrq_wrq(TFTPOpcode.RRQ, filename, mode)
#:

def pack_wrq(filename: str, mode: str = DEFAULT_MODE):
    return _pack_rrq_wrq(TFTPOpcode.WRQ, filename, mode)
#:

def _pack_rrq_wrq(opcode: int, filename: str, mode: str = DEFAULT_MODE) -> bytes:
    if not is_ascii_printable(filename):
        raise TFTPValueError(f"Invalid filename: {filename}. Not ASCII printable.")
    filename_bytes = filename.encode() + b'\x00'
    mode_bytes = mode.encode() + b'\x00'
    fmt = f'!H{len(filename_bytes)}s{len(mode_bytes)}s'
    return struct.pack(fmt, TFTPOpcode.RRQ, filename_bytes, mode_bytes)
#:

#####
# Unpack RRQ/WRQ
#####

def unpack_rrq(packet: bytes) -> tuple[str, str]:
    return _unpack_rrq_wrq(TFTPOpcode.RRQ, packet)
#:

def unpack_wrq(packet: bytes) -> tuple[str, str]:
    return _unpack_rrq_wrq(TFTPOpcode.WRQ, packet)
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

#####
# DAT
#####

def pack_dat(block_number: int, data: bytes) -> bytes:
    if not 0 <= block_number <= MAX_BLOCK_NUMBER:
        err_msg = f'Invalid block {block_number} larger than allowed /{MAX_BLOCK_NUMBER}'
        raise TFTPValueError(err_msg)
    if len(data) > MAX_DATA_LEN:
        err_msg = f'Data size {block_number} larger than allowed /{MAX_DATA_LEN}'
        raise TFTPValueError(err_msg)
    fmt = f'!HH{len(data)}s'
    return struct.pack(fmt, TFTPOpcode.DAT, block_number, data)
#:

def unpack_dat(packet: bytes) -> tuple[int, bytes]:
    opcode, block_number = struct.unpack('!HH', packet[:4])
    if opcode != TFTPOpcode.DAT:
        raise TFTPValueError(f'Invalid opcode {opcode}. Expecting {TFTPOpcode.DAT=}.')
    return block_number, packet[4:]
#:

#####
# ACK
#####

def pack_ack(block_number: int) -> bytes:
    if not 0 <= block_number <= MAX_BLOCK_NUMBER:
        err_msg = f'Invalid block {block_number} larger than allowed /{MAX_BLOCK_NUMBER}'
        raise TFTPValueError(err_msg)
    return struct.pack(f'!HH', TFTPOpcode.ACK, block_number)
#:

def unpack_ack(packet: bytes) -> int:
    opcode, block_number = struct.unpack('!HH', packet)
    if opcode != TFTPOpcode.ACK:
        err_msg = f'Invalid opcode {opcode}. Expecting {TFTPOpcode.ACK=}.'
        raise TFTPValueError(err_msg)
    return block_number
#:

#####
# ERR
#####

def pack_err(error_code: int, error_msg: str | None = None) -> bytes:
    if error_msg not in ERROR_MESSAGES:
        raise TFTPValueError(f'Invalid error code {error_code}')
    if error_msg is None:
        error_msg = ERROR_MESSAGES[error_code]
    error_msg_bytes = error_msg.encode() + b'\x00'
    fmt = f'!HH{len(error_msg_bytes)}s'
    return struct.pack(fmt, TFTPOpcode.ERR, error_code, error_msg_bytes)
#:

def unpack_err(opcode: int, packet: bytes) -> tuple[str, str]:
    opcode, error_code = struct.unpack('!HH', packet[:4])
    if opcode != TFTPOpcode.ERR:
        raise TFTPValueError(f'Invalid opcode: {opcode}. Expected opcode: {TFTPOpcode.ERR=}')
    return error_code, packet[4:-1].decode()
#:

#####
# OPCODE
#####

def unpack_opcode(packet: bytes) -> int:
    opcode, *_ = struct.unpack('!H', packet[:2])
    if opcode not in (TFTPOpcode.RRQ, TFTPOpcode.WRQ, TFTPOpcode.DAT, TFTPOpcode.ACK, TFTPOpcode.ERR):
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

class NetworkError(Exception):
    """
    Any network error, like "host not found", timeouts, etc.
    """
#:

class ProtocolError(NetworkError):
    """
    A protocol error like unexpected of invalid opcode, wrong block number, or any other invalid protocol parameter.
    """
#:

class Err(Exception):
    """
    An error sent by the server. It may be caused because a read/write can't be processed. 
    Read and write errors during file transmission also cause this message to be sent,
    and transmission is then terminated.
    The error number gives a numeric error code, 
    followed by an ASCII error message that might contain additional, 
    operating system specific information.
    """
    def __init__(self, error_code: int, error_msg: str):
        super().__init__(f'TFTP Error {error_code}')
        self.error_code = error_code
        self.error_msg = error_msg
    #:
#:


###################################
##
##  COMMON UTILITIES
##
###################################

def _make_is_valid_hostname():
    allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    def _is_valid_hostname(hostname):
        """
        From: http://stackoverflow.com/questions/2532053/validate-a-hostname-string
        See also https://en.wikipedia.org/wiki/Hostname (and the RFC referenced there)
        """
        if not 0 < len(hostname) <= 255:
            return False
        print(len(hostname))
        if hostname[-1] == ".":
            # strip exactly one dot from the right, if present
            hostname = hostname[:-1]
        return all(allowed.match(x) for x in hostname.split("."))
    return _is_valid_hostname
#:
is_valid_hostname = _make_is_valid_hostname()

def get_host_info(server_addr: str) -> tuple[str, str]:
    """
    Returns the server ip and hostname for server_addr. 
    This param may either be an IP address, 
    in which case this function tries to query its hostname or vice versa.
    This function raises a ValueError exception if the host name in server_addr is ill-formed, 
    and raises NetworkError if we can't get an IP address for that host name.
    """
    try:
        ipaddress.ip_address(server_addr)
    except ValueError:
        # server_addr not a valid ip address, then it might be a valid hostname
        if not is_valid_hostname(server_addr):
            raise ValueError(f"Invalid hostname: {server_addr}.")
        server_name = server_addr
        try:
            # gethostbyname_ex returns the following tuple:
            # (hostname, aliaslist, ipaddrlist)
            server_ip = socket.gethostbyname_ex(server_name)[2][0]
        except socket.gaierror:
            raise NetworkError(f"Unknown server: {server_name}.")
    else:
        # server_addr is a valid ip address, get the hostname if possible
        server_ip = server_addr
        try:
            # returns a tuple like gethostbyname_ex
            server_name = socket.gethostbyaddr(server_ip)[0]
        except socket.herror:
            server_name = ''
    return server_ip, server_name
#:

def is_ascii_printable(txt: str) -> bool:
    return set(txt).issubset(string.printable)
#:
