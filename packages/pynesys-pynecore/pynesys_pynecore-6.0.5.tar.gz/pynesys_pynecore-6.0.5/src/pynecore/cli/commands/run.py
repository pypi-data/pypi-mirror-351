from pathlib import Path
from datetime import datetime

from typer import Option, Argument, secho, Exit
from rich.progress import (Progress, SpinnerColumn, TextColumn, BarColumn,
                           TimeElapsedColumn, TimeRemainingColumn)

from ..app import app, app_state

from ...utils.rich.date_column import DateColumn
from pynecore.core.ohlcv_file import OHLCVReader

from pynecore.core.syminfo import SymInfo
from pynecore.core.script_runner import ScriptRunner

__all__ = []


@app.command()
def run(
        script: Path = Argument(..., dir_okay=False, file_okay=True, help="Script to run"),
        data: Path = Argument(..., dir_okay=False, file_okay=True,
                              help="Data file to use (*.ohlcv)"),
        time_from: datetime | None = Option(None, '--from', '-f',
                                            formats=["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"],
                                            help="Start date (UTC), if not specified, will use the "
                                                 "first date in the data"),
        time_to: datetime | None = Option(None, '--to', '-t',
                                          formats=["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"],
                                          help="End date (UTC), if not specified, will use the last "
                                               "date in the data"),
        plot_path: Path | None = Option(None, "--plot", "-pp",
                                        help="Path to save the plot data",
                                        rich_help_panel="Out Path Options"),
        strat_path: Path | None = Option(None, "--strat", "-sp",
                                         help="Path to save the strategy statistics",
                                         rich_help_panel="Out Path Options"
                                         ),
        equity_path: Path | None = Option(None, "--equity", "-ep",
                                          help="Path to save the equity curve",
                                          rich_help_panel="Out Path Options"),
):
    """
    Run a script

    The system automatically searches for the workdir folder in the current and parent directories.
    If not found, it creates or uses a workdir folder in the current directory.

    If [bold]script[/] path is a name without full path, it will be searched in the [italic]"workdir/scripts"[/] directory.
    Similarly, if [bold]data[/] path is a name without full path, it will be searched in the [italic]"workdir/data"[/] directory.
    The [bold]plot_path[/], [bold]strat_path[/], and [bold]equity_path[/] work the same way - if they are names without full paths,
    they will be saved in the [italic]"workdir/output"[/] directory.
    """  # noqa
    # Ensure .py extension
    if script.suffix != ".py":
        script = script.with_suffix(".py")
    # Expand script path
    if len(script.parts) == 1:
        script = app_state.scripts_dir / script
    # Check if script exists
    if not script.exists():
        secho(f"Script file '{script}' not found!", fg="red", err=True)
        raise Exit(1)

    # Check file format and extension
    if data.suffix == "":
        # No extension, add .ohlcv
        data = data.with_suffix(".ohlcv")
    elif data.suffix != ".ohlcv":
        # Has extension but not .ohlcv
        secho(f"Cannot run with '{data.suffix}' files. The PyneCore runtime requires .ohlcv format.",
              fg="red", err=True)
        secho("If you're trying to use a different data format, please convert it first:", fg="red")
        symbol_placeholder = "YOUR_SYMBOL"
        timeframe_placeholder = "YOUR_TIMEFRAME"
        secho(f"pyne data convert-from {data} --symbol {symbol_placeholder} --timeframe {timeframe_placeholder}",
              fg="yellow")
        raise Exit(1)

    # Expand data path
    if len(data.parts) == 1:
        data = app_state.data_dir / data
    # Check if data exists
    if not data.exists():
        secho(f"Data file '{data}' not found!", fg="red", err=True)
        raise Exit(1)

    # Ensure .csv extension for plot path
    if plot_path and plot_path.suffix != ".csv":
        plot_path = plot_path.with_suffix(".csv")
    if not plot_path:
        plot_path = app_state.output_dir / f"{script.stem}.csv"

    # Ensure .csv extension for strategy path
    if strat_path and strat_path.suffix != ".csv":
        strat_path = strat_path.with_suffix(".csv")
    if not strat_path:
        strat_path = app_state.output_dir / f"{script.stem}_strat.csv"

    # Ensure .csv extension for equity path
    if equity_path and equity_path.suffix != ".csv":
        equity_path = equity_path.with_suffix(".csv")
    if not equity_path:
        equity_path = app_state.output_dir / f"{script.stem}_equity.csv"

    # Get symbol info for the data
    try:
        syminfo = SymInfo.load_toml(data.with_suffix(".toml"))
    except FileNotFoundError:
        secho(f"Symbol info file '{data.with_suffix('.toml')}' not found!", fg="red", err=True)
        raise Exit(1)

    # Open data file
    with OHLCVReader(data) as reader:
        if not time_from:
            time_from = reader.start_datetime
        if not time_to:
            time_to = reader.end_datetime
        time_from = time_from.replace(tzinfo=None)
        time_to = time_to.replace(tzinfo=None)

        total_seconds = int((time_to - time_from).total_seconds())

        # Get the iterator
        size = reader.get_size(int(time_from.timestamp()), int(time_to.timestamp()))
        ohlcv_iter = reader.read_from(int(time_from.timestamp()), int(time_to.timestamp()))

        with Progress(
                SpinnerColumn(finished_text="[green]✓"),
                TextColumn("{task.description}"),
                DateColumn(time_from),
                BarColumn(),
                TimeElapsedColumn(),
                "/",
                TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task(
                description="Running script...",
                total=total_seconds,
            )

            def cb_progress(current_time: datetime | None):
                """ Callback to update progress """
                if current_time == datetime.max:
                    current_time = time_to
                assert current_time is not None
                elapsed_seconds = int((current_time - time_from).total_seconds())
                progress.update(task, completed=elapsed_seconds)

            # Create script runner
            runner = ScriptRunner(script, ohlcv_iter, syminfo, last_bar_index=size - 1,
                                  plot_path=plot_path, strat_path=strat_path, equity_path=equity_path)
            # Run the script
            runner.run(on_progress=cb_progress)
