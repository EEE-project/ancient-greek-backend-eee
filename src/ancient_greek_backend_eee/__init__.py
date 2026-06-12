from ancient_greek_backend_eee.backend import AncientGreekBackend

try:
    from eee_project import register_tag_type as _reg

    def _ag_paradigm_dispatch(backend, lemma, slot, pos, lang):
        return backend.paradigm(lemma, pos).get(slot.tag, set())

    _reg("ag-paradigm", _ag_paradigm_dispatch)
except ImportError:
    pass

__all__ = ["AncientGreekBackend"]
