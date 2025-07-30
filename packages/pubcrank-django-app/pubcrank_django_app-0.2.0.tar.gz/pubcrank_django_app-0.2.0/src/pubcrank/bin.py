from pathlib import Path
import os
import sys

from piou import Cli, Option
from rich.console import Console

import django

from pubcrank.crank import Crank


econsole = Console(stderr=True, style="bold red")
cli = Cli(description='Pubcrank static site generator')

ConfigOption = Option(Path("pubcrank.hjson"), "-c", "--config", help="config file path")
DjangoOption = Option(Path("."), "-d", "--django", help="path to django project")
VerboseOption = Option(False, "-v", help="verbose output")
SettingsOption = Option(None, "-s", "--settings", help="django settings module")


def setup_django(django_dir, settings=None):
  sys.path.append(str(django_dir))

  if settings:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

  django.setup()


def eprint(message):
  econsole.print(f"Error: {message}")


@cli.command(help='build your site')
def build(
  config: Path = ConfigOption,
  django_dir: Path = DjangoOption,
  settings: str = SettingsOption,
  verbose: bool = VerboseOption,
  baseurl: str = Option("/", "--base-url", help="base URL for site"),
  noclear: bool = Option(False, "--no-clear", help="disable clear directory before building"),
  outdir: Path = Option(Path('output'), "-o", "--output", help="output directory", raise_path_does_not_exist=False)
):
  if not config.exists():
    eprint("Config file does not exist.")
    sys.exit(1)

  if outdir.exists() and not outdir.is_dir():
    eprint("Output must be a directory.")
    sys.exit(1)

  setup_django(django_dir, settings)
  crank = Crank(config, baseurl, verbose=verbose)
  crank.build(outdir, noclear=noclear)

if __name__ == '__main__':
  cli.run()
