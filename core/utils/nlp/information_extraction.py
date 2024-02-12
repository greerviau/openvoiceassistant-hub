import spacy
from spacy.matcher import DependencyMatcher

nlp = spacy.load('en_core_web_sm')

ROOMS = [
    "Living Room",
    "Dining Room",
    "Kitchen",
    "Bedroom",
    "Kids Bedroom",
    "Guest Bedroom",
    "Master Bedroom",
    "Bathroom",
    "Home Office",
    "Study",
    "Library",
    "Den",
    "Family Room",
    "Home Theater",
    "Gym",
    "Exercise Room",
    "Laundry Room",
    "Mudroom",
    "Walk-in Closet",
    "Storage Room",
    "Attic Room",
    "Basement",
    "Game Room",
    "Craft Room",
    "Music Room",
    "Sunroom",
    "Conservatory",
    "Wine Cellar",
    "Panic Room",
    "Patio",
    "Deck",
    "Front Porch",
    "Back Porch",
    "Veranda",
    "Balcony",
    "Terrace",
    "Garden",
    "Yard",
    "Pool House",
    "Greenhouse",
    "Garage",
    "Carport",
    "Tool Shed",
    "Storage Shed",
    "Workshop",
    "Playhouse"
]

def extract_information(sentence: str):
    doc = nlp(sentence)

    parsed = {}
    parsed["SUBJECT"], parsed["OBJECT"], parsed["COMP"] = [], [], []

    for token in doc:
        #print(f"{token.text} -> {token.dep_}")
        if (token.dep_=='nsubj'):
            parsed["SUBJECT"].append(token.text)

        elif (token.dep_=='dobj'):
            parsed["OBJECT"].append(token.text)

        elif (token.dep_=='compound'):
            parsed["COMP"].append(token.text)

    parsed["ENTITIES"] = dict([(ent.label_, ent.text) for ent in doc.ents])

    parsed['NOUN_CHUNKS'] = []
    for chunk in doc.noun_chunks:
        parsed['NOUN_CHUNKS'].append(chunk.text)

    object_pattern = [
        {
            "RIGHT_ID": "target",
            "RIGHT_ATTRS": {"POS": "NOUN"}
        },
        # founded -> subject
        {
            "LEFT_ID": "target",
            "REL_OP": ">",
            "RIGHT_ID": "modifier",
            "RIGHT_ATTRS": {"DEP": {"IN": ["amod", "nummod"]}}
        }
    ]

    matcher = DependencyMatcher(nlp.vocab)
    matcher.add("OBJ", [object_pattern])   

    parsed["MOD_OBJECT"] = []
    for match_id, (modifier, target) in matcher(doc):
        parsed["MOD_OBJECT"].append(' '.join([doc[modifier].text, doc[target].text]))

    return parsed

def new_extract_information(sentence: str):
    doc = nlp(sentence)

    # NAMED ENTITIES
    parsed = {}
    parsed["ENTITIES"] = dict([(ent.label_, ent.text) for ent in doc.ents])

    # ROOMS
    rooms = []
    for room in ROOMS:
        room = room.lower()
        if room in sentence.lower():
            rooms.append(room)
    parsed["ROOMS"] = rooms

    # ITEMS
    objects = []
    mod_objects_patterns = [
        {"RIGHT_ID": "target", "RIGHT_ATTRS": {"POS": "NOUN"}},
        {"LEFT_ID": "target", "REL_OP": ">", "RIGHT_ID": "modifier", "RIGHT_ATTRS": {"DEP": {"IN": ["amod", "nummod"]}}}
    ]
    matcher = spacy.matcher.DependencyMatcher(nlp.vocab)
    matcher.add("MODOBJECT", [mod_objects_patterns])
    matches = matcher(doc)
    for match_id, token_ids in matches:
        objects.append(" ".join([doc[token_id].text for token_id in token_ids]))
    for token in doc:
        if (token.dep_=='dobj'):
            objects.append(token.text)
    parsed["OBJECTS"] = objects

    print(parsed)

    return parsed

if __name__ == "__main__":
    while True:
        text = input("Test: ")
        new_extract_information(text)