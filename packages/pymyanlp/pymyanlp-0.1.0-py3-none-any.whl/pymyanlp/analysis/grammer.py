from enum import Enum, auto

class MyanmarParticleType(Enum):
    """Enum representing types of Myanmar particles"""
    FROM_DIRECTION_MARKER = "from direction marker"
    TO_DIRECTION_MARKER = "to direction marker"
    APPELLATIVE = "appellative"
    ADVERBIAL_MARKER = "adverbial marker"
    REALIS_VERB_MARKER = "realis verb marker"
    IRREALIS_VERB_MARKER = "irrealis verb marker"
    SEEKING_AGREEMENT = "seeking agreement"
    ATTRIBUTIVE_MARKER = "attributive marker"
    BENEFACTIVE = "benefactive"
    CAUSATIVE = "causative"
    CLASSIFIER = "classifier"
    POSSESSIVE = "possessive"
    COMPASSION = "compassion"
    CONTINUATIVE = "continuative"
    DISTRIBUTIVE = "distributive"
    EMPHATIC = "emphatic"
    EXCLAMATION = "exclamation"
    EXPERIENTIAL = "experiential"
    EUPHONIC = "euphonic"
    HONORIFIC = "honorific"
    IMPERATIVE = "imperative"
    INADVERTENTLY = "inadvertently"
    IRREALIS = "irrealis"
    NEGATIVE = "negative"
    NORMALISER = "normaliser"
    NORMALISED_REALIS = "normalised realis"
    OBJECT_MARKER = "object marker"
    PLURAL_MARKER = "plural marker"
    POLITE = "polite"
    PURPOSE = "purpose"
    YES_NO_QUESTION = "yes/no-question sentence-final marker"
    WH_QUESTION = "wh-question sentence-final marker"
    QUOTATION_MARKER = "quotation marker"
    REALIS_MODALITY = "realis modality"
    RECIPROCAL = "reciprocal"
    REFLEXIVE = "reflexive"
    REMOTE = "remote; temporal or spatial remoteness"
    RESULTATIVE = "resultative"
    SUBJECT_MARKER = "subject marker"
    SUBJUNCTIVE = "subjunctive"
    SUBORDINATE_CLAUSE_MARKER = "subordinate clause marker"

# Dictionary mapping Myanmar particle characters to their types
myanmar_particle_map = {
    "သည်": MyanmarParticleType.SUBJECT_MARKER,
    "က": MyanmarParticleType.SUBJECT_MARKER,
    "မှာ": MyanmarParticleType.SUBJECT_MARKER,

    "ကို": MyanmarParticleType.OBJECT_MARKER,

    "မှ": MyanmarParticleType.FROM_DIRECTION_MARKER,
    "က ၂": MyanmarParticleType.FROM_DIRECTION_MARKER,

    "သို့": MyanmarParticleType.TO_DIRECTION_MARKER,
    "ကို ၂": MyanmarParticleType.TO_DIRECTION_MARKER,

    "ရယ်": MyanmarParticleType.APPELLATIVE,
    "စွာ": MyanmarParticleType.ADVERBIAL_MARKER,
    "တဲ့": MyanmarParticleType.REALIS_VERB_MARKER,
    "မဲ့": MyanmarParticleType.IRREALIS_VERB_MARKER,
    "‌နော်": MyanmarParticleType.SEEKING_AGREEMENT,
    "သော": MyanmarParticleType.ATTRIBUTIVE_MARKER,
    "ပေး": MyanmarParticleType.BENEFACTIVE,
    "စေ": MyanmarParticleType.CAUSATIVE,
    "ခု": MyanmarParticleType.CLASSIFIER,

    "ရဲ့": MyanmarParticleType.POSSESSIVE,
    "၏": MyanmarParticleType.POSSESSIVE,

    "ရှာ": MyanmarParticleType.COMPASSION,
    "နေ": MyanmarParticleType.CONTINUATIVE,
    "စီ": MyanmarParticleType.DISTRIBUTIVE,
    "ပဲ": MyanmarParticleType.EMPHATIC,
    "တကား": MyanmarParticleType.EXCLAMATION,
    "ဖူး": MyanmarParticleType.EXPERIENTIAL,
    "လေ": MyanmarParticleType.EUPHONIC,
    "တော်": MyanmarParticleType.HONORIFIC,

    "နဲ့": MyanmarParticleType.IMPERATIVE,
    "ဖြင့်": MyanmarParticleType.IMPERATIVE,
    "နှင့်": MyanmarParticleType.IMPERATIVE,
    "နဲ့": MyanmarParticleType.IMPERATIVE,

    "မိ": MyanmarParticleType.INADVERTENTLY,
    "မယ်": MyanmarParticleType.IRREALIS,
    "မ": MyanmarParticleType.NEGATIVE,
    "ခြင်း": MyanmarParticleType.NORMALISER,
    "တာ": MyanmarParticleType.NORMALISED_REALIS,

    "တွေ": MyanmarParticleType.PLURAL_MARKER,
    "များ": MyanmarParticleType.PLURAL_MARKER,
    "တို့": MyanmarParticleType.PLURAL_MARKER,

    "လား": MyanmarParticleType.YES_NO_QUESTION,
    "လဲ": MyanmarParticleType.WH_QUESTION,

    "ပါ": MyanmarParticleType.POLITE,
    "ဖို့": MyanmarParticleType.PURPOSE,
    "လို့": MyanmarParticleType.QUOTATION_MARKER,
    "တယ်": MyanmarParticleType.REALIS_MODALITY,
    "အချင်းချင်း": MyanmarParticleType.RECIPROCAL,
    "ကိုယ်": MyanmarParticleType.REFLEXIVE,
    "ခဲ့": MyanmarParticleType.REMOTE,
    "ထား": MyanmarParticleType.RESULTATIVE,
    "ဖြစ်ဖြစ်": MyanmarParticleType.SUBJUNCTIVE,
    "၍": MyanmarParticleType.SUBORDINATE_CLAUSE_MARKER,
}

# For backward compatibility
myanmar_particles = [(p_type.value, particle) for particle, p_type in myanmar_particle_map.items()]

"""
Agreement errors

Word order errors

Missing words (particularly prepositions)

Misused prepositions

Unwanted prepositions
"""