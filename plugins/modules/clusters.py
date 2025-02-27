#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = r"""
---
module: clusters

short_description: Handle AssistedInstall clusters

version_added: "1.0.0"

description: Interact with clusters through the AssistedInstall API

options:
    action:
      description: The action to perform (list, create, delete)
      required: false
      default: "list"
      type: str
    cluster_id:
        description: The cluster ID to perform the action on
        required: false
        type: str
    with_hosts:
        description: Include hosts in the returned list
        default: false
        type: bool

author:
    - Name (@vjayaramrh)
    - Tony García (@tonyskapunk)
"""

EXAMPLES = r"""
# Use argument
- name: List clusters
  clusters:
    action: list

- name: Delete cluster
  clusters:
    action: delete
    cluster_id: "deadbeef-dead-beef-dead-beefdeadbeef"
"""

RETURN = r"""
clusters:
    description: A message with the status
    type: list
    returned: always
    sample: []
"""

import os
import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib

try:
    import requests
except ImportError:
    HAS_REQUESTS = False
    REQUESTS_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_REQUESTS = True
    REQUESTS_IMPORT_ERROR = None

API_VERSION = "v2"
API_URL = f"https://api.openshift.com/api/assisted-install/{API_VERSION}"

# add additional query parameters to the query_params_list
QUERY_PARAMS_LIST = ["with_hosts"]


def run_module():

    module_args = dict(
        action=dict(type="str", required=False, default="list"),
        cluster_id=dict(type="str", required=False),
        # any API query parameters may have to be added here
        with_hosts=dict(type="bool", required=False, default=False),
        data=dict(type="dict", required=False),
    )
    token = os.environ.get('AI_API_TOKEN')
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Fail if requests is not installed
    if not HAS_REQUESTS:
        module.fail_json(msg=missing_required_lib('requests'), exception=REQUESTS_IMPORT_ERROR)

    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    # List clusters
    if module.params.get('action') == "list":
        list_params = {}
        for k in QUERY_PARAMS_LIST:
            val = module.params.get(k)
            if val:
                list_params = list_params | {k: val}

        response = requests.get(f"{API_URL}/clusters", params=list_params, headers=headers)

        if not response.ok:
            result = dict(changed=True, response=response.text)
            module.fail_json(msg="Error listing clusters", **result)

        result = dict(clusters=response.json())

    # Delete cluster
    elif module.params.get('action') == "absent":
        if not module.params.get('cluster_id'):
            module.fail_json(msg="cluster_id is required for delete action")

        response = requests.delete(f"{API_URL}/clusters/{module.params.get('cluster_id')}", headers=headers)

        if response.status_code != 204:
            result = dict(response=response.text)
            module.fail_json(msg=f"Error deleting cluster_id: {module.params.get('cluster_id')}", **result)

        result = dict(changed=True, clusters=[])

    # Register cluster
    elif module.params.get('action') == "present":
        pull_secret = os.environ.get('AI_PULL_SECRET')

        data = module.params.get('data')
        data['pull_secret'] = pull_secret

        response = requests.post(f"{API_URL}/clusters", headers=headers, json=data)

        if not response.ok:
            result = dict(changed=True, response=response.text)
            module.fail_json(msg="Error registering cluster", **result)

        result = dict(clusters=response.json())

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
