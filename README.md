# Run the playbook

```bash
export CSP_TOKEN="<yourToken>"
```

```bash
ANSIBLE_CONFIG=ansible.cfg  ansible-playbook play-ibcsp_ip_space.yml --limit="ddi001.ru.bloxone.metro-cc.com"
```