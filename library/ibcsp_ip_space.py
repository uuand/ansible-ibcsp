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
        type: string
    comment:
        description:
            - A comment of the IP Space object
        required: false
        type: string
    dhcp_config:
        description:
            - A shared DHCP configuration that controls how leases are issued.
        required: false
        type: dict
        suboptions:
            allow_unknown:
                description:
                    - Disable to allow leases only for known clients, those for which a Fixed Address is configured.
                type: bool
            filters:
                description:
                    - List of Filter resource identifier.
                type: list
                suboptions:
                    str:
                        description:
                            - Resource Identifier of a Filter
                        type: string
            ignore_list:
                description:
                    - List of clients to ignore requests from.
                type: List
                suboptions:
                    type:
                        description:
                            - Type of ignore matching: client to ignore by client identifier (client hex or client text) or hardware to ignore by hardware identifier (MAC address). It can have one of the following values: [client_hex, client_text, hardware].
                        type: string
                    value:
                        description:
                            - Value to match.
                        type: string
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
        dhcp_config=dict(type='dict',
                        options=dict(
                            allow_unknown=dict(
                                type='bool',
                                required=False
                            ),
                            filters=dict(
                                type='list',
                                elements='str'
                            ),
                            ignore_list=dict(
                                type='list',
                                elements='dict',
                                options=dict(
                                    type=dict(type='str', choices=['client_hex','client_text','hardware']),
                                    value=dict(type='str')
                                )
                            ),
                            lease_time=dict(type='int')
                        )
        ),
        dhcp_options=dict(type='list',
                        elements='dict',
                        options=dict(
                            group=dict(type='str'),
                            option_code=dict(type='str'),
                            option_value=dict(type='str'),
                            type=dict(type='str')
                        )
        ),
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
    cspconf = csp_configuration(module.params)
    cspclient = csp_ipspaceclient(cspconf)
    fetch = csp_get(module, cspclient, getfilter(module.params))
    #api_response.results is a empty List if none was found
    if len(fetch.results) > 0:
        if module.params['state'] == 'present':
            #fetch.results[0] = IpamsvcIPSpace object and module2IpamsvcIPSpace = IpamsvcIPSpace
            if isdifferent(module, fetch.results[0], module2IpamsvcIPSpace(module, fetch)):
                #debug = {'msg':{'isdifferent':'yeah'}}
                #module.fail_json(**debug)
                body = module2IpamsvcIPSpace(module, fetch)
                fetch = csp_put(module, cspclient, fetch, body)
                result['changed'] = True
                result['result'] = fetch.results[0].to_dict()
            else:
                result['result'] = fetch.results[0].to_dict()

        else:
            #delete
            fetch = csp_delete(module, cspclient, fetch)
            result['changed'] = True
            result['result'] = ''
            result['msg'] = fetch['msg']
    else:
        if module.params['state'] == 'present':
            #try to create the resource
            body = module2IpamsvcIPSpace(module)
            fetch = csp_post(module, cspclient, body)
            result['changed'] = True
            result['result'] = fetch.results[0].to_dict()
        else:
            result['msg'] = {'msg':'IpSpaceApi ip_space Object is absent'}

    module.exit_json(**result)
    
  
def csp_configuration(module_args):
    cspurl = 'https://{0}/api/ddi/v{1}/'.format(module_args['csp_host'], module_args['csp_apiversion'])
    configuration = ibcsp_ipamsvc.Configuration(cspurl)
    configuration.api_key['Authorization'] = module_args['csp_apitoken']
    configuration.api_key_prefix['Authorization'] = 'Token'
    return configuration

def csp_ipspaceclient(configuration):
    api_instance = ibcsp_ipamsvc.IpSpaceApi(ibcsp_ipamsvc.ApiClient(configuration))
    return api_instance

def csp_delete(module, api_instance, have):
    objectid = have.results[0].id.rsplit('/')[2]
    try:
        # Deletion returns an empty response so we return a msg
        # fetch.results[0].id contains part of the path ipam/ip_space/6b11d4ea-cc20-11ea-b5c8-3670d2b79356
        # remove everything that is not the UUID
        api_response = api_instance.ip_space_delete('ipam','ip_space', objectid)
        api_response = {'msg':'IpSpaceApi ip_space Object deleted'}
        return api_response
    except ApiException as e:
        debug = {'msg':{'Message':'csp_delete - Exception when calling IpSpaceApi->ip_space_delete with id {0}'.format(objectid), 'Error':'{0}'.format(e)}}
        module.fail_json(**debug)

def csp_get(module, api_instance, filterstr):
    try:
        # Read One Address object by name attribute
        api_response = api_instance.ip_space_list(filter=filterstr, inherit='full')
        return api_response
    except ApiException as e:
        debug = {'msg':{'Message':'csp_get - Exception when calling IpSpaceApi->ip_space_list with filter {0}'.format(filterstr),'Error':'{0}'.format(e)}}
        module.fail_json(**debug)

