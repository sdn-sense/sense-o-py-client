# Table of contents

 - [Description](#descr)
 - [Stitching Sample Workflow Configuration](#wconfig)
 - [Installation](#install)
 - [Operation Instructions](#operate)
 - [Quick Start](#quickstart)

# <a name="descr"></a>Description
The `Sense Workflow Tool` is a command-line python tool that enables you to define and provision `sense services` using configuration files. It uses a declarative language, which basically means you define the desired state of your workflow and the tool figures out the steps to achieve that state by following this simple procedure that consists of the following three steps. The `Sense Workflow Tool` maintains a state
a state file on disk to track the current state of your workflow, enabling it to understand how to achieve the desired state.

- Step 1: Write
<br>Write your configuration. You can refer to [sense workflow design document](./docs/workflow_design.md) or check out the many example sense workflow configration files ending with the `.sense` extension under the `workflow_examples` directory.
- Step 2: Plan
<br>Use the tool to display its plan to either add or remove `sense services` predicated upon the comparison of your declared workflow and the current state of existing `sense services`.
- Step 3: Apply
<br> Finally, use the tool to accept planned changes to add or remove `sense services`. 

# <a name="wconfig"></a>Stitching Sample Workflow Configuration

The following workflow configuration snippet, though incomplete, consists of three services: a pool `sense service pool`` and two instance `sense services (serv1, serv2)` and shows how to stitch or connect outputs of a service to another service. For example service <i>serv1</i> and <i>serv2<i> use ip addresses from the pool <i>pool1</i> and service <i>serv2</i> uses the vlan tag from <i>serv1<i>'s second terminal.

- The <i>edit_template</i>, not shown here, is used to ovverride the editable fields in a `sense profile`.
- The <i>manifest_template</i>, not shown here, is used to retrieve the desired state of a deployed `sense service`
- For more details, you can refer to [sense workflow design document](./docs/workflow_design.md)

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

# <a name="quickstart"></a>Quick Start

- [ ] Assumes you have installed the `Sense Worflow Tool`
- [ ] Assumes you have configured your `Sense Credentials` (.sense-o-auth.yaml)


The session name `exp-any-to-any-l2vpn` is arbitrarily picked. Feel free to change it. It is used as a prefix to
name the `sense services` and to track the state of the workflow. 

```
>cd workflow_examples/basic-stitching/any-to-any-l2vpn
>sense_workflow.py sessions -show                                           # show existing sessions.
>sense_workflow.py workflow -s exp-any-to-any-l2vpn -validate
>sense_workflow.py workflow -s exp-any-to-any-l2vpn -plan -summary
>sense_workflow.py workflow -s exp-basic-any-to-any-l2vpn -apply            # create services
>sense_workflow.py workflow -s exp-basic-any-to-any-l2vpn -show -summary    # show state
>sense_workflow.py sessions -show
>sense_workflow.py workflow -s exp-basic-any-to-any-l2vpn -destroy          # destroy services
>sense_workflow.py sessions -show
```
