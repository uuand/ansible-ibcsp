#!/usr/bin/python

# Copyright: (c) 2020, Jens-Peter Wand <jenswand@googlemail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ibcsp_ip_space

short_description: This module interacts with the Infoblox BloxOne REST api

version_added: "2.x"

description:
    - "Test Infoblox BloxOne IP Space handling through Ansible"
options:
    name:
        description:
            - Name of the IP Space Object
        required: true
    comment:
        description:
            - A comment of the IP Space object
        required: false
    dhcp_config:
        description:
            - A shared DHCP configuration that controls how leases are issued.
        required: false
    dhcp_options:
        description:
            - A list of DHCP options. May be either a specific option or a group of options.
        required: false
    inheritance_sources:
        description:
            - Optional. Inheritance configuration.
        required: false
    tags:
        description:
            - Tagging specifics.
        required: false
    threshold:
        description:
            - The Utilization threshold (low and high) values of the utilization.
        required: false
    state:
        description:
            - Wheter the declared state should be present or absent
        default: present
        choices:
            - present
            - absent
    csp_host:
        description:
            - CSP Host
        default: csp.infoblox.com
    csp_apitoken:
        description:
            - CSP ApiToken retrieved from Logged-in User Properties/Settings
        required: true
    csp_apiversion:
        description:
            - CSP api version to use
        default: 1

author:
    - Jens-Peter Wand (@yourhandle)