def csp_put(module, api_instance, objectid, body):
    # update does not return the full object ?_inherit=full so we need to read once more
    objectid = objectid.results[0].id.rsplit('/')[2]
    filterstr = getfilter(module.params)
    try:
        api_response = api_instance.ip_space_update('ipam','ip_space', objectid, body)
    except ApiException as e:
        debug = {'msg':{'Message':'csp_put - Exception when calling IpSpaceApi->ip_space_update with id {0}'.format(objectid), 'Error':'{0}'.format(e)}}
        module.fail_json(**debug)

    try:
        # Read One Address object by name attribute
        api_response = api_instance.ip_space_list(filter=filterstr, inherit='full')
        return api_response
    except ApiException as e:
        debug = {'msg':{'Message':'csp_put - Exception when calling IpSpaceApi->ip_space_read with filter _inherit=full','Error':'{0}'.format(e)}}
        module.fail_json(**debug)


def csp_post(module, api_instance, body):
    # create does not return the full object ?_inherit=full so we need to read once more
    # create with inheritance_sources does not take the value, only the override action
    # so a update is required as well
    try:
        # Create the Object first
        api_response = api_instance.ip_space_create('ipam','ip_space',body)
    except ApiException as e:
        debug = {'msg':{'Message':'csp_post - Exception when calling IpSpaceApi->ip_space_create', 'Error':'{0}'.format(e)}}
        module.fail_json(**debug)
    
    try:
        # Read the Object with _inherit=full
        api_response = api_instance.ip_space_list(filter=getfilter(module.params),inherit='full')
    except ApiException as e:
        debug = {'msg':{'Message':'csp_post - Exception when calling IpSpaceApi->ip_space_list with filter {0}'.format(filterstr),'Error':'{0}'.format(e)}}
        module.fail_json(**debug)

    if len(api_response.results) > 0:
        objectid = api_response.results[0].id.rsplit('/')[2]
        body = module2IpamsvcIPSpace(module, api_response)
        try:
            # Update the Object
            api_response = api_instance.ip_space_update('','', objectid ,body)

        except ApiException as e:
            debug = {'msg':{'Message':'csp_post - Exception when calling IpSpaceApi->ip_space_update update of inheritance settings failed','Error':'{0}'.format(e)}}
            module.fail_json(**debug)

        try:
            # Read the Object with _inherit=full
            api_response = api_instance.ip_space_list(filter=getfilter(module.params),inherit='full')
            return api_response
        except ApiException as e:
            debug = {'msg':{'Message':'csp_post - Exception when calling IpSpaceApi->ip_space_list with filter {0}'.format(filterstr),'Error':'{0}'.format(e)}}
            module.fail_json(**debug)

    else:
        debug = {'msg':{'Message':'csp_post - Exception when calling IpSpaceApi->ip_space_create update of inheritance settings failed','Error':'{0}'.format(e)}}
        module.fail_json(**debug)


def getfilter(module_args):
    # prepare GET Parameters for name and request the inheritance_sources key
    filterstr = '{0}=="{1}"'.format('name', module_args['name'])
    return filterstr

def module2IpamsvcIPSpace(module, have=None):
    module_args = module.params
    dhcp_options = None
    dhcp_config = None
    threshold = None
    inheritance_sources = {}

    if have != None:
        inheritance_sources = have.results[0].inheritance_sources.to_dict()

    if 'dhcp_options' in module_args:
        #transform
        dhcp_options = module_args['dhcp_options']
    
    if 'dhcp_config' in module_args:
        #transform
        dhcp_config = module_args['dhcp_config']
        for k,v in module_args['dhcp_config'].items():
            # prevent uninitialized module paramenters
            if 'dhcp_config' in inheritance_sources and v != None:
                inheritance_sources['dhcp_config'][k]['action'] = 'override'
                if k != 'lease_time':
                    inheritance_sources['dhcp_config'][k]['value'] = v
            elif have != None:
                inheritance_sources['dhcp_config'][k]['action'] = 'inherit'

    # assign module arguments as named parameters (defaults are set)
    ipspace = IpamsvcIPSpace( comment=module_args['comment'],
                                            name=module_args['name'],
                                            dhcp_config=dhcp_config,
                                            dhcp_options=dhcp_options,
                                            inheritance_sources=inheritance_sources,
                                            threshold=threshold,
                                            tags=module_args['tags'] )
    #debug = {'msg':{'ipspace':ipspace.to_dict()}}
    #module.fail_json(**debug)
    return ipspace

def isdifferent(module, have, want):
    # only look for differences in certain keys
    # IpamsvcIPSpace has a __eq__ , but it compares each field - even fields we can't set
    # so define the Fields of interest and compare them with a to_dict() variant
    # just some, which are toplevel
    f = ['name','comment','tags','inheritance_sources']
    wantclean = {}
    haveclean = {}
    for k, v in want.to_dict().items():
        if k in f:
            wantclean[k] = v
    for k, v in have.to_dict().items():
        if k in f:
            haveclean[k] = v
    #debug = {'msg':{'want': str(wantclean), 'have':str(haveclean)}}
    #module.fail_json(**debug)
    if haveclean == wantclean:
        return False
    else:
        return True

def main():
    run_module()

if __name__ == '__main__':
    main()