#!/usr/bin/python

import yaml
import sys

### SETTINGS ###

CONFIGFILE_NAME = 'config.yaml'
SSHCONFIGFILE_LOCATION = './generated_ssh_config'
DEBUG = False

### GENERAL FUNCTIONS ###

def debug(msg):
    """
    Function to dispaly a debug message.
    """
    if DEBUG:
        print( "DEBUG: " + str(msg) )

def error (msg):
    """
    Function to display a error message.
    """
    print( "ERROR: " + str(msg) )
    sys.exit( '1' )

### FUNCTIONS ###

def default_settingshash():
    default_hash = {
            'proxycommand': 'ssh proxyhost -W %h:%p',
            }

def translate_key(key):
    """
    Function to return the correct configuration key.
    If not found return the key itself.
    Returns a string.
    """
    mapping = {
            'user': 'User',
            'identityfile': 'IdentityFile',
            'proxycommand': 'ProxyCommand',
            'ip': 'Hostname',
            'hostname': 'Hostname',
            'port': 'Port',
            }
    if key in mapping:
        return str(mapping[key])
    else:
        return str(key)

def read_configfile(configfile):
    """
    Function to read the configfile.
    Returns a hash.
    """
    debug( 'Reading: ' + configfile )
    with open(configfile, 'r') as stream:
        try:
            confighash = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            error( exc )
    return confighash

def generate_confighash(settingshash, confighash):
    """
    Function to build a hash existing of one level.
    Returns a hash.
    """
    defaults = confighash['default']
    configblock = {}
    for host in confighash['hosts']:

        if 'domain' in confighash['hosts'][host]:
            fqdn = str(host) + '.' + str(confighash['hosts'][host]['domain'])
        else:
            fqdn = str(host) + '.' + str(defaults['domain'])

        if 'proxycommand' in defaults:
            proxycommand = defaults['proxycommand']
        else:
            proxycommand = settingshash['proxycommand']

        if 'host' in confighash['hosts'][host]:
            hostname = confighash['hosts'][host]['host']
            configblock[hostname] = {}
            configblock[hostname]['Hostname'] = fqdn
        else:
            hostname = fqdn
            configblock[hostname] = {}


        for key in confighash['hosts'][host]:
            # Skip not valid configuration functions
            if key in ['host','domain']:
                continue
            if key == 'proxyhost':
                proxyhost = str(confighash['hosts'][host][key]) + '.' + str(defaults['domain'])
                configblock[hostname]['ProxyCommand'] = proxycommand.replace('proxyhost',proxyhost)
            else:
                if not confighash['hosts'][host][key] == '':
                    configblock[hostname][translate_key(key)] = str(confighash['hosts'][host][key])

        for key in defaults:
            # Skip not valid configuration functions
            if key in ['domain','proxycommand']:
                continue
            # Skip already included keys
            elif translate_key(key) in configblock[hostname]:
                continue
            else:
                configblock[hostname][translate_key(key)] = defaults[key]

    return configblock

def overwrite_config(configfile, confighash, seperator):
    """
    Function to write the generated config to the specified file.
    Will overwrite the configuration encapsulated by the HEADER and TAILER.
    """
    debug( 'Writing configblock' )

    config = open( configfile, 'r' ).readlines()
    if seperator in config:
        # Purge old config
        with open( configfile, 'w' ) as f:
            config_include = 1
            for line in config:
                if line == seperator:
                    config_include = -config_include
                    f.write(seperator)
                elif config_include > 0:
                    f.write(line)

        # Insert new config
        config = open( configfile, 'r' ).readlines()
        with open( configfile, 'w' ) as f:
            write_config = 1
            for line in config:
                if line == seperator:
                    write_config = -write_config

                f.write(line)

                if write_config < 0:
                    for host in confighash:
                        configblock = 'Host ' + host + '\n'
                        for key in confighash[host]:
                            configblock += '  ' + key + ' ' + str(confighash[host][key]) + '\n'
                        configblock += '\n'
                        f.write(configblock)
    else:
        with open( configfile, 'a' ) as f:
            f.write(seperator)
            for host in confighash:
                configblock = 'Host ' + host + '\n'
                for key in confighash[host]:
                    configblock += '  ' + key + ' ' + str(confighash[host][key]) + '\n'
                configblock += '\n'
                f.write(configblock)
            f.write(seperator)

def generate_config():
    """
    Function to generate the configuration.
    """
    CONFIG = read_configfile(CONFIGFILE_NAME)

    if not 'settings' in CONFIG:
        settingshash = default_settingshash()
    else:
        settingshash = CONFIG['settings']

    for SECTION in CONFIG:
        if SECTION == 'settings':
            continue

        HEADER = '#===GENERATED_BY_' + SECTION + '===#\n'
        debug( 'Generating configuration for "' + SECTION + '" section' )
        CONFIG_HASH = generate_confighash(settingshash, CONFIG[SECTION])
        overwrite_config(SSHCONFIGFILE_LOCATION, CONFIG_HASH, HEADER)

### MAIN ###

if '__main__' == __name__:
    generate_config()
