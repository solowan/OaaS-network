# Copyright 2013 Dell Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class OaasDriverBase(object):
    """Optimizer as a Service Driver base class.

    Using OaasDriver Class, an instance of L3 perimeter Optimizer
    can be created. The optimizer co-exists with the L3 agent.

    One instance is created for each tenant. One optimizer policy
    is associated with each tenant (in the Havana release).

    The Optimizer can be visualized as having two zones (in Havana
    release), trusted and untrusted.

    All the 'internal' interfaces of Neutron Router is treated as trusted. The
    interface connected to 'external network' is treated as untrusted.

    The policy is applied on traffic ingressing/egressing interfaces on
    the trusted zone. This implies that policy will be applied for traffic
    passing from
        - trusted to untrusted zones
        - untrusted to trusted zones
        - trusted to trusted zones

    Policy WILL NOT be applied for traffic from untrusted to untrusted zones.
    This is not a problem in Havana release as there is only one interface
    connected to external network.

    Since the policy is applied on the internal interfaces, the traffic
    will be not be NATed to floating IP. For incoming traffic, the
    traffic will get NATed to internal IP address before it hits
    the optimizer rules. So, while writing the rules, care should be
    taken if using rules based on floating IP.

    The optimizer rule addition/deletion/insertion/update are done by the
    management console. When the policy is sent to the driver, the complete
    policy is sent and the whole policy has to be applied atomically. The
    optimizer rules will not get updated individually. This is to avoid problems
    related to out-of-order notifications or inconsistent behaviour by partial
    application of rules. Argument agent_mode indicates the l3 agent in DVR or
    DVR_SNAT or LEGACY mode.
    """

    @abc.abstractmethod
    def create_optimizer(self, agent_mode, apply_list, optimizer):
        """Create the Optimizer with default (drop all) policy.

        The default policy will be applied on all the interfaces of
        trusted zone.
        """
        pass

    @abc.abstractmethod
    def delete_optimizer(self, agent_mode, apply_list, optimizer):
        """Delete optimizer.

        Removes all policies created by this instance and frees up
        all the resources.
        """
        pass

    @abc.abstractmethod
    def update_optimizer(self, agent_mode, apply_list, optimizer):
        """Apply the policy on all trusted interfaces.

        Remove previous policy and apply the new policy on all trusted
        interfaces.
        """
        pass

    @abc.abstractmethod
    def apply_default_policy(self, agent_mode, apply_list, optimizer):
        """Apply the default policy on all trusted interfaces.

        Remove current policy and apply the default policy on all trusted
        interfaces.
        """
        pass
