#!/usr/bin/env python3

import requests
import argparse
import sys

def get_calling_conventions_for_all_archs():
    url = 'https://api.syscall.sh/v1/conventions'

    headers = {'accept': 'application/json'}
    req = requests.get(url, headers=headers)

    if req.status_code != 200:
        print(f'Failed fetching API at "{url}" - HTTP Status {req.status_code}', file=sys.stderr)
        sys.exit(1)
    
    return req.json()


def search_syscall(arch, syscall_name_or_number):
    base_url = 'https://api.syscall.sh/v1/syscalls/'
    headers = {'accept': 'application/json'}
    req = requests.get(f'{base_url}{syscall_name_or_number}', headers=headers)

    if req.status_code != 200:
        print(f'Failed fetching API at "{base_url}{syscall_name_or_number}" - HTTP Status {req.status_code}', file=sys.stderr)
        sys.exit(1)

    response = req.json()

    if arch == 'all':
        return response
    
    response_list = list()

    for item in response:
        if item['arch'] == arch or arch == 'all':
            response_list.append(item)
    
    return response_list


def print_response_list(response_list, calling_conventions, color):
    def colorize_or_not(mystr):
        if color:
            return f'\033[0;32m{mystr}\033[0m'
        else:
            return mystr
    
    # Not checking for archs that does not exist
    def get_calling_convention_for(arch):
        for item in calling_conventions:
            if item['arch'] == arch:
                return item
        
        return None
    
    def get_arguments_string_for(item):
        prototype = f"{item['name']}("
        arguments_string = ''

        for arg in ('arg0', 'arg1', 'arg2', 'arg3', 'arg4', 'arg5'):
            if item[arg] != '':
                arguments_string += f"{get_calling_convention_for(item['arch'])[arg]} <- {colorize_or_not(item[arg])}\n"
                prototype += f"{item[arg]}, "
        
        prototype += '\b\b);'
        arguments_string += f'\nPrototype: {prototype}'

        return arguments_string


    for item in response_list:
        # item['arg0'] == 'unsigned int fd'
        pretty_str = f'''
Architecture: {colorize_or_not(item['arch'])}
Name: {colorize_or_not(item['name'])}
Syscall Number: {colorize_or_not(item['nr'])} ( {colorize_or_not(hex(item['nr']))} )


{get_calling_convention_for(item['arch'])['nr']} <- {item['nr']}
{get_arguments_string_for(item)}
Return is on: {colorize_or_not(get_calling_convention_for(item['arch'])['return'])}
----------------------------
'''
        print(pretty_str)
            


def main():
    parser = argparse.ArgumentParser(
        prog='search_syscall',
        description='search api.syscall.sh for informations about a specific syscall name or number',
        epilog='License: GPLv3'
    )

    parser.add_argument('-a', '--arch',
        help='architecture that you are working on',
        choices=['all', 'x64', 'x86', 'arm', 'arm64'],
        default='all'
    )
    parser.add_argument('-s', '--search',
        help='syscall number or name to search',
        required=True
    )
    
    parser.add_argument('-c', '--color',
        help='specify to use colors on terminal or not',
        default=False,
        action="store_true"
    )

    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)

    args = parser.parse_args(sys.argv[1:])

    response_list = search_syscall(args.arch, args.search)
    calling_conventions = get_calling_conventions_for_all_archs()
    print_response_list(response_list=response_list, calling_conventions=calling_conventions, color=args.color)



if __name__ == '__main__':
    main()