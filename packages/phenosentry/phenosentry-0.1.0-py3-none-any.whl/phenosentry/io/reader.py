import zipfile

from ..model.phenopacket_store import PhenopacketStore
from ..model.input_mode import InputMode
import logging

def read_phenopacket_store(
    directory: str, mode: InputMode,
    logger: logging.Logger,
) -> PhenopacketStore:
    logger.info("Reading phenopackets at `%s`", directory)
    phenopacket_store = None
    if mode == InputMode.STORE:
        phenopacket_store = PhenopacketStore.from_notebook_dir(directory)
    elif mode == InputMode.FOLDER:
        phenopacket_store = PhenopacketStore.from_folder(directory)
    elif mode == InputMode.FILE:
        phenopacket_store = PhenopacketStore.from_file(directory)
        logger.info(
            "Read %d cohorts with %d phenopackets",
            phenopacket_store.cohort_count(),
            phenopacket_store.phenopacket_count(),
        )
    elif mode == InputMode.ZIP:
        with zipfile.ZipFile(directory) as zfh:
            phenopacket_store = PhenopacketStore.from_release_zip(zip_file=zfh, strategy="eager")
    return phenopacket_store