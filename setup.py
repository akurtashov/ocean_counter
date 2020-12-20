import configparser
import os
import argparse

"""

"""
def setup():
    parser = argparse.ArgumentParser(description='Setup initial parameter of ocean_counter project')
    parser.add_argument('-c', default='/etc/ocean_counter.conf', type=str, help='config file name')
    
    args = parser.parse_args()
    
    config_file = args.c

    config = configparser.ConfigParser()
    config.read(config_file)
    ftp_server = config['ftp server']
    
    return (ftp_server.get('ip'), ftp_server.get('login'), ftp_server.get('password'))


if __name__ == '__main__':
    print(setup())
