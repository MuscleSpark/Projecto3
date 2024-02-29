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

from tftp import get_file 


def main():
    ## Define args with docopt
    args = docopt(f"""
    TFTPy - Cliente TFTP em Python

    Usage:
        client.py (-h | --help)
        client.py [-p SERV_PORT] <server>
        client.py (get | put) [-p SERV_PORT] <server> <source_file> [dest_file]

    Required:
        get                                         Downloads file from server
        put                                         Uploads file to server

    Arguments:
        server                                      Server IP
        source_file                                 Source file
        dest_file                                   Optional destination file

    Options:
        -h, --help                                  Show this screen.
        -p SERV_PORT, --port=SERV_PORT              Choose port to connect to [default: 69]
    
    """)


## Setting defaults if no option given
#    if args['serv_port'] == None: args['serv_port'] = '69'
    if args['dest_file'] == None: args['dest_file'] = args['source_file']


## Debugging docopt
    print(args)
    print()

    if args['get']:
        print("GET")
    elif args['put']:
        print("PUT")
    else:
        exec_tftp_shell(args['<server>'], int(args['--port']))

"""
Add TRY EXCEPT
"""


def exec_tftp_shell(server: str, server_port: int):
    print(f"Exchanging files with server '{server}' (<ip do servidor>)")
    print(f"Server port is {server_port}\n")

    while True:
        cmd = input("tftpy client> ")

        match cmd:
            case 'help':
                print(textwrap.dedent(
                    """
                    Commands:
                    """
                ))
            case 'get':
                print("GET (shell)")
            case 'put':
                print("PUT (shell)")
            case 'quit':
                print("Exiting TFTP client.")
                print("Goodbye!")
                sys.exit(0)
            case _:
                print(f"Unknown command: '{cmd}'")
#:


def clear_screen():
    if os.name == 'posix':
        subprocess.run(['clear'])
    elif os.name == 'nt':
        subprocess.run(['cls'], shell=True)

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

