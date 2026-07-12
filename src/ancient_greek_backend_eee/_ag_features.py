"""Pure UD FEATS → TVM key mapping module.

No imports from greek_inflexion_eee. Zero external runtime dependencies.

TVM key format used by greek_inflexion_eee:
  Tense (1 char) + Voice (1 char) + Mood/Form (1 char) [+ "." + suffix]
  e.g. "PAI.1S" = Present Active Indicative 1st Singular

Voice=Mid,Pass returns None from ag_verb_key — caller unions M and P results.
Absent Gender returns None from ag_noun_key / ag_adj_key — caller unions all genders.
ag_pron_key never returns None: absent Gender routes to its Person-keyed
branch instead of triggering a union, since Gender's absence is the
permanent, correct state for personal pronouns, not a caller omission.
"""

# Tense
T_PRES = 'P'
T_IMP  = 'I'
T_AOR  = 'A'
T_FUT  = 'F'
T_PERF = 'X'
T_PLUP = 'Y'

# Voice
V_ACT  = 'A'
V_MID  = 'M'
V_PASS = 'P'

# Mood / Form
M_IND  = 'I'
M_SUB  = 'S'
M_OPT  = 'O'
M_IMP  = 'D'
M_INF  = 'N'
M_PART = 'P'

_TENSE = {
    'Pres': T_PRES,
    'Imp':  T_IMP,
    'Aor':  T_AOR,
    'Fut':  T_FUT,
    'Perf': T_PERF,
    'Pqp':  T_PLUP,
}

_VOICE = {
    'Act':  V_ACT,
    'Mid':  V_MID,
    'Pass': V_PASS,
}

_MOOD = {
    ('Fin',  'Ind'): M_IND,
    ('Fin',  'Sub'): M_SUB,
    ('Fin',  'Opt'): M_OPT,
    ('Fin',  'Imp'): M_IMP,
    ('Inf',  None):  M_INF,
    ('Part', None):  M_PART,
}

_PERSNUM = {
    ('1', 'Sing'): '1S',
    ('2', 'Sing'): '2S',
    ('3', 'Sing'): '3S',
    ('1', 'Plur'): '1P',
    ('2', 'Plur'): '2P',
    ('3', 'Plur'): '3P',
    ('1', 'Dual'): '1D',
    ('2', 'Dual'): '2D',
    ('3', 'Dual'): '3D',
}

_CASE = {'Nom': 'N', 'Acc': 'A', 'Gen': 'G', 'Dat': 'D', 'Voc': 'V'}
_NUM  = {'Sing': 'S', 'Plur': 'P', 'Dual': 'D'}
_GEND = {'Masc': 'M', 'Fem': 'F', 'Neut': 'N'}


def ag_verb_key(features: dict[str, str]) -> str | None:
    """Compose a TVM key string from UD verb features.

    Returns None when Voice is 'Mid,Pass' (sentinel for union-of-M-and-P).
    Raises KeyError if VerbForm, Tense, or (for finite forms) Person/Number is absent.
    Unknown feature keys are silently ignored.
    """
    t = _TENSE[features['Tense']]
    voice = features['Voice']
    if voice == 'Mid,Pass':
        return None
    v = _VOICE[voice]
    verbform = features['VerbForm']
    m = _MOOD[(verbform, features.get('Mood'))]
    key = t + v + m
    if verbform == 'Fin':
        key += '.' + _PERSNUM[(features['Person'], features['Number'])]
    elif verbform == 'Part':
        key += '.' + _CASE[features['Case']] + _NUM[features['Number']] + _GEND[features['Gender']]
    return key


def ag_noun_key(features: dict[str, str]) -> str | None:
    """Return a .CSG suffix string (e.g. '.NSM') from UD nominal features.

    Returns None when Gender is absent — caller unions across all genders.
    Raises KeyError if Case or Number is absent.
    Unknown feature keys are silently ignored.
    """
    case = features['Case']
    number = features['Number']
    gender = features.get('Gender')
    if gender is None:
        return None
    return '.' + _CASE[case] + _NUM[number] + _GEND[gender]


def ag_adj_key(features: dict[str, str]) -> str | None:
    """Return a .CSG suffix string from UD adjective features.

    Degree feature is ignored here; the caller (backend) handles degree dispatch.
    Returns None when Gender is absent.
    Raises KeyError if Case or Number is absent.
    """
    case = features['Case']
    number = features['Number']
    gender = features.get('Gender')
    if gender is None:
        return None
    return '.' + _CASE[case] + _NUM[number] + _GEND[gender]


def ag_pron_key(features: dict[str, str]) -> str:
    """Compose a tag-key string from UD pronoun features.

    Branches on Gender presence, not PronType:
      - Gender present (demonstrative/relative/interrogative/indefinite/
        reciprocal): identical Case+Number+Gender composition to
        ag_adj_key, dot-prefixed.
      - Gender absent (personal pronouns, ἐγώ/σύ): a new Case+Number+
        Person composition, also dot-prefixed for the same backend
        cache-key convention.
    Gender-presence is already the established branch signal ag_noun_key/
    ag_adj_key use elsewhere in this module; PronType only needs to be
    present in the caller's features dict for downstream rendering to
    consume, not consulted here.

    Unlike ag_noun_key/ag_adj_key, this never returns None: Gender's
    absence is the *normal*, permanent state for personal pronouns, not
    a caller omission requesting a cross-gender union.

    Raises KeyError if Case or Number is absent, or if the relevant axis
    (Gender for the first branch, Person for the second) is missing.
    """
    case = features['Case']
    number = features['Number']
    gender = features.get('Gender')
    if gender is not None:
        return '.' + _CASE[case] + _NUM[number] + _GEND[gender]
    person = features['Person']
    return '.' + _CASE[case] + _NUM[number] + person
