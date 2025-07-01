# Vlan Overlap Checker
This script checks for VLAN range overlaps between ports in a network model using data from a SPARQL query accessed via the WorkflowCombinedApi. It outputs overlapping VLANs between ports, taking into account aliases, and writes the results to a CSV file.

The script outputs results in the following format (CSV with | as a separator):
```
PORT1|PORT2|Common|Only PORT1|Only PORT2|Common Vlans|Only In PORT1 List|Only In PORT2 List|PORT1 Range|PORT2 Range
```
Each line represents a comparison between a port and its alias.

Example:
```
urn:ogf:network:siteA:port1|urn:ogf:network:siteA:port1-alias|3|2|1|[10, 11, 12]|[13, 14]|[9]|[10, 11, 12, 13, 14]|[9, 10, 11, 12]
```

Ports without a resolved isAlias will be skipped with a warning.
