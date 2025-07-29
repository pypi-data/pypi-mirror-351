## SentinelC App Library

Tooling used to validate, create and publish an app libary feed for the SentinelC platform.

Published applications are importable into a SentinelC cloud controller, browsable in the web app and deployable to appliances using a simple click-through form.

For an example structure of an app libary that uses the tooling provided by this project, see [Demo App Library](https://gitlab.com/sentinelc/app-library-demo/).

## Specification of an app library structure

### General files hierarchy

- `manifests/`: Contains all apps
  - `app1`: Unique name of the app
    - `app1.yml`: App description and parameters (description file)
    - `app1-fr.yml`: Optional translation
    - `app1.kube.yml`: Kubectl YAML as a jinja template
    - `README.md`: Full description of the app
    - `README-fr.md`: Translated full description
  - `app2`
    - `...`


### Description file

*{app}.yml in the root of the manifest*

The description file (app1.yml) contains the information required to generate the application entry in the app library. 

- **display_name**: Application name (translatable)
- **description**: Short description of the app (translatable)
- **homepage**: Official URL of the app.
- **documentation**: Optional URL of the app's documentation.
- **category**: Tag used to categorize the app.
- **version**: Version string of the app.
- **architectures**: List of supported architectures. See [architectures](#architectures) below.
- **requirements**: Storage and memory requirements. See [requirements](#requirements) below. 
- **vars**: List of installation variables. See [variables](#variables) below.
- **networks**: Network settings. See [networks](#networks) below.
- **cloud_proxy**: Enable cloud proxy access. See [cloud proxy](#cloud-proxy) below.

Basic example:

```yaml
display_name: My App
description: Show description of my app.
category: demo
version: "1.0.0"
architectures:
    - amd64
vars:
  var_key:
    label: Test var
networks:
  default:
    type: VLAN
    description: Choose the zone/vlan in which the service will be launched.
cloud_proxy:
  port: 80
```

#### Architectures

List of compatible/supported architectures. Possible values:

- `amd64`
- `arm64`

This indicates that the app has been tested as compatible with these architectures.

All the container images used by the recipe should support the defined architectures.
See https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/ for more details.

#### Requirements

You can add hints to your users regarding the disk space and memory requirement for an application.

These are not hard-limits, they will only be shown as a warning a installation time.

Example values:

```yaml
requirements:
  storage: 5000Mb
  memory: 64Gb
```

The values are parsed using the humanfriendly python library. See documentation of the
[parse_size](https://humanfriendly.readthedocs.io/en/latest/api.html#humanfriendly.parse_size) function for details.

#### Variables

This is used to parameterize the individual instances of the application that will be deployed.

Anything that must or can differ from an instance to another should be defined as a variable.

| Field name   | Type         | Valid values                                             | Default         | Notes                                                                                                                                                                        |
|--------------|--------------|----------------------------------------------------------|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| key          | String       | `[a-z_]+`                                                |                 | Name used inside the kube template.                                                                                                                                          |
| type         | String       | text, checkbox, number, password, email, url,  textarea. | text            | Check the next table to learn more.                                                                                                                                          |
| label        | Translatable |                                                          | Capitalized key | The field label to display in the user form.                                                                                                                                 |
| description  | Translatable |                                                          |                 | Help text for the field. Optional                                                                                                                                            |
| required     | Boolean      |                                                          | false           | Field cannot be empty. If type is checkbox, it must be checked.                                                                                                              |
| regexp       | String       | Python regular expression                                | none            | Value must match the regexp. See django RegexpValidator                                                                                                                      |
| default      | String       |                                                          | empty           | A default value. Can be in function(param) format. See supported default functions.                                                                                          |
| auto         | Boolean      |                                                          | false           | Indicates this field is fully auto-generated using the `default` field.                                                                                                      |
| secret       | Boolean      |                                                          | false           | Indicates this field is not visible to the user. If auto is false, it is user-provided on creation only, then hidden. If auto is true, it is not visible to the user at all. |
| immutable    | Boolean      |                                                          | false           | The value cannot be changed after creation of the service. This is implied if auto is true.                                                                                  |
| reveal_once  | Boolean      |                                                          | false           | Indicates if a secret field should be revealed during the pod creation process.                                                                                              |

Here is listed all "type" fields. All inputs are strings and some are converted during the creation of the template. 

| Value    | Type returned | Note                                                                                                                                                                |
|----------|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Checkbox | Bool          | Returns yaml bool "true" if ticked, else "false". If required, must be ticked.                                                                                      |
| Email    | String        | Any acceptable email as per defined in [RFC 3696-3](https://www.rfc-editor.org/rfc/rfc3696#section-3)                                                               |
| URL      | String        | Any acceptable url as per [RFC 1034](https://www.rfc-editor.org/rfc/rfc3696) & [RFC 1738](https://www.rfc-editor.org/rfc/rfc1738). Must use HTTP or HTTPS protocol. |
| Number   | Decimal       | Accepts any decimal number and returns a python Decimal.                                                                                                                     |
| text     | String        | Any string.                                                                                                                                                         |
| textarea | String        | Any string, including newlines `\n`.                                                                                                                                |
| Password | String        | Any string.                                                                                                                                                         |



*Variable example: Most basic*

```yaml
vars:
  my_var:
```

Is expanded to:

```yaml
vars:
  my_var:
    type: text
    label: my_var
    description: null
    required: false
    regexp: null
    default: ""
    auto: false
    secret: false
    immutable: false
```

*Variable example: A default/initial password that the user can override*

```yaml
vars:
  initial_admin_password:
    description: The initial admin user password you will use to connect to the admin panel after installation.
    required: true
    default: random_hex(12)
    immutable: true
```

*Variable example: A default/initial password that the user can see but not change*

note: immutable is implied to true for all auto field.

```yaml
vars:
  initial_admin_password:
    description: Use this password to login the admin panel for the first time.
    auto: true
    default: random_hex(12)
```

*Variable example: An internal secret that the user does not need to know about*

```yaml
vars:
  mysql_password:
    auto: true
    default: random_hex(32)
    secret: true
```

*Variable example: An initial password that the user can see and override on creation only*

Since `auto` is not set to true, the user will be asked to fill the field even if `secret` is true.

```yaml
vars:
  initial_password:
    default: random_hex(32)
    secret: true
    immutable: true
```

#### Default generators

The default value can be generated using a function. The following default generators are available:

| Generator  | Description                                                                                   | Example                           |
|------------|-----------------------------------------------------------------------------------------------|-----------------------------------|
| random_hex | Generates a random hexadecimal string of a specified length.                                  | `random_hex(12)`                  |
| get_device_attribute           | Copy an attribute or nested attribute from the device on which the service will be installed. | `get_device_attribute(device_id)` |


#### Networks

This section allows to configure how you want the networking for the pod to be configured.

This section is optional. If you do not define any network and you do not enable hostNetwork in the kube spec file,
a default VLAN network named `default` will be automatically added to your recipe.

Behind the scene, this feature will auto-configure CNI networks using the appropriate plugins.

**VLAN networks**

This is the default network type. It will launch the app inside a SentinelC VLAN (also known as a Zone). The 
specific vlan is chosen at installation time.

You may define more than one VLAN network. In this case the user will be asked to select multiple vlans when
installing. For example, this could be used to create a proxy service that allows traffic from one vlan to 
another, or simply to expose a service to multiple vlans.

For each VLAN network, a random mac address will be generated, and a free static IP address within the
vlan subnet will be assigned. Inside the container, your app will see a virtual network interface named
eth0 for the first network, eth1 for the second, etc.

All the settings of the VLAN network will apply, just like if the service was a normal client device connected
to this vlan. This includes DNS settings, QoS limits, internet access, intra-vlan networking, security profiles, etc.

You may explicitly declare on which ports your service is listening using the `expose` attribute. This is only
for informational purposes. It will be visible on the service details page to help users understand
how your service is meant to be accessed.

The actual exposed/reachable ports depends entirely on how your specific service behaves. If your app 
listens to 0.0.0.0, it will be reachable from all VLAN networks. Otherwise, you must 
configure your application to listen on the correct network interface(s) only. You can even configure extra 
firewall rules (using iptables or nftables) from a startup script to further limit traffic.

Example:

```yaml
networks:
  my-vlan:
    type: VLAN
    description: Choose a VLAN where the server will be launched.
    expose:
      - 3000/tcp
```

**PORT networks**

This uses the `host-device` CNI plugin to dedicate a network interface to the Pod. The interface is moved from the 
Host network stack to the Pod's network stack and is fully dedicated. Inside the Pod, the interface will be renamed
`eth0`, `eth1`, etc. depending on the ordering.

```yaml
networks:
  dedicated:
    type: PORT
    description: Choose an ethernet port for running our special operation.
```

This is a specialized use case for running traffic capture or whenever direct, full access to a port is required. You
would typically also pair this with a standard VLAN network if you need a reliable internet connection. Otherwise,
the service is responsible for fully initializing the network interface, using DHCP for example.

**Host networking**

Recipes can also opt to use the host's networking stack, i.e., no network isolation at all. Host networking cannot be
mixed with isolated CNI networking as described above.

To use host networking, simply omit the `networks` section from the recipe info file, and add the standard
hostNetwork property to the pod spec file. For example:


```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello-world
spec:
  hostNetwork: true
  containers:
  - image: docker.io/library/hello-world:latest
    name: hello-world
status: {}
```

#### Cloud proxy

A cloud proxy with authentication can automatically be setup at installation time. To enable the feature, simply define
the network and port to expose. Your app must listen for HTTP traffic on the port.

Example:

```yaml
networks:
  my-vlan:
    type: VLAN
    description: Choose a VLAN where the server will be launched.
cloud_proxy:
  network: my-vlan
  port: 80
  protect_from_vlan: true
```

In this example, we create a VLAN network named `my-vlan`, then map a cloud proxy to port 80 of this vlan network.

This means that the service is expected to listen on port 80 of either `0.0.0.0` (all networks, the default for most 
apps). Since the `my-vlan` network will be mapped to `eth0` within the service, you could also configure your service
to listen on `eth0` only.

The `protect_from_vlan` is optional and defaults to `true`. It is used the automatically block other VLAN clients
from accessing this port.

This will add firewall rules on the host machine to block normal VLAN clients from accessing the port
80 directly, reserving it solely for the cloud proxy (remote) access.

The `protect_from_vlan` flag is meant for the typical use-case where you want the web application to be *only*
accessible remotely using the secure cloud proxy feature, and you don't want a local untrusted device on the LAN
to access the web interface directly. If you omit this option, it defaults to true, which is secure by default. 

*Warning*: When using multiple VLAN networks, it is the recipe creator's responsibility to ensure the app is not
reachable on the other networks. The `protect_from_vlan` option only applies to the network and port number targeted by
the cloud proxy.

### Kube template file

*{app}.kube.yml in the app folder*

The kube file (app1.kube.yml) contains the yaml description of the pod with placeholders.

The file is in jinja2 template format.


## Using this tool

### Locally using docker

Official docker images are published on each release of this repository to the gitlab.com docker registry.

Run the image using a command such as:

```
cd my-app-feed/
docker run --rm -it -v .:/mnt/work registry.gitlab.com/sentinelc/app-library-builder:v3.0.0 bash
cd /mnt/work
applib-builder --help
```

Once inside the container, all the applib-* tools will be available (see below).


### Locally using a python virtual env

The tools are also published to PyPi: https://pypi.org/project/sentinelc-appfeed/

A common way to install them would be to use a virtual env.

```bash
python3 -m venv env
source env/bin/activate
pip install sentinelc-appfeed
cd /some/where/my-app-feed/
applib-builder --help
```

### Automate with gitlab-ci in a custom app library

It is possible to fully automate the validation, build and publishing steps for your custom app feed.

The [demo repository](https://gitlab.com/sentinelc/app-library-demo) contains a `.gitlab-ci.yml` file you can use as a starting point.

Forking the demo repository is an easy way to get started. Otherwise, copy the `.gitlab-ci.yml` and add your own manifests.

Once your final JSON feed is published, you will need to subscribe your SentinelC cloud controller to your custom app feed:

https://sentinelc.com/docs/technical-guides/service-library


## List of tools

All tools have a help section by using the -h or --help flag.

### applib-builder

```bash
  Creates a JSON file containing the valid apps located inside the manifest folder

  how to use
  -------------

  `applib-builder`
  Creates a feed based on the ./manifest folder and output the feed as ./feed/demo-feed.yml

  `applib-builder -p newmanifest -o customfeed -f feed.yml`
  Creates a feed based on the ./newmanifest folder and output the feed as ./customfeed/feed.yml
```

### applib-validator

```bash
  Validates the folder hiearchy and values of a specific app in the manifest
          
  how to use
  ------------
  `applib-validator newapp`
  Validates the `newapp` app located inside the ./manifests folder
  
  `applib-validator -p newmanifest newapp`
  Validates the `newapp` app located inside the ./newmanifest folder
```

