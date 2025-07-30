"""
Read-only viewing of Jupyter notebooks in the web browser.
"""

from __future__ import annotations

import logging
from pathlib import Path

import typer
from rich.logging import RichHandler

__version__ = "0.0.4"

logging.basicConfig(
    format="%(message)s",
    datefmt=f"[%X] {__name__}",
    handlers=[RichHandler(rich_tracebacks=True, markup=True, show_path=False)],
)

log = logging.getLogger(__name__)

app = typer.Typer(name="nbv", add_completion=False)


def _main(
    notebook: str | Path,
    *,
    theme: str = "light",
    template: str = "lab",
    cli: bool = False,
    debug: bool = False,
) -> None:
    """Convert notebook to HTML using nbconvert and open in default web browser."""
    import subprocess
    import tempfile
    import webbrowser

    p0 = Path(notebook)

    tf = tempfile.NamedTemporaryFile(
        prefix=f"notebook={p0.name}_",
        suffix=".html",
        delete=False,
    )
    tf.close()
    p = Path(tf.name)

    # TODO: theme/template options
    # [x] default templates: lab (default), classic, basic
    # [x] default themes: light (default), dark
    # other templates: toc ?
    # other themes: https://github.com/dunovank/jupyter-themes ?
    if cli:
        # fmt: off
        cmd = [
            "jupyter-nbconvert", str(p0),
            "--to", "html",
            "--theme", theme,
            "--template", template,
            "--output", p.as_posix(),
        ]
        # fmt: on
        log.info(f"Invoking '{' '.join(cmd)}'.")
        cp = subprocess.run(cmd, capture_output=not debug)
        if cp.returncode != 0:
            if cp.stderr is not None:
                suff = ":\n...\n" + "\n".join(cp.stderr.decode().splitlines()[-3:])
            else:
                suff = "."
            raise Exception(f"Command '{' '.join(cmd)}' failed{suff}")
    else:
        from nbconvert import HTMLExporter

        exporter = HTMLExporter(
            template_name=template,
            theme=theme,
        )

        log.info(f"Converting '{p0.as_posix()}' to HTML using nbconvert Python API.")
        (body, resources) = exporter.from_filename(p0.as_posix())

        with open(p, "w", encoding="utf-8") as f:
            f.write(body)

    # TODO: browser option using https://docs.python.org/3/library/webbrowser.html#webbrowser.get
    log.info(f"Opening '{p.as_posix()}' in default web browser.")
    webbrowser.open(f"file://{p.as_posix()}", new=2, autoraise=True)


def _try(fn, *args, **kwargs) -> bool:
    """Handle possible exception, returning True if one occurred."""
    try:
        fn(*args, **kwargs)
    except Exception as e:
        msg = f"Invoking `{fn.__name__}` failed"
        if kwargs.get("debug", False):
            log.exception(f"{msg}.")
        else:
            log.error(f"{msg} with message: [bold]{e}[/]")
        return True
    else:
        return False


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"nbv {__version__}")

        try:
            import nbconvert
        except ImportError:
            pass
        else:
            typer.echo(f"found nbconvert {nbconvert.__version__} (Python API)")

        import subprocess

        try:
            cp = subprocess.run(
                ["jupyter-nbconvert", "--version"],
                text=True,
                capture_output=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        else:
            typer.echo(f"found jupyter-nbconvert {cp.stdout.strip()} (CLI)")

        raise typer.Exit()


@app.command(no_args_is_help=True, help="View Jupyter notebook in web browser.")
def main(
    notebook: Path = typer.Argument(..., help="Notebook file to open."),
    theme: str = typer.Option("light", help="HTML theme to use."),
    template: str = typer.Option("lab", help="HTML template to use."),
    cleanup: bool = typer.Option(
        False,
        "--cleanup/",
        help="First remove previous nbv HTML notebook files from the temp dir.",
    ),
    use_nbconvert_cli: bool = typer.Option(
        None,
        help=(
            "Use nbconvert CLI available on PATH. "
            "Default is to use the nbconvert Python API if installed, "
            "otherwise attempt to use the CLI."
        ),
        show_default=False,
        envvar="NBV_USE_NBCONVERT_CLI",
        show_envvar=False,
    ),
    debug: bool = typer.Option(False, "--debug/", help="Enable info/debug messages."),
    version: bool = typer.Option(
        False,
        "--version/",
        help="Print version.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    log.setLevel(logging.DEBUG if debug else logging.WARNING)

    if use_nbconvert_cli is None:
        try:
            import nbconvert  # noqa: F401
        except ImportError:
            log.info("Failed to import nbconvert Python API, will use CLI.")
            use_nbconvert_cli = True
        else:
            log.info("nbconvert library is available, will use.")
            use_nbconvert_cli = False

    if cleanup:
        import os
        import tempfile

        to_remove = list(Path(tempfile.gettempdir()).glob("notebook=*_*.html"))
        log.info(f"Found {len(to_remove)} old notebook HTML files in the temp dir.")
        for p in to_remove:
            os.remove(p)

    p = notebook
    if not p.suffix == ".ipynb":
        log.error("Only '.ipynb' files are supported.")
        raise typer.Exit(2)

    if not p.is_file():
        log.error(f"File {p.as_posix()!r} does not exist.")
        raise typer.Exit(2)

    if theme == "dark" and template in {"basic", "classic"}:
        typer.echo(
            "Note that theme 'dark' is only applied with template 'lab' (the default template)."
        )

    err = _try(
        _main,
        p,
        theme=theme,
        template=template,
        cli=use_nbconvert_cli,
        debug=debug,
    )

    raise typer.Exit(int(err))


if __name__ == "__main__":
    app()
