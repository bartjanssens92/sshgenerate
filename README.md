# SSH config generator

## Features

 - Takes a yaml file as input to generate sshconfiguration.
 - Does not overwrite existing configuration.
 - Updates the generated config with changes.

## Config

There are 2 config parts to this script:

### Script configuration

Some parameters are set inside the script:

```
### SETTINGS ###

CONFIGFILE_NAME = 'config.yaml'
DEBUG = True
```

The configfile_name parameter sets where to find the configuration yaml file.
Debug enables debugging

### Configfile

The configfile is a yaml formatted file that includes the following sections.

#### Settings

This part configures general settings, currently includes only the proxycommand.
This is a bit special as it replaces the proxyhost string with the supplied on in the host config.

```
settings:
  proxycommand: 'ssh proxyhost -W %h:%p
  debug: False
  sshconfigfile: '/home/username/.ssh/config_test'
```

#### Section

A section allows to split up hosts in logical segments that share the same defaults.
It includes a default key that holds the defaults to set for each host.
Next to that it includes the hosts in the section.

The yaml configuration allows for some shortnames and non capitalized keys.
They are mapped by the script to the correct key. The current complete mapping can be found in the translate_key function.
When in doubt what key to use, use the default ssh configuration format.

```
customer-internal:
  default:
    domain: internal.customer.com
    user: myname_customer
    identityfile: id_rsa_customer
  hosts:
    proxy:
      ip: 1.2.3.4
    foreman: {}
    jenkins:
      hostname: jenkins7
      User: myname_customer_again
    docker:
      proxyhost: proxy
```

The above example will generate the following ssh configuration:
```
#===GENERATED_BY_customer-internal===#
Host proxy.internal.customer.com
  Hostname 1.2.3.4
  User myname_customer
  IdentityFile id_rsa_customer

Host foreman.internal.customer.com
  User myname_customer
  IdentityFile id_rsa_customer

Host jenkins.internal.customer.com
  Hostname jenkins7
  User myname_customer_again
  IdentityFile id_rsa_customer

Host docker.internal.customer.com
  ProxyCommand ssh proxy.internal.customer.com -W %h:%p
  User myname_customer
  IdentityFile id_rsa_customer

#===GENERATED_BY_customer-internal===#
```

## More advanced configuration examples

### Generating wildcard rules

```
---
settings:
  proxycommand: 'ssh proxyhost -W %h:%p'

customer-internal:
  default:
    domain: dev
    proxycommand: 'bash -c "exec ssh proxyhost -W $(basename -s.dev %h).development.customer.be:%p"'
  hosts:
    'proxy':
      host: proxy
      domain: somewhere.over.the.rainbow
      user: another_user
      port: 443
    '*':
      proxyhost: proxy
```

Will create this:
```
#===GENERATED_BY_customer-development===#
Host proxy
  Hostname proxy.somewhere.over.the.rainbow
  User another_user
  Port 443

Host *.dev
  ProxyCommand bash -c "exec ssh proxy.dev -W $(basename -s.dev %h).development.customer.be:%p"

#===GENERATED_BY_customer-development===#
```

