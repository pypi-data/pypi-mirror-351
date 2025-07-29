"""
Created on 2025-05-28

@author: wf
"""

from dataclasses import asdict
from pathlib import Path
from typing import Callable, Dict

from omnigraph.blazegraph import Blazegraph, BlazegraphConfig
from omnigraph.jena import Jena, JenaConfig
from omnigraph.qlever import QLever, QLeverConfig
from omnigraph.sparql_server import ServerCmd, ServerConfig, ServerConfigs, ServerEnv, SparqlServer


class OmniServer:
    """
    Factory class for creating and managing SPARQL server instances.
    """

    def __init__(self, env: ServerEnv):
        """
        constructor
        """
        self.env = env

    def get_server_commands(self) -> Dict[str, Callable[[SparqlServer], ServerCmd]]:
        """
        Get available server commands as factory functions.

        Returns:
            Dictionary mapping command names to ServerCmd factories
        """
        server_cmds = {
            "start": lambda s: ServerCmd(title=f"start {s.name}", func=s.start),
            "stop": lambda s: ServerCmd(title=f"stop {s.name}", func=s.stop),
            "status": lambda s: ServerCmd(title=f"status {s.name}", func=s.status),
            "clear": lambda s: ServerCmd(title=f"clear {s.name}", func=s.clear),
            "count": lambda s: ServerCmd(title=f"triple count {s.name}", func=s.count_triples),
            "load": lambda s: ServerCmd(title=f"load dumps {s.name}", func=s.load_dump_files),
            "webui": lambda s: ServerCmd(title=f"webui {s.name}", func=s.webui),
        }
        return server_cmds

    def server4Config(self, config: ServerConfig) -> SparqlServer:
        """
        Create a SparqlServer instance based on server type in config.

        Args:
            config: ServerConfig with server type and settings

        Returns:
            SparqlServer instance of appropriate type
        """
        server_instance = None
        config_dict = asdict(config)

        if config.server == "blazegraph":
            blazegraph_config = BlazegraphConfig(**config_dict)
            server_instance = Blazegraph(config=blazegraph_config, env=self.env)
        elif config.server == "qlever":
            qlever_config = QLeverConfig(**config_dict)
            server_instance = QLever(config=qlever_config, env=self.env)
        elif config.server == "jena":
            jena_config = JenaConfig(**config_dict)
            server_instance = Jena(config=jena_config, env=self.env)

        return server_instance

    def servers(self, yaml_path: Path) -> Dict[str, SparqlServer]:
        """
        Load active servers from YAML configuration.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            Dictionary mapping server names to SparqlServer instances
        """
        server_configs = ServerConfigs.ofYaml(yaml_path)
        servers_dict = {}

        for server_name, config in server_configs.servers.items():
            if config.active:
                server_instance = self.server4Config(config)
                if server_instance:
                    servers_dict[server_name] = server_instance

        return servers_dict
