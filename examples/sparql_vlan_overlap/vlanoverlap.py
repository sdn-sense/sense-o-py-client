#!/usr/bin/env python3
# pylint: disable=line-too-long
# -*- coding: utf-8 -*-
"""
This script is used to check for VLAN overlaps between ports in a network model.
It retrieves data from a workflow API with SparQL query, processes the data to find VLAN overlaps,
and outputs the results in a CSV format (separated by |) and console.
"""
import json
import time
from sense.client.workflow_combined_api import WorkflowCombinedApi


def getData():
    """Get data from WorkflowCombinedApi."""
    wapi = WorkflowCombinedApi()
    template = {"Ports": [{
        "isAlias": '?isAlias?',
        "source_port": "?source_port?",
        "vlan_range": "?vlan_values?",
        "sparql": """SELECT DISTINCT ?source_port ?isAlias ?vlan_range ?vlan_values
                    WHERE {
                    ?source_port ?anyProp1 ?vlan_range .
                    FILTER regex(str(?anyProp1), "hasLabelGroup$")

                    ?vlan_range ?anyProp2 ?vlan_values .
                    FILTER regex(str(?anyProp2), "values$")

                    OPTIONAL {
                        ?source_port ?isAliasProp ?isAlias .
                        FILTER regex(str(?isAliasProp), "isAlias$")
                    }
                    }"""
    }]}
    out = wapi.manifest_create(json.dumps(template))
    data = json.loads(out['jsonTemplate'])['Ports']

    # Build a lookup from source_port to isAlias
    aliassourcemap = {entry['isAlias']: entry['source_port'] for entry in data if entry.get('isAlias') and entry['isAlias'] != "?isAlias?"}

    new_data = []
    for entry in data:
        # If isAlias is missing or a placeholder, try to update it
        if not entry.get('isAlias') or entry['isAlias'] == "?isAlias?":
            # Try to find another entry whose source_port matches this one's isAlias
            updated_alias = aliassourcemap.get(entry['source_port'])
            if updated_alias:
                print(f"Found alias for {entry['source_port']}: {updated_alias}")
                new_entry = dict(entry)
                new_entry['isAlias'] = updated_alias
                new_data.append(new_entry)
            else:
                new_data.append(entry)
        else:
            new_data.append(entry)
    return new_data


def checkportisAlias(data):
    """Check if port is an alias and update the output dictionary."""
    # Create a dictionary to hold the output
    # This will map source_port to its corresponding entry
    # If isAlias is not a placeholder, it will be used directly
    # If it is a placeholder, we will find the actual alias later
    output = {}
    for entry in data:
        if entry['isAlias'] != "?isAlias?":
            output[entry['source_port']] = entry
        else:
            # Loop again via all data and find a match
            found = False
            for sub_entry in data:
                if sub_entry['isAlias'] == entry['source_port']:
                    output[entry['source_port']] = sub_entry
                    output[entry['source_port']]['isAlias'] = sub_entry['source_port']
                    found = True
                    break
            if not found:
                # If no match found, keep the original entry
                print(f"Warning: No alias found for {entry['source_port']}, Will not check it for vlan overlap.")
    return output

def compareRanges(list1, list2):
    """Compare two lists and return common elements, elements only in the first list, and elements only in the second list."""
    set1 = set(list1)
    set2 = set(list2)

    common = set1 & set2
    onlyFirst = set1 - set2
    onlySecond = set2 - set1
    return list(common), list(onlyFirst), list(onlySecond)


def getVlanRange(vlan_range):
    """Convert vlan_range string to a list of integers."""
    vlanout = []
    if vlan_range and vlan_range != "?vlan_values?":
        for item in vlan_range.split(','):
            try:
                # If the item is a single number, convert it to int
                if item.isdigit():
                    vlanout.append(int(item))
                # If the item is a range like "10-20", split and create a range
                elif '-' in item:
                    start, end = map(int, item.split('-'))
                    vlanout.extend(range(start, end + 1))
                else:
                    # If the item is not a number or range, print a warning
                    print(f"Invalid vlan_range item: {item}")
            except ValueError:
                print(f"Invalid vlan_range format: {vlan_range}")
    return vlanout

def checkvlanWriteOutput(output):
    """Check VLAN overlaps and write output to a CSV file."""
    # Now that we have the output and both ends, we loop through all of them
    scanned = []
    # Write to csv file
    fname = f'vlan_overlap_output-{int(time.time())}.csv'
    with open(fname, 'w', encoding="utf-8") as fd:
        fd.write("PORT1|PORT2|Common|Only PORT1|Only PORT2|Common Vlans|Only In PORT1 List|Only In PORT2 List|PORT1 Range|PORT2 Range\n")
        print("PORT1|PORT2|Common|Only PORT1|Only PORT2|Common Vlans|Only In PORT1 List|Only In PORT2 List|PORT1 Range|PORT2 Range")
        for source_port, entry in output.items():
            if source_port in scanned:
                continue  # Skip if already scanned
            scanned.append(source_port)
            # Find isAlias in output
            entryisAlias = output.get(entry['isAlias'])
            if entryisAlias:
                scanned.append(entryisAlias['source_port'])
                # Check if vlan_range overlaps
                entry_vlan_range = entry.get('vlan_range', '')
                alias_vlan_range = entryisAlias.get('vlan_range', '')

                if entry_vlan_range and alias_vlan_range:
                    # Assuming vlan_range is a string like "10-20"
                    # Split the ranges and convert to integers
                    range1 = getVlanRange(entry_vlan_range)
                    range2 = getVlanRange(alias_vlan_range)
                    common, onlyFirst, onlySecond = compareRanges(range1, range2)
                    # Print the results | separated
                    out = [source_port, entry["isAlias"], len(common), len(onlyFirst), len(onlySecond), common, onlyFirst, onlySecond, range1, range2]
                    print("|".join(map(str, out)))
                    fd.write("|".join(map(str, out)) + "\n")
                else:
                    print(f"No vlan range to check for overlap for {source_port} and {entryisAlias['source_port']}")
                    fd.write(f"{source_port}|{entry['isAlias']}|0|0|0|-1|-1|-1|{entry_vlan_range}|{alias_vlan_range}No vlan range to check for overlap\n")
    print("="*40)
    print(f"Output written to {fname}. CSV file separated by |")

def main():
    """Main function to run the script."""
    data = getData()
    if not data:
        print("No data retrieved from WorkflowCombinedApi.")
        return
    output = checkportisAlias(data)
    if not output:
        print("No valid output found after checking isAlias.")
        return
    checkvlanWriteOutput(output)

if __name__ == "__main__":
    main()
