# Table of contents

 - [Description](#descr)
 - [Installation](#install)
 - [Operation Instructions](#operate)

# <a name="descr"></a>Description
The Sense Workflow tool allows users to deploy and compose sense services by using a yaml based workflow definition.

- For more details, refer to [sense workflow design document](./docs/workflow_design.md)
- Many sample workflow definitions can be found under this directory. 
- For a quick start, you can use the notebook [getting_started_example.ipynb](./notebooks/getting_started_example.ipynb)
- Or use these instructions to exercise the sample workflow under `workflow_examples/basic-stitching/any-to-any-l2vpn`.

```
# Feel free to change the session name specified by the `-s switch option`
>cd workflow_examples/basic-stitching/any-to-any-l2vpn
>sense_workflow.py sessions -show   # show existing sessions.
>sense_workflow.py workflow -s exp-any-to-any-l2vpn -validate
>sense_workflow.py workflow -s exp-any-to-any-l2vpn -plan -summary
>sense_workflow.py workflow -s exp-basic-any-to-any-l2vpn -apply  # create resources
>sense_workflow.py workflow -s exp-basic-any-to-any-l2vpn -show -summary # show state
>sense_workflow.py sessions -show
>sense_workflow.py workflow -s exp-basic-any-to-any-l2vpn -destroy # destroy resources
>sense_workflow.py sessions -show
```

The following snippet of the sample workflow shows how to connect outputs of a resource to another resource.

- Note how service <i>serv1</i> and <i>serv2<i> use ip addresses from pool <i>pool1</i>
- Note how service <i>serv2</i> uses the vlan tag from <i>serv1<i>'s second terminal. 

```
resource:
  - service:
      - pool1:
          pool: AutoGOLE-IPv4-Test-Pool
          addr_type: IPv4
          batch: subnet
          netmask: '/30'
      - serv1:
          profile: Any-to-Any-L2VPN-IPv4
          manifest_template: '{{ manifest_template.nrp_manifest_template }}'
          edit_template:
              data.connections[0].terminals[0].uri: urn:ogf:network:maxgigapop.net:2013:ptxn-sense-v1.maxgigapop.net
              data.connections[0].terminals[1].uri: urn:ogf:network:es.net:2013::star-cr6:2_1_c5_1:+
              data.connections[0].suggest_ip_range[0].start: '{{ service.pool1.hosts[0] }}'
              data.connections[0].suggest_ip_range[0].end: '{{ service.pool1.hosts[0] }}'
              data.connections[0].bandwidth.capacity: 1000
          count: 1
      - serv2:
          profile: Any-to-Any-L2VPN-IPv4
          manifest_template: '{{ manifest_template.nrp_manifest_template }}'
          edit_template:
              data.connections[0].terminals[0].uri: urn:ogf:network:icair.org:2013:mren8700:esnet
              data.connections[0].terminals[1].uri: urn:ogf:network:starlight.org:2022:r740xd4.it.northwestern.edu 
              data.connections[0].suggest_ip_range[0].start: '{{ service.pool1.hosts[1] }}'
              data.connections[0].suggest_ip_range[0].end: '{{ service.pool1.hosts[1] }}'
              data.connections[0].terminals[0].vlan_tag: '{{ service.serv1.manifest.switching_subnets[1].switching_ports[1].tag }}'
              data.connections[0].bandwidth.capacity: 1000
          count: 1
```

# <a name="install"></a>Installation

sense_o_api is available on PyPI.
```
pip install sense_o_api
```


Alternatively, you may install and test using the following commands:
```
pip install -e .
sense_workflow.py --help
sense_workflow.py workflow --help
sense_workflow.py sessions --help
```

# <a name="operate"></a>Operation Instructions
- Sense worflow configuration can be specified across one or more <i>.sense<i> files. The workflow tool assembles all the .sense configuration files and then parses the assembled configuration.  
- The <i>--config-dir</i> switch can be used to specify the configuration directory.  If  not present, the current directory is used. 
- The --var-file option can be used to override the default value of any variable. It consists of a set of key-value pairs with each pair written as ```key: value```. At runtime, all variables found in an assembled configuration must have a value other than ```None```. The parser will halt and throw an exeption otherwise. 
- The --session is a friendly name used to track a given workflow.  
- Use the --help options shown above if in doubt.

```
# Validation
sense_workflow.py --config-dir some_dir [--var-file some_var_file.yml] --session some_session -validate

# Plan
sense_workflow.py workflow --config-dir some_dir [--var-file some_var_file.yml] --session some_session -plan [-summary] [-json]

# Apply
sense_workflow.py --config-dir some_dir [--var-file some_var_file.yml] --session some_session -apply

# View State. 
sense_workflow.py workflow --config-dir some_dir [--var-file some_var_file.yml] --session some_session -show [-summary] [-json]

# Destroy
sense_workflow.py workflow --config-dir some_dir [--var-file some_var_file.yml] --session some_session -destroy

# Use this option to manage your workflow sessions
sense_workflow.py sessions -show
```
