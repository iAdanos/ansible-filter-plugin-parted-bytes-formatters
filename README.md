# Ansible formatters filter plugins for parted

Adds two filter plugins:

- `parted_human_readable`
- `parted_human_to_bytes`

## History

These plugins are used to convert partition size in bytes to parted-compatable format.

Parted (as its [Ansible module](https://docs.ansible.com/ansible/2.8/modules/parted_module.html) wrapper) supports both Kilobytes ([SI prefix](https://en.wikipedia.org/wiki/Metric_prefix#List_of_SI_prefixes)) and [Kibibytes](https://en.wikipedia.org/wiki/Kibibyte).  
Ansible considers GB a Gibibyte while Parted interprets is as a Gigabyte.  
Also Parted is case-sensitive and doesn't support space separator for taken values.

Code is based on [official Ansible filters for size convertions](https://docs.ansible.com/ansible/latest/user_guide/playbooks_filters.html#computer-theory-assertions).

## Installation

[Common for custom Ansible filter plugins](https://docs.ansible.com/ansible/latest/dev_guide/developing_locally.html#adding-a-plugin-locally).

## Use

### Parted Human Readable

Asserts whether the given string is human readable or not.

For example:

```yaml
- name: "Parted Human Readable"
  assert:
    that:
      - '"1.00 Bytes" == 1|parted_human_readable'
      - '"1.00 bits" == 1|parted_human_readable(isbits=True)'
      - '"10.00 KB" == 10000|parted_human_readable'
      - '"97.66 MB" == 97660000|parted_human_readable'
      - '"0.10 GB" == 100000000|parted_human_readable(unit="G")'
      - '"0.10 Gb" == 100000000|parted_human_readable(isbits=True, unit="G")'
      - '"10.00 KiB" == 10240|parted_human_readable(iskibi=True)'
      - '"97.66 MiB" == 102400000|parted_human_readable(iskibi=True)'
      - '"0.10 GiB" == 107374182|parted_human_readable(iskibi=True, unit="Gi")'
      - '"0.10 Gib" == 107374182|parted_human_readable(iskibi=True, isbits=True, unit="Gi")'
      - '"0.10GiB" == 107374182|parted_human_readable(iskibi=True, unit="Gi", spaceseparator=False)'
```

This would result in:

```json
{ "changed": false, "msg": "All assertions passed" }
```

### Parted Human to Bytes

Returns the given string in the Bytes format.

For example:

```yaml
- name: "Parted Human to Bytes"
  assert:
    that:
      - "{{'0'|parted_human_to_bytes}}        == 0"
      - "{{'0.1'|parted_human_to_bytes}}      == 0"
      - "{{'0.9'|parted_human_to_bytes}}      == 1"
      - "{{'1'|parted_human_to_bytes}}        == 1"
      - "{{'10.00 KB'|parted_human_to_bytes}} == 10000"
      - "{{   '11 MB'|parted_human_to_bytes}} == 11000000"
      - "{{  '1.1 GB'|parted_human_to_bytes}} == 1100000000"
      - "{{'10.00 Kib'|parted_human_to_bytes(iskibi=True, isbits=True)}} == 10240"
      - "{{'10.00 KiB'|parted_human_to_bytes(iskibi=True)}} == 10240"
      - "{{   '11 MiB'|parted_human_to_bytes(iskibi=True)}} == 11534336"
      - "{{  '1.1 GiB'|parted_human_to_bytes(iskibi=True)}} == 1181116006"
```

This would result in:

```json
{ "changed": false, "msg": "All assertions passed" }
```
