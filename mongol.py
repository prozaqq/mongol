import json
import nmap
import sys
import argparse
import pymongo


def save(filename,str,ip):
    with open(filename,'a+') as file:
        file.write('Host - {}\n\n'.format(ip))
        file.write('{}\n\n'.format(str))


def check_args(args=None):
    parser = argparse.ArgumentParser(description='A tool to enumerate MongoDB databases without authentication')
    parser.add_argument('-l','--log',action='store_true')
    parser.add_argument('-o','--output',action='store_true')

    results = parser.parse_args(args)
    return(results.log, results.output)


if __name__ == "__main__":

    log , output = check_args(sys.argv[1:])

    PORT = '27017'

    cidr_list = open('ipblock.txt').read().splitlines()
    ip_list = []
    nm = nmap.PortScanner()

    # Scan

    for cidr in cidr_list:
        print('Scanning - {}'.format(cidr))
        nm.scan(cidr, PORT)

    for host in nm.all_hosts():
        if host not in ip_list and nm[host]['tcp'][27017]['state'] == 'open':
            ip_list.append(host)
            print('[+] {} - {} / open'.format(host, PORT))

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
        client.close()
