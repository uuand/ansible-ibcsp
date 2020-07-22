# Run the playbook

```bash
export CSP_TOKEN="<yourToken>"
```

```bash
ANSIBLE_CONFIG=ansible.cfg  ansible-playbook play-ibcsp_ip_space.yml --limit="ddi001.ru.bloxone.metro-cc.com"
```

```bash
PLAY [Test CSP IP Space via Ansible] ***********************************************************************************************************************************************************************************

TASK [get hostname from ENV] *******************************************************************************************************************************************************************************************
ok: [ddi001.ru.bloxone.metro-cc.com]

TASK [ensure IP_Space is present] **************************************************************************************************************************************************************************************
changed: [ddi001.ru.bloxone.metro-cc.com]

TASK [debug present IP_Space] ******************************************************************************************************************************************************************************************
ok: [ddi001.ru.bloxone.metro-cc.com] => {
    "result": {
        "changed": true,
        "failed": false,
        "msg": "",
        "result": {
            "asm_config": {
                "asm_threshold": 90,
                "enable": true,
                "enable_notification": true,
                "forecast_period": 14,
                "growth_factor": 20,
                "growth_type": "percent",
                "history": 30,
                "min_total": 10,
                "min_unused": 10,
                "reenable_date": "1970-01-01T00:00:00+00:00"
            },
            "asm_scope_flag": 0,
            "comment": "MCC RU IP Space created through Ansible",
            "dhcp_config": {
                "allow_unknown": true,
                "filters": [],
                "ignore_list": [],
                "lease_time": 3600
            },
            "dhcp_options": [],
            "id": "ipam/ip_space/de597d01-cc2b-11ea-adc9-ea058a5aeaa6",
            "inheritance_sources": null,
            "name": "MCCRU-Ansible",
            "tags": {
                "value": null
            },
            "threshold": {
                "enabled": false,
                "high": 0,
                "low": 0
            },
            "utilization": {
                "abandon_utilization": 0,
                "abandoned": "0",
                "dynamic": "0",
                "free": "0",
                "static": "0",
                "total": "0",
                "used": "0",
                "utilization": 0
            }
        }
    }
}

TASK [ensure IP_Space is still present] ********************************************************************************************************************************************************************************
ok: [ddi001.ru.bloxone.metro-cc.com]

TASK [debug still present IP_Space] ************************************************************************************************************************************************************************************
ok: [ddi001.ru.bloxone.metro-cc.com] => {
    "result": {
        "changed": false,
        "failed": false,
        "msg": "",
        "result": {
            "asm_config": {
                "asm_threshold": 90,
                "enable": true,
                "enable_notification": true,
                "forecast_period": 14,
                "growth_factor": 20,
                "growth_type": "percent",
                "history": 30,
                "min_total": 10,
                "min_unused": 10,
                "reenable_date": "1970-01-01T00:00:00+00:00"
            },
            "asm_scope_flag": 0,
            "comment": "MCC RU IP Space created through Ansible",
            "dhcp_config": {
                "allow_unknown": true,
                "filters": [],
                "ignore_list": [],
                "lease_time": 3600
            },
            "dhcp_options": [],
            "id": "ipam/ip_space/de597d01-cc2b-11ea-adc9-ea058a5aeaa6",
            "inheritance_sources": null,
            "name": "MCCRU-Ansible",
            "tags": {
                "value": null
            },
            "threshold": {
                "enabled": false,
                "high": 0,
                "low": 0
            },
            "utilization": {
                "abandon_utilization": 0,
                "abandoned": "0",
                "dynamic": "0",
                "free": "0",
                "static": "0",
                "total": "0",
                "used": "0",
                "utilization": 0
            }
        }
    }
}

TASK [ensure IP_Space is absent] ***************************************************************************************************************************************************************************************
changed: [ddi001.ru.bloxone.metro-cc.com]

TASK [debug absent IP_Space] *******************************************************************************************************************************************************************************************
ok: [ddi001.ru.bloxone.metro-cc.com] => {
    "result": {
        "changed": true,
        "failed": false,
        "msg": "IpSpaceApi ip_space Object deleted",
        "result": ""
    }
}

TASK [ensure IP_Space is still absent] *********************************************************************************************************************************************************************************
ok: [ddi001.ru.bloxone.metro-cc.com]

TASK [debug still absent IP_Space] *************************************************************************************************************************************************************************************
ok: [ddi001.ru.bloxone.metro-cc.com] => {
    "result": {
        "changed": false,
        "failed": false,
        "msg": {
            "msg": "IpSpaceApi ip_space Object is absent"
        },
        "result": ""
    }
}

PLAY RECAP *************************************************************************************************************************************************************************************************************
ddi001.ru.bloxone.metro-cc.com : ok=9    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```