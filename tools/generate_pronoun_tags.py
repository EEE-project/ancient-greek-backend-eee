"""Regenerate data/pronoun-tags.tsv from greek-inflexion-eee's
pronoun_lexicon.yaml -- run this whenever that lexicon's forms: keys
change (a new lemma, a new cell added to an existing lemma).

Usage (from this repo's root, ~/.venv/eee active, sibling checkout of
greek-inflexion-eee expected at ../greek-inflexion-eee):

    python3 tools/generate_pronoun_tags.py

get_slot_templates()/get_tags() are POS-level, not lemma-level (same
architecture as noun-tags.tsv/adj-tags.tsv: one shared grid serves every
lemma of that pos). But unlike nouns/adjectives, PronType is a genuine
per-LEMMA-FAMILY fact, not a per-TAG one: a given Case+Number+Gender tag
(e.g. .NSM) is legitimately shared across several pronoun families with
DIFFERENT PronType values (οὗτος=Dem, ὅς=Rel, τίς=Int, τις=Ind all have
an NSM cell). An earlier version of this script deduped to one row per
raw tag string (picking a single PronType via priority order), which
silently made Rcp/Int/Ind completely unrepresentable anywhere in the
table -- every one of their cells always collided with a higher-priority
family's identical tag. Fixed by deduping by (tag, PronType) instead:
the same raw tag string legitimately appears once per distinct pronoun
family that attests it (146 rows total, not 60).

Known consequence, not yet fully resolved downstream (flagged during
section-05's code review, 2026-07-12): get_slot_templates("grc",
"pronoun", lang) returns multiple SlotTemplate objects sharing the
identical .tag/.label with different .features["PronType"]. A caller
that picks the FIRST slot matching a tag (e.g. eee-project's
resolve_word_grammar, as currently written) will always resolve to
whichever PronType happens to sort first for a shared tag -- currently
Dem, since demonstrative lemmas are processed first below and Dem's
36-cell shape is a superset of every other adjective-like family's
cells. Any lemma-agnostic tag-only matching strategy has this same
problem; there is no tie-break order that fixes it, since Dem and Rel
have IDENTICAL cell-shapes (either could "win" every shared cell). A
correct fix requires the caller to know the LEMMA's real PronType before
selecting among colliding slots -- out of scope for this script and this
repo's own dispatch code, which never reads PronType internally
(ag_pron_key branches on Gender presence, not PronType).

ὅστις's PronType is assigned "Rel" (indefinite relative), matching
common UD-treebank practice: it introduces a relative clause
morphosyntactically, and the "indefinite" part of "indefinite relative"
is semantic, not a distinct UD PronType value. Structurally this choice
is unobservable in the shipped TSV: ὅστις's own cell-shape (24 cells,
no dual) is a strict subset of ὅς/Rel's 36-cell shape, so it contributes
zero new (tag, PronType) rows regardless of which label it "should" get.
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_LEXICON_SRC = _REPO_ROOT.parent / "greek-inflexion-eee" / "src"
sys.path.insert(0, str(_LEXICON_SRC))
from greek_inflexion_eee.fileformat import _load_lexicon_yaml  # noqa: E402

_OUT_PATH = _REPO_ROOT / "src" / "ancient_greek_backend_eee" / "data" / "pronoun-tags.tsv"

_CASE_REV = {'N': 'Nom', 'A': 'Acc', 'G': 'Gen', 'D': 'Dat', 'V': 'Voc'}
_NUM_REV = {'S': 'Sing', 'P': 'Plur', 'D': 'Dual'}
_GEND_REV = {'M': 'Masc', 'F': 'Fem', 'N': 'Neut'}

_PERSONAL_LEMMAS = {"ἐγώ", "σύ"}
_PRONTYPE = {
    "ἐγώ": "Prs", "σύ": "Prs",
    "οὗτος": "Dem", "ἐκεῖνος": "Dem", "ὅδε": "Dem",
    "ὅς": "Rel",
    "τίς": "Int",
    "τις": "Ind",
    "ὅστις": "Rel",  # see module docstring
    "ἀλλήλων": "Rcp",
}


def main() -> None:
    data = _load_lexicon_yaml("pronoun_lexicon.yaml")

    rows_by_key = {}
    for lemma, entry in data.items():
        prontype = _PRONTYPE[lemma]
        personal = lemma in _PERSONAL_LEMMAS
        for key in entry["forms"]:
            c, n, x = key[0], key[1], key[2]
            tag = "." + key
            if personal:
                row = (tag, _CASE_REV[c], _NUM_REV[n], "", x, prontype)
            else:
                row = (tag, _CASE_REV[c], _NUM_REV[n], _GEND_REV[x], "", prontype)
            rows_by_key[(tag, prontype)] = row

    rows = list(rows_by_key.values())

    # Sort: adjective-like family (has Gender) first, matching noun-tags.tsv's
    # own N-then-G-then-D-then-A-then-V case order; personal family after.
    case_order = {"Nom": 0, "Gen": 1, "Dat": 2, "Acc": 3, "Voc": 4}
    num_order = {"Sing": 0, "Plur": 1, "Dual": 2}
    gend_order = {"Masc": 0, "Fem": 1, "Neut": 2, "": 3}

    def sort_key(row):
        _tag, case, num, gend, pers, _prontype = row
        return (pers != "", case_order[case], num_order[num], gend_order[gend], pers)

    rows.sort(key=sort_key)

    with open(_OUT_PATH, "w", encoding="utf-8") as f:
        f.write("tag\tCase\tNumber\tGender\tPerson\tPronType\n")
        for row in rows:
            f.write("\t".join(row) + "\n")

    print(f"{_OUT_PATH}: {len(rows)} rows written")
    prontypes = sorted({r[5] for r in rows})
    print(f"PronType values present: {prontypes}")


if __name__ == "__main__":
    main()
