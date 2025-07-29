
# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san SDK Software in commercial settings.
#
# END COPYRIGHT
"""
See class comment for details
"""
from typing import List


class AgentsUpdater:
    """
    Abstract interface for updating current collection of agents
    being served.
    """

    def update_agents(self, agents: List[str]):
        """
        :param agents: list of agents names which should be served currently.
        :return: nothing
        """
        raise NotImplementedError
