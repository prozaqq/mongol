import json
import nmap
import sys
import argparse
import pymongo


def save(filename, str, ip):
    with open(filename,'a+') as file:
        file.write('Host - {}\n\n'.format(ip))
        file.write('{}\n\n'.format(str))


def check_args(args=None):
    parser = argparse.ArgumentParser(description='A tool to enumerate MongoDB databases without authentication')
    parser.add_argument('-l', '--log', action='store_true',help='log exceptions into a text file')
    parser.add_argument('-o', '--output', action='store_true', help='save successful enumerations to a text file')
    parser.add_argument('-f', '--file', help='network list file path', default='')
    parser.add_argument('-net', '--network', help='network to scan / for example \"192.168.0.1/24\"', default='')
    parser.add_argument('-v', '--verbose', action='store_true', help='prints exceptions to screen')

    results = parser.parse_args(args)
    return results.log, results.output, results.file, results.network, results.verbose


def check_open(hosts):
    for host in hosts:
        if host not in ip_list and nm[host]['tcp'][27017]['state'] == 'open':
            ip_list.append(host)
            print('[+] {} - {} / open'.format(host, PORT))


def scan_file(file):
    print('[!] Starting a network scan from a file ...')
    cidr_list = open(filename).read().splitlines()
    for cidr in cidr_list:
        print('[!] Scanning - {}'.format(cidr))
        nm.scan(cidr, PORT)
        check_open(nm.all_hosts())


def scan_network(network):
    print('[!] Starting a single network scan ...')
    print('[!] Scanning - {}'.format(network))
    nm.scan(network, PORT)
    check_open(nm.all_hosts())


if __name__ == "__main__":

    log, output, filename, network, verbose = check_args(sys.argv[1:])

    PORT = '27017'

    ip_list = []
    nm = nmap.PortScanner()

    if len(filename) > len(network):
        scan_file(filename)
    else:
        scan_network(network)

    # Connect and enumerate dbs and collections

    for ip in ip_list:
        try:
            client = pymongo.MongoClient(ip, 27017, maxPoolSize=50)
            d = dict((db, [collection for collection in client[db].list_collection_names()])
                     for db in client.list_database_names())
            print('[+] Host: {}'.format(ip))
            print('[+] Enumeration:\n')
            for db in d:
                print('{}:'.format(db))
                for collection in d[db]:
                    print('\t{}'.format(collection))
                if output:
                    save('output.txt', json.dumps(d, indent=4, sort_keys=True), ip)
        except (pymongo.errors.ConfigurationError,
                pymongo.errors.OperationFailure,
                pymongo.errors.ServerSelectionTimeoutError) as e:
            if log:
                save('log.txt', e, ip)
            if verbose:
                print('[!] {}'.format(e))
        client.close()

