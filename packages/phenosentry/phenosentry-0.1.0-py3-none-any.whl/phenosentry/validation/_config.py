from ._api import PhenopacketStoreAuditor
from ._checks import DefaultPhenopacketStoreAuditor, UniqueIdsCheck, NoUnwantedCharactersCheck, DeprecatedTermIdCheck
import hpotk

def default_auditor() -> PhenopacketStoreAuditor:
    store = hpotk.configure_ontology_store()
    hpo = store.load_hpo()
    checks = (
        UniqueIdsCheck(),
        NoUnwantedCharactersCheck.no_whitespace(),
        DeprecatedTermIdCheck(hpo)
    )
    return DefaultPhenopacketStoreAuditor(checks=checks)