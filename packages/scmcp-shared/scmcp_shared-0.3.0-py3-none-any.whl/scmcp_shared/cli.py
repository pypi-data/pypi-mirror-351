import typer
from typing import Optional, Union, Type
from enum import Enum
from .util import add_figure_route, set_env,setup_mcp


class TransportEnum(str, Enum):
    STDIO = "stdio"
    SSE = "sse"
    SHTTP = "shttp"

    @property
    def transport_value(self) -> str:
        """Get the actual transport value to use."""
        if self == TransportEnum.SHTTP:
            return "streamable-http"
        return self.value


class ModuleEnum(str, Enum):
    """Base class for module types."""
    ALL = "all"



class MCPCLI:
    """Base class for CLI applications with support for dynamic modules and parameters."""
    
    def __init__(self, name: str, help_text: str, manager=None, modules=ModuleEnum):
        self.name = name
        self.modules = modules
        self.manager = manager
        self.app = typer.Typer(
            name=name,
            help=help_text,
            add_completion=False,
            no_args_is_help=True,
        )
        self._setup_commands()
    
    def _setup_commands(self):
        """Setup the main commands for the CLI."""
        self.app.command(name="run", help="Start the server with the specified configuration")(self.run_command())
        self.app.callback()(self._callback)

    def run_command(self):
        def _run_command(
            log_file: Optional[str] = typer.Option(None, "--log-file", help="log file path, use stdout if None"),
            transport: TransportEnum = typer.Option(TransportEnum.STDIO, "-t", "--transport", help="specify transport type", 
                                        case_sensitive=False),
            port: int = typer.Option(8000, "-p", "--port", help="transport port"),
            host: str = typer.Option("127.0.0.1", "--host", help="transport host"),
            forward: str = typer.Option(None, "-f", "--forward", help="forward request to another server"),
            module: list[self.modules] = typer.Option(
                [self.modules.ALL], 
                "-m", 
                "--module", 
                help="specify module to run"
            ),
        ):
            """Start the server with the specified configuration."""
            if "all" in module:
                modules = None
            elif isinstance(module, list) and bool(module):
                modules = [m.value for m in module]
            self.mcp =  self.manager(self.name, include_modules=modules).mcp

            self.run_mcp(log_file, forward, transport, host, port)
        return _run_command
        

    def _callback(self):
        """Liana MCP CLI root command."""
        pass

    def run_mcp(self, log_file, forward, transport, host, port):
        set_env(log_file, forward, transport, host, port)
        from .logging_config import setup_logger
        setup_logger(log_file)
        if transport == "stdio":
            self.mcp.run()
        elif transport in ["sse", "shttp"]:
            add_figure_route(self.mcp)
            transport = transport.transport_value
            self.mcp.run(
                transport=transport,
                host=host, 
                port=port, 
                log_level="info"
            )
 
    def run_cli(self, mcp=None, module_dic=None):
        """Run the CLI application."""
        self.mcp = mcp
        self.module_dic = module_dic
        self.app()
