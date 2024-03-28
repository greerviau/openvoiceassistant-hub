import re
import spacy
from spacy.matcher import DependencyMatcher
import logging
logger = logging.getLogger("utils.nlp.information_extraction")

nlp = spacy.load("en_core_web_sm")

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
    "Closet",
    "Walk-in Closet",
    "Back Stairs",
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

# Combine common prefix with different specific patterns
music_patterns = [
    r"\b(play|start playing|put on)\b\s+(?P<song>[A-Za-z0-9\s'-]+?)?(?:\s+by\s+(?P<artist>[A-Za-z0-9\s'-]+?))?(?:\s+on\s+(?P<platform>[A-Za-z0-9\s'-]+?))?$"
]

def extract_music_info(sentence):
    music_info = {}

    for pattern in music_patterns:
        match = re.match(pattern, sentence, re.IGNORECASE)
        if match:
            # Extract information using named groups
            info = {key: value.strip() for key, value in match.groupdict().items() if value is not None}
            music_info.update(info)

    return music_info

def find_compounds(token):
    compounds = []
    for child in token.children:
        if child.dep_ == "compound":
            compounds.insert(0, child.text)
            compounds = find_compounds(child) + compounds
        elif child.dep_ == "amod":  # Handle adjectives modifying the object
            compounds.insert(0, child.text)
            compounds = find_compounds(child) + compounds
    return compounds

def extract_information(sentence: str):
    sentence = sentence.lower()
    doc = nlp(sentence)
    parsed = {}

    parsed["POS_TAGGING"] = [(token.text, token.dep_) for token in doc]

    # NAMED ENTITIES
    parsed["ENTITIES"] = dict([(ent.label_, ent.text) for ent in doc.ents])

    # ROOMS
    parsed["ROOMS"] = [room.lower() for room in ROOMS if room.lower() in sentence.lower()]

    #MUSIC
    parsed["MUSIC"] = extract_music_info(sentence)

    # ITEMS
    items = []
    for token in doc:
        if token.dep_ == "dobj" or token.dep_ == "conj":
            compound_object = find_compounds(token) + [token.text]
            items.append(" ".join(compound_object))

    parsed["ITEMS"] = list(set(items))

    # OBJECTS
    objects = []
    for token in doc:
        if token.dep_ == "pobj":
            compound_object = find_compounds(token) + [token.text]
            objects.append(" ".join(compound_object))

    parsed["OBJECTS"] = list(set(objects))

    return parsed

if __name__ == "__main__":
    while True:
        text = input("Test: ")
        new_extract_information(text)