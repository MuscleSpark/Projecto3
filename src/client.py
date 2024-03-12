#!/usr/bin/env python3
"""

(c) 2024 Rodrigo Nunes, Henrique Saraiva

Código fonte de acordo com a licença GPL3. Deverá consultar:
    https://www.gnu.org/licenses/gpl-3.0.en.html

"""

## client.py

## Import necessary (maybe) libraries
import os
import sys
import subprocess
import textwrap
from docopt import docopt

from tftp import get_file, put_file
import socket


def main():
    ## Define args with docopt
    args = docopt(f"""
    TFTPy - Cliente TFTP em Python

    Usage:
        client.py (-h | --help)
        client.py [-p SERV_PORT] <server>
        client.py (get | put) [-p SERV_PORT] <server> <source_file> [<dest_file>]

    Required:
        get                                         Downloads file from server
        put                                         Uploads file to server

    Arguments:
        server                                      Server IP
        source_file                                 Source filename
        dest_file                                   Optional destination filename

    Options:
        -h, --help                                  Show this screen.
        -p SERV_PORT, --port=SERV_PORT              Choose port to connect to [default: 69]
    
    """)


## Setting defaults if no option given
#    if args['serv_port'] == None: args['serv_port'] = '69'
    source_file = args['<source_file>']
    dest_file = args['<dest_file>']
    if dest_file is None: dest_file = source_file


## Debugging docopt
    print(args)
    print()

    if args['get']:
        get_file((args['<server>'], int(args['--port'])), source_file, dest_file)
    elif args['put']:
        put_file((args['<server>'], int(args['--port'])), source_file, dest_file)
    else:
        exec_tftp_shell(args['<server>'], int(args['--port']))

"""
Add TRY EXCEPT
"""


def exec_tftp_shell(server: str, server_port: int):
    print(f"Exchanging files with server '{server}' ({socket.gethostbyname(server)})")
    print(f"Server port is {server_port}\n")

    while True:
        cmd = input("tftpy client> ")
        cmd = cmd.split()
        cmd = cmd + None + None
        print(cmd)

        match cmd[0]:
            case 'help':
                print(textwrap.dedent(
                    """
                    Commands:
                        get source_file [destination_file] - get a source_file from server and save it as destination_file
                        put source_file [destination_file] - send a source_file to server and store it as destination_file
                        dir                                - obtain a listing of remote files
                        quit | exit | bye                  - exit TFTP client
                    """
                ))
            case 'get':
                get_file((server, server_port), cmd[1], cmd[2])
            case 'put':
                put_file((server, server_port), cmd[1], cmd[2])
            case 'dir':
                get_file((server, server_port), b'', )
            case 'quit' | 'exit' | 'bye':
                print("Exiting TFTP client.")
                print("Goodbye!")
                sys.exit(0)
            case _:
                print(f"Unknown command: '{cmd}'. Try 'help'?")
#:


def clear_screen():
    if os.name == 'posix':
        subprocess.run(['clear'])
    elif os.name == 'nt':
        subprocess.run(['cls'], shell=True)
    else:
        pass

# ## Summon respective functions based on arguments
#     rules = [not args['--contents'],
#          not args['--name'],
#          not args['--extension'],
#          not args['--regex']]
    
#     if all(rules):
#         print("No options will use --name")
#         name(args['<dir>'])
#     else:
#         if args['--contents'] == True: contents(args['<dir>'])
#         if args['--name'] == True: name(args['<dir>'])
#         if args['--extension'] == True: extension(args['<dir>'])
#         if args['--regex'] != None: regex(args['<dir>'], args['--regex'])

#     print("\nTask complete.")
#:



if __name__ == "__main__":
    main()

