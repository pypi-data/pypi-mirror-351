import sys
from pathlib import Path

import typer

from ..app import app, app_state
from ..utils.error_hook import setup_global_error_logging

from ...providers import available_providers

# Import commands
from . import run, data, compile

__all__ = ['run', 'data', 'compile']


@app.callback()
def setup(
        ctx: typer.Context,
        workdir: Path = typer.Option(
            app_state.workdir,
            "--workdir", "-w",
            envvar="PYNE_WORK_DIR",
            help="Working directory",
            file_okay=False, dir_okay=True,
            resolve_path=True,
        ),
):
    """
    Pyne Command Line Interface
    """
    if ctx.resilient_parsing or ctx.invoked_subcommand is None:
        return
    if any(arg in ('-h', '--help') for arg in sys.argv[1:]):
        return

    typer.echo("")

    # Check if workdir is available
    workdir_existed = Path(workdir).exists()
    if not workdir_existed:
        typer.echo(f"Working directory '{workdir}' does not exist.")
        typer.confirm("Do you want to create it?", abort=True)

        # Create workdir
        Path(workdir).mkdir(parents=True, exist_ok=False)

    # Create scripts directory
    scripts_dir = Path(workdir) / 'scripts' / 'lib'
    scripts_dir.mkdir(parents=True, exist_ok=True)

    # Create demo.py file only if we created the workdir in this run
    if not workdir_existed:
        demo_file = Path(workdir) / 'scripts' / 'demo.py'
        if not demo_file.exists():
            with demo_file.open('w') as f:
                f.write('''"""
@pyne
Simple Pyne Script Demo

A basic demo showing a 12 and 26 period EMA crossover system.
"""
from pynecore import Series
from pynecore.lib import script, input, plot, color, ta


@script.indicator(
    title="Simple EMA Crossover Demo",
    shorttitle="EMA Demo",
    overlay=True
)
def main(
    src: Series[float] = input.source("close", title="Price Source"),
    fast_length: int = input.int(12, title="Fast EMA Length"),
    slow_length: int = input.int(26, title="Slow EMA Length")
):
    """
    A simple EMA crossover demo
    """
    # Calculate EMAs
    fast_ema = ta.ema(src, fast_length)
    slow_ema = ta.ema(src, slow_length)

    # Plot our indicators
    plot(fast_ema, title="Fast EMA", color=color.blue)
    plot(slow_ema, title="Slow EMA", color=color.red)
''')

    # Create data directory
    data_dir = Path(workdir) / 'data'
    data_dir.mkdir(exist_ok=True)
    # Create output and logs directory
    output_dir = Path(workdir) / 'output' / 'logs'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create config directory
    config_dir = Path(workdir) / 'config'
    config_dir.mkdir(exist_ok=True)

    # Create providers.toml file for all supported providers (if not exists)
    providers_file = config_dir / 'providers.toml'
    if not providers_file.exists():
        with providers_file.open('w') as f:
            for provider in available_providers:
                f.write(f"[{provider}]\n")
                provider_module = __import__(f"pynecore.providers.{provider}", fromlist=[''])
                provider_class = getattr(
                    provider_module,
                    [p for p in dir(provider_module) if p.endswith('Provider')][0]
                )
                for key, value in provider_class.config_keys.items():
                    if key.startswith('#'):  # Comments
                        f.write(f'{key}\n')
                    else:
                        if isinstance(value, str):
                            f.write(f'{key} = "{value}"\n')
                        elif isinstance(value, bool):
                            f.write(f'{key} = {str(value).lower()}\n')
                        elif isinstance(value, int) or isinstance(value, float):
                            f.write(f'{key} = {value}\n')
                        else:
                            raise ValueError(f"Unsupported type for {key}: {type(value)}")
                f.write("\n")

    # Set workdir in app_state
    app_state.workdir = workdir

    # Setup global error logging
    setup_global_error_logging(workdir / "output" / "logs" / "error.log")
