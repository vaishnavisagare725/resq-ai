"""Rule-based triage for emergency reports.

Pure Python: no Django imports, so it is easy to test and easy to replace
with a machine-learning model later.
"""
import re

URGENCY_LEVELS = ['low', 'medium', 'high', 'critical']

# (phrase, urgency). The highest urgency among the matched phrases wins.
URGENCY_SIGNALS = [
    # critical: life at immediate risk
    ('not breathing', 'critical'), ("can't breathe", 'critical'), ('cannot breathe', 'critical'),
    ('unconscious', 'critical'), ('unresponsive', 'critical'), ('not responding', 'critical'),
    ('trapped', 'critical'), ('heart attack', 'critical'), ('cardiac arrest', 'critical'),
    ('heavy bleeding', 'critical'), ('bleeding heavily', 'critical'), ('drowning', 'critical'),
    ('explosion', 'critical'), ('stabbed', 'critical'), ('gunshot', 'critical'),
    ('collapsed', 'critical'),
    # high: serious danger
    ('fire', 'high'), ('smoke', 'high'), ('burning', 'high'), ('flames', 'high'), ('blaze', 'high'),
    ('bleeding', 'high'), ('injured', 'high'), ('accident', 'high'), ('crash', 'high'),
    ('crashed', 'high'), ('collision', 'high'), ('collided', 'high'), ('overturned', 'high'),
    ('flood', 'high'), ('flooded', 'high'), ('flooding', 'high'), ('landslide', 'high'),
    ('gas leak', 'high'), ('fracture', 'high'), ('chest pain', 'high'), ('seizure', 'high'),
    ('fainted', 'high'), ('burn', 'high'), ('burns', 'high'),
    # medium: needs attention
    ('water logging', 'medium'), ('waterlogging', 'medium'), ('fallen tree', 'medium'),
    ('road blocked', 'medium'), ('short circuit', 'medium'), ('stuck', 'medium'),
    ('leak', 'medium'), ('sick', 'medium'), ('fever', 'medium'), ('pain', 'medium'),
    ('dizzy', 'medium'),
]

# One level up for children, elderly people, or crowds.
RAISERS = [
    'child', 'children', 'kid', 'kids', 'baby', 'infant', 'elderly', 'pregnant',
    'many people', 'several people', 'multiple people', 'crowd', 'dozens',
]

# keyword -> weight, per category
CATEGORY_KEYWORDS = {
    'fire': {
        'fire': 3, 'smoke': 2, 'burning': 2, 'flames': 3, 'blaze': 3,
        'explosion': 3, 'gas leak': 2, 'short circuit': 2,
    },
    'medical': {
        'heart attack': 3, 'cardiac arrest': 3, 'unconscious': 3, 'unresponsive': 3,
        'not responding': 2, 'not breathing': 3, 'cannot breathe': 3, "can't breathe": 3,
        'chest pain': 3, 'seizure': 3, 'collapsed': 2, 'fainted': 2, 'bleeding': 2,
        'heavy bleeding': 2, 'ambulance': 2, 'injured': 1, 'sick': 1, 'fever': 1, 'pain': 1,
    },
    'flood': {
        'flood': 3, 'flooded': 3, 'flooding': 3, 'water logging': 2, 'waterlogging': 2,
        'drowning': 3, 'landslide': 3, 'overflowing': 2,
    },
    'accident': {
        'accident': 2, 'crash': 2, 'crashed': 2, 'collision': 3, 'collided': 3,
        'hit and run': 3, 'overturned': 2, 'skidded': 2,
    },
}
CATEGORY_PRIORITY = ['fire', 'accident', 'flood', 'medical']   # used to break ties

NEGATION_BEFORE = re.compile(r'\b(no|not|without|never|false)\s*$')
NOBODY_BEFORE = re.compile(r'\b(no one|nobody)( is| was| are)?\s*$')


def _normalise(text):
    text = text.lower().replace('\u2019', "'")          # curly apostrophe -> straight
    return re.sub(r'\s+', ' ', text).strip()


def _present(text, phrase):
    """True if the phrase appears as whole words and is not negated ("no fire")."""
    for match in re.finditer(r'\b' + re.escape(phrase) + r'\b', text):
        before = text[max(0, match.start() - 20):match.start()]
        if NEGATION_BEFORE.search(before) or NOBODY_BEFORE.search(before):
            continue
        return True
    return False


def predict(title, description):
    text = _normalise(f'{title}. {description}')

    # 1. urgency: the highest matched level
    matched = []
    level = 0
    for phrase, name in URGENCY_SIGNALS:
        if _present(text, phrase):
            matched.append(phrase)
            level = max(level, URGENCY_LEVELS.index(name))

    # 2. raise one level for vulnerable people or crowds (medium and high only)
    raised = False
    if 1 <= level < 3 and any(_present(text, word) for word in RAISERS):
        level += 1
        raised = True

    # 3. category: the highest weighted score, ties broken by priority
    scores = {
        category: sum(weight for word, weight in words.items() if _present(text, word))
        for category, words in CATEGORY_KEYWORDS.items()
    }
    best = max(CATEGORY_PRIORITY, key=lambda c: (scores[c], -CATEGORY_PRIORITY.index(c)))
    category = best if scores[best] > 0 else 'other'

    urgency = URGENCY_LEVELS[level]

    # 4. explain the decision
    parts = []
    if matched:
        parts.append(f"urgency {urgency} from: {', '.join(matched)}")
    if raised:
        parts.append('raised one level: vulnerable person or many people')
    if category != 'other':
        found = [w for w in CATEGORY_KEYWORDS[category] if _present(text, w)]
        parts.append(f"category {category} from: {', '.join(found)}")
    if not parts:
        parts.append('no emergency keywords found: a responder must triage this report')

    return {
        'urgency': urgency,
        'category': category,
        'needs_review': category == 'other' or not matched,
        'reason': '. '.join(parts)[:300],
    }