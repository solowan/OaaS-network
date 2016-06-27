# Copyright 2015 Brocade Communications System, Inc.
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
#

from neutron.callbacks import events
from neutron.callbacks import registry
from neutron.callbacks import resources
from neutron import context
from oslo_log import log as logging

from neutron_oaas.services.optimizer.agents.vyatta import vyatta_utils


LOG = logging.getLogger(__name__)


class VyattaOptimizerService(object):
    # TODO(vishwanathj): Code to be revised in Liberty release to use
    # the base class optimizer_service.OptimizerService for registrations
    def __init__(self, l3_agent):
        self.conf = l3_agent.conf
        registry.subscribe(
            sync_optimizer_zones, resources.ROUTER, events.AFTER_CREATE)
        registry.subscribe(
            sync_optimizer_zones, resources.ROUTER, events.AFTER_DELETE)
        registry.subscribe(
            sync_optimizer_zones, resources.ROUTER, events.AFTER_UPDATE)


def sync_optimizer_zones(resource, event, l3_agent, **kwargs):
    LOG.debug('VyattaOptimizerService:: sync_optimizer_zones() called')

    ri = kwargs['router']

    ctx = context.Context(None, ri.router['tenant_id'])
    client = l3_agent._vyatta_clients_pool.get_by_db_lookup(
        ri.router['id'], ctx)
    opt_list = l3_agent.optplugin_rpc.get_optimizers_for_tenant(ctx)
    if opt_list:
        zone_cmds = []
        for opt in opt_list:
            if ri.router['id'] in opt['router_ids']:
                opt_name = vyatta_utils.get_optimizer_name(ri, opt)
                zone_cmds.extend(vyatta_utils.get_zone_cmds(client, ri,
                                                            opt_name))
        client.exec_cmd_batch(zone_cmds)