'''

EXAMPLES = '''
# Pass in a message
tbd
'''

RETURN = '''
tbd
'''

from ansible.module_utils.basic import AnsibleModule
import ibcsp_ipamsvc
from ibcsp_ipamsvc.rest import ApiException
from ibcsp_ipamsvc.models.ipamsvc_ip_space import IpamsvcIPSpace
import os, json

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=True),
        comment=dict(type='str', required=False),
        dhcp_config=dict(type='str', required=False),
        dhcp_options=dict(type='str', required=False),
        inheritance_sources=dict(type='str', required=False),
        tags=dict(type='dict', required=False),
        threshold=dict(type='str', required=False),
        state=dict(type='str', default='present', choices=['present','absent']),
        csp_host=dict(type='str', default='csp.infoblox.com'),
        csp_apitoken=dict(type='str', required=True, no_log=True),
        csp_apiversion=dict(type='str', default="1")
    )

    # seed the result dict in the object
    result = dict(
        changed=False,
        result='',
        msg=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    cspclient = csp_client(module.params)
    fetch = csp_get(module, cspclient, getfilter(module.params))
    #api_response.results is a empty List if none was found
    if len(fetch.results) > 0:
        if module.params['state'] == 'present':
            #fetch.results[0] = IpamsvcIPSpace object and module2IpamsvcIPSpace = IpamsvcIPSpace
            if isdifferent(module, fetch.results[0], module2IpamsvcIPSpace(module.params)):
                body = module2IpamsvcIPSpace(module.params)
                fetch = csp_put(module, cspclient, fetch.results[0].id, body)
                result['changed'] = True
                result['result'] = fetch.result.to_dict()
            else:
                result['result'] = fetch.results[0].to_dict()
        else:
            #delete
            fetch = csp_delete(module, cspclient, fetch.results[0].id)
            result['changed'] = True
            result['result'] = ''
            result['msg'] = fetch['msg']
    else:
        if module.params['state'] == 'present':
            #try to create the resource
            body = module2IpamsvcIPSpace(module.params)
            fetch = csp_post(module, cspclient, body)
            result['changed'] = True
            result['result'] = fetch.result.to_dict()
        else:
            result['msg'] = {'msg':'IpSpaceApi ip_space Object is absent'}

    module.exit_json(**result)
    
  
def csp_client(module_args):
    cspurl = 'https://{0}/api/ddi/v{1}/'.format(module_args['csp_host'], module_args['csp_apiversion'])
    configuration = ibcsp_ipamsvc.Configuration(cspurl)
    configuration.api_key['Authorization'] = module_args['csp_apitoken']
    configuration.api_key_prefix['Authorization'] = 'Token'
    api_instance = ibcsp_ipamsvc.IpSpaceApi(ibcsp_ipamsvc.ApiClient(configuration))
    return api_instance

def csp_delete(module, api_instance, objectid):
    try:
        # Deletion returns an empty response so we return a msg
        # fetch.results[0].id contains part of the path ipam/ip_space/6b11d4ea-cc20-11ea-b5c8-3670d2b79356
        # remove everything that is not the UUID
        api_response = api_instance.ip_space_delete('ipam','ip_space', objectid.rsplit('/')[2])
        api_response = {'msg':'IpSpaceApi ip_space Object deleted'}
        return api_response
    except ApiException as e:
        debug = {'msg':{'Message':'Exception when calling IpSpaceApi->ip_space_delete with id {0}'.format(objectid.rsplit('/')[2]), 'Error':'{0}'.format(e)}}
        module.fail_json(**debug)

def csp_get(module, api_instance, filterstr):
    try:
        # Read One Address object by name attribute
        api_response = api_instance.ip_space_list(filter=filterstr)
        return api_response
    except ApiException as e:
        debug = {'msg':{'Message':'Exception when calling IpSpaceApi->ip_space_list with filter {0}'.format(filterstr),'Error':'{0}'.format(e)}}
        module.fail_json(**debug)

def csp_put(module, api_instance, objectid, body):
    try:
        # Read One Address object by name attribute
        api_response = api_instance.ip_space_update('ipam','ip_space', objectid.rsplit('/')[2], body)
        return api_response
    except ApiException as e:
        debug = {'msg':{'Message':'Exception when calling IpSpaceApi->ip_space_update with id {0}'.format(objectid.rsplit('/')[2]), 'Error':'{0}'.format(e)}}
        module.fail_json(**debug)

def csp_post(module, api_instance, body):
    try:
        # Read One Address object by name attribute
        api_response = api_instance.ip_space_create('ipam','ip_space',body)
        return api_response
    except ApiException as e:
        debug = {'msg':{'Message':'Exception when calling IpSpaceApi->ip_space_create', 'Error':'{0}'.format(e)}}
        module.fail_json(**debug)

def getfilter(module_args):
    # prepare GET Parameters for name
    filterstr = '{0}=="{1}"'.format('name', module_args['name'])
    return filterstr

def module2IpamsvcIPSpace(module_args):
    dhcp_options = None
    if module_args['dhcp_options']:
        #transform
        dhcp_options = module_args['dhcp_options']
    dhcp_config = None
    if module_args['dhcp_config']:
        #transform
        dhcp_config = module_args['dhcp_config']
    inheritance_sources = None
    if module_args['inheritance_sources']:
        #transform
        inheritance_sources = module_args['inheritance_sources']
    threshold = None
    if module_args['threshold']:
        #transform
        threshold = module_args['threshold']
    # assign module arguments as named parameters (defaults are set)
    ipspace = IpamsvcIPSpace( comment=module_args['comment'],
                                            name=module_args['name'],
                                            dhcp_config=dhcp_config,
                                            dhcp_options=dhcp_options,
                                            inheritance_sources=inheritance_sources,
                                            threshold=threshold,
                                            tags=module_args['tags'] )
    return ipspace

def isdifferent(module, have, want):
    # only look for differences in certain keys
    #debug = {'msg':{'want': str(want), 'have':str(have)}}
    #module.fail_json(**debug)
    # IpamsvcIPSpace has a __eq__ , but it compares each field - even fields we can't set
    # so define the Fields of interest and compare them with a to_dict() variant
    f = ['name','comment','tags']
    wantclean = {}
    haveclean = {}
    for k, v in want.to_dict().items():
        if k in f:
            wantclean[k] = v
    for k, v in have.to_dict().items():
        if k in f:
            haveclean[k] = v
    if haveclean == wantclean:
        return True
    else:
        return False

def main():
    run_module()

if __name__ == '__main__':
    main()