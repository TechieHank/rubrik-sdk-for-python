# Copyright 2018 Rubrik, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License prop
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the Rubrik SDK Cluster class.
"""

import sys
from .api import Api

_API = Api


class Cluster(_API):
    """This class contains methods related to the managment of the Rubrik Cluster itself.
    """

    def cluster_version(self, timeout=15):
        """Retrieves the software version of the Rubrik Cluster.

        Keyword Arguments:
            timeout {int} -- The response timeout value, in seconds, of the API call. (default: {15})

        Returns:
            dict -- Software version running on the Rubrik Cluster
        """
        self.log('cluster_version: Getting the software version of the Rubrik Cluster.')
        api_request = self.get('v1', '/cluster/me/version', timeout)
        return api_request

    def cluster_node_ip(self, timeout=15):
        """Retrive the IP Address for each node in the Rubrik Cluster.

        Keyword Arguments:
            timeout {int} -- The response timeout value, in seconds, of the API call. (default: {15})

        Returns:
            list -- A list that contains the IP Address for each node in the Rubrik Cluster.
        """

        self.log('cluster_node_ip: Generating a list of all Cluster Node IPs.')
        api_request = self.get('internal', '/cluster/me/node', timeout)

        node_ip_list = []

        for node in api_request['data']:
            node_ip_list.append(node["ipAddress"])

        return node_ip_list

    def bootstrap(self, cluster_name, admin_email, admin_password, management_gateway, management_subnet_mask, enable_encryption=True, node_config=None, dns_search_domains=None, dns_nameservers=None, ntp_servers=None, timeout=15):
        """Issues a bootstrap request to a specified Rubrik cluster

        Arguments:
            cluster_name {str} -- Unique name to assign to the Rubrik cluster.
            admin_email {str} -- The Rubrik cluster sends messages for the admin account to this email address.
            admin_password {str} --  Password for the admin account.
            management_gateway {str} --  IP address assigned to the management network gateway
            management_subnet_mask {str} -- Subnet mask assigned to the management network.

        Keyword Arguments:
            enable_encryption {bool} -- Enable software data encryption at rest. (default: {True})
            node_config {dict} -- [description] (default: {None})
            dns_search_domains {str} -- The search domain that the DNS Service will use to resolve hostnames that are not fully qualified. (default: {None})
            dns_nameservers {list} -- IPv4 addresses of DNS servers. (default: {None})
            ntp_servers {list} -- FQDN or IPv4 address of a network time protocol (NTP) server. (default: {None})
            timeout {int} -- The response timeout value, in seconds, of the API call. (default: {15})

        Returns:
            dict -- The response returned by the API call.
        """

        if node_config is None or isinstance(node_config, dict) is not True:
            sys.exit('Error: You must provide a valid dictionary for "node_config".')

        if dns_search_domains is None:
            dns_search_domains = []
        elif isinstance(dns_search_domains, list) is not True:
            sys.exit('Error: You must provide a valid list for "dns_search_domains".')

        if dns_nameservers is None:
            dns_nameservers = ['8.8.8.8']
        elif isinstance(dns_nameservers, list) is not True:
            sys.exit('Error: You must provide a valid list for "dns_nameservers".')

        if ntp_servers is None:
            ntp_servers = ['pool.ntp.org']
        elif isinstance(ntp_servers, list) is not True:
            sys.exit('Error: You must provide a valid list for "ntp_servers".')

        bootstrap_config = {}
        bootstrap_config["enableSoftwareEncryptionAtRest"] = enable_encryption
        bootstrap_config["name"] = cluster_name
        bootstrap_config["dnsNameservers"] = dns_nameservers
        bootstrap_config["dnsSearchDomains"] = dns_search_domains
        bootstrap_config["ntpServers"] = ntp_servers

        bootstrap_config["adminUserInfo"] = {}
        bootstrap_config["adminUserInfo"]['password'] = admin_password
        bootstrap_config["adminUserInfo"]['emailAddress'] = admin_email
        bootstrap_config["adminUserInfo"]['id'] = "admin"

        bootstrap_config["nodeConfigs"] = {}
        for node_name, node_ip in node_config.items():
            bootstrap_config["nodeConfigs"][node_name] = {}
            bootstrap_config["nodeConfigs"][node_name]['managementIpConfig'] = {}
            bootstrap_config["nodeConfigs"][node_name]['managementIpConfig']['netmask'] = management_subnet_mask
            bootstrap_config["nodeConfigs"][node_name]['managementIpConfig']['gateway'] = management_gateway
            bootstrap_config["nodeConfigs"][node_name]['managementIpConfig']['address'] = node_ip

        self.log('bootstrap: Starting the bootstrap process.')
        api_request = self.post('internal', '/cluster/me/bootstrap', bootstrap_config, timeout, authentication=False)

        return api_request

    def bootstrap_status(self, request_id="1", timeout=15):
        """Retrieves status of in progress bootstrap requests

        Arguments:


        Keyword Arguments:
            request_id {str} -- Id of the bootstrap request (default: {"1"})
            timeout {int} -- The response timeout value, in seconds, of the API call. (default: {15})

        Returns:
            dict -- The response returned by the API call.
        """

        bootstrap_status_api_endpoint = '/cluster/me/bootstrap?request_id={}'.format(request_id)

        self.log('bootstrap_status: Getting the status of the Rubrik Cluster bootstrap.')
        api_request = self.get('internal', bootstrap_status_api_endpoint, timeout=timeout, authentication=False)

        return api_request

    def end_user_authorization(self, object_name, end_user, object_type='vmware', timeout=15):

        valid_object_type = ['vmware']

        if object_type not in valid_object_type:
            sys.exit("Error: The end_user_authorization() object_type argument must be one of the following: {}.".format(
                valid_object_type))

        self.log("end_user_authorization: Searching the Rubrik Cluster for the vSphere VM '{}'.".format(object_name))
        vm_id = self.object_id(object_name, object_type)

        self.log("end_user_authorization: Searching the Rubrik Cluster for the End User '{}'.".format(end_user))
        user_id = self.get('internal', '/user?username={}'.format(end_user))
        print(user_id)
