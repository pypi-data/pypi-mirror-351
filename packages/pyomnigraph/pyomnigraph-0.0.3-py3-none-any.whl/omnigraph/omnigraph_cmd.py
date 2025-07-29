"""
Created on 2025-05-28

@author: wf
"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter, Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List
import webbrowser

from omnigraph.ominigraph_paths import OmnigraphPaths
from omnigraph.omniserver import OmniServer
from omnigraph.sparql_server import SparqlServer, ServerEnv
from omnigraph.version import Version


@dataclass
class ServerCmd:
    """
    Command wrapper for server operations.
    """

    def __init__(self, title: str, func: Callable):
        """
        Initialize server command.

        Args:
            title: Description of the command
            func: Function to execute
        """
        self.title = title
        self.func = func

    def run(self, verbose: bool = True) -> any:
        """
        Execute the server command.

        Args:
            verbose: Whether to print result

        Returns:
            Result from function execution
        """
        result = self.func()
        if verbose:
            print(f"{self.title}: {result}")
        return result

class OmnigraphCmd:
    """
    Command line interface for omnigraph.
    """

    def __init__(self):
        """
        Initialize command line interface.
        """
        self.ogp = OmnigraphPaths()
        self.default_yaml_path = self.ogp.examples_dir / "servers.yaml"
        self.version = Version()
        self.program_version_message = f"{self.version.name} {self.version.version}"
        self.parser = self.getArgParser()

    def getArgParser(self, description: str = None, version_msg=None) -> ArgumentParser:
        """
        Setup command line argument parser

        Args:
            description(str): the description
            version_msg(str): the version message

        Returns:
            ArgumentParser: the argument parser
        """
        if description is None:
            description = self.version.description
        if version_msg is None:
            version_msg = self.program_version_message

        parser = ArgumentParser(
            description=description, formatter_class=RawDescriptionHelpFormatter
        )
        parser.add_argument(
            "-a",
            "--about",
            help="show about info [default: %(default)s]",
            action="store_true",
        )
        parser.add_argument(
            "-c","--config",
            type=str,
            default=str(self.default_yaml_path),
            help="Path to server configuration YAML file [default: %(default)s]"
        )
        parser.add_argument(
            "--cmd",
            nargs="+",
            help="commands to execute on servers: start, stop, status"
        )
        parser.add_argument(
            "-d",
            "--debug",
            action="store_true",
            help="show debug info [default: %(default)s]",
        )
        parser.add_argument(
            "-l",
            "--list-servers",
            action="store_true",
            help="List available servers [default: %(default)s]"
        )
        parser.add_argument(
            "-s","--servers",
            nargs="+",
            default=["blazegraph"],
            help="servers: servers to work with - all is an alias for all servers [default: %(default)s]"
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="show verbose output [default: %(default)s]",
        )
        parser.add_argument("-V", "--version", action="version", version=version_msg)
        return parser

    def getServers(self) -> Dict[str, SparqlServer]:
        """
        Get the servers to work with.

        Returns:
            Dictionary of active servers
        """
        servers = {}
        server_names = self.args.servers
        if "all" in server_names:
            server_names = list(self.all_servers.keys())
        for server_name in server_names:
            server = self.all_servers.get(server_name)
            if server:
                servers[server_name] = server
        return servers

    def run_cmds(self, server: SparqlServer, cmds: List[str]) -> bool:
        """
        Run commands on a server.

        Args:
            server: Server instance
            cmds: List of commands to execute

        Returns:
            True if any commands were handled
        """
        handled=False
        s_cmds = {
            "start": ServerCmd(title=f"start {server.name}", func=server.start),
            "stop": ServerCmd(title=f"stop {server.name}", func=server.stop),
            "status": ServerCmd(title=f"status {server.name}", func=server.status)
        }
        if cmds:
            for cmd in cmds:
                s_cmd=s_cmds.get(cmd)
                if s_cmd:
                    s_cmd.run()
                    handled=True
                else:
                    print(f"unsupported command {cmd}")
        return handled


    def handle_args(self,args:Namespace) -> bool:
        """
        Handle command line arguments.

        Returns:
            bool: True if arguments were handled, False otherwise
            args: Namespace
        """
        self.args=args
        handled = False
        self.all_servers={}
        if Path(self.args.config).exists():
            env=ServerEnv(debug=args.debug,verbose=args.verbose)
            omni_server=OmniServer(env=env)
            self.all_servers = omni_server.servers(args.config)
        else:
            print(f"Config file not found: {args.config}")

        if args.about:
            print(self.program_version_message)
            print(f"{len(self.servers)} servers configured")
            print(f"see {self.version.doc_url}")
            webbrowser.open(self.version.doc_url)
            handled = True

        if self.args.list_servers:
            print("Available servers:")
            for name, server in self.servers.items():
                print(f"  {name}: {server.config.server}")
            handled = True

        self.servers=self.getServers()
        for server in self.servers.values():
            handled=handled or self.run_cmds(server,cmds=args.cmd)

        return handled

def main():
    """
    Main entry point for command line interface.
    """
    cmd = OmnigraphCmd()
    args = cmd.parser.parse_args()
    cmd.handle_args(args)


if __name__ == "__main__":
    main()