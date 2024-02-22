"""

(c) 2024 Rodrigo Nunes, Henrique Saraiva

Código fonte de acordo com a licença GPL3. Deverá consultar:
    https://www.gnu.org/licenses/gpl-3.0.en.html

"""

## tftp.py
## Código comum ao cliente e servidor. Deve incluir aqui o código para gerar os pacotes e para gerir o envio de um ficheiro e a recepção de um ficheiro.


###################################
##
##  SEND AND RECEIVE FILES
##
###################################

INET4Address = tuple[str, int]      # TCP/UDP address => IPv4 and port

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

