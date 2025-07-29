import click
import logging

from .model import InputMode
from .validation import qc_phenopackets
from .io import read_phenopacket_store

def setup_logging():
    level = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s %(name)-20s %(levelname)-3s : %(message)s"
    )
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

@click.group()
def main():
    pass

@main.command('validate')
@click.option("--path", type=click.Path(exists=True, readable=True), required=True)
@click.option(
    "--mode",
    type=click.Choice([m.value for m in InputMode]),
    required=True,
    help="Input type: store (phenopacket-store), folder (set-of-phenopackets), or file (single-phenpacket)."
)
def validate(path, mode):
    setup_logging()
    logger = logging.getLogger(__name__)
    mode_enum = InputMode(mode)
    store = read_phenopacket_store(path, mode_enum, logger)
    qc_phenopackets(store, logger)


if __name__ == '__main__':
    main()