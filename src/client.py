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
#    print(args)
    print()
    try:
        if args['get']:
            get_file((args['<server>'], int(args['--port'])), source_file, dest_file)
        elif args['put']:
            put_file((args['<server>'], int(args['--port'])), source_file, dest_file)
        else:
            exec_tftp_shell(args['<server>'], int(args['--port']))
    except Exception as Err:
        print(f"Error: {Err}")

"""
Add TRY EXCEPT
"""


def exec_tftp_shell(server: str, server_port: int):
    clear_screen()
    print(f"Exchanging files with server '{server}' ({socket.gethostbyname(server)})")
    print(f"Server port is {server_port}\n")

    while True:
        try:
            cmd = input("tftpy client> ")
            cmd, *args  = cmd.split()
            if len(args) > 0:
                source_file = args[0]
                destination_file = args[1] if len(args) > 1 else source_file

            match cmd:
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
                    if len(args) == 0:
                        print("Usage: get source_file [destination_file] - get a source_file from server and save it as destination_file")
                    else:
                        get_file((server, server_port), source_file, destination_file)
                case 'put':
                    if len(args) == 0:
                        print("Usage: put source_file [destination_file] - send a source_file to server and store it as destination_file")
                    else:
                        put_file((server, server_port), source_file, destination_file)
    #            case 'dir':
    #                get_file((server, server_port), b'', )
                case 'quit' | 'exit' | 'bye':
                    print("Exiting TFTP client.")
                    print("Goodbye!")
                    sys.exit(0)
                case _:
                    print(f"Unknown command: '{cmd}'. Try 'help'?")
        except Exception as e:
            print(f"Error: {e}")
#:


def clear_screen():
    if os.name == 'posix':
        subprocess.run(['clear'])
    elif os.name == 'nt':
        subprocess.run(['cls'], shell=True)
    else:
        pass


if __name__ == "__main__":
    main()

