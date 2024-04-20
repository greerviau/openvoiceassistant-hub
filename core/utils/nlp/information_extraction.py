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

def text_to_seconds(text: str) -> int:
    # Define regex pattern to match time units and their fractions
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:and\s+a\s+(half))?\s*(hour|minute|second)s?',
        r'(\d+(?:\.\d+)?)\s*(?:and\s+a\s+(half))?\s*(hour|minute|second)s?'
    ]

    # Find all matches in the text
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            total_seconds = 0
            for match in matches:
                value, fraction, unit = match
                value = float(value)
                if fraction:
                    value += 0.5  # Increment by half if "half" is present
                if unit == 'hour':
                    total_seconds += value * 3600
                elif unit == 'minute':
                    total_seconds += value * 60
                elif unit == 'second':
                    total_seconds += value
            return int(total_seconds)
    return 0

if __name__ == "__main__":
    text1 = "1 hour and 30 seconds"
    text2 = "2 and a half hours"
    text3 = "1 hour, 30 minutes, and 15 seconds"
    text4 = "2 and a half minutes"
    text5 = "a half hour"
    text6 = "an hour and a half"

    print(text_to_seconds(text1))  # Output: 3630
    print(text_to_seconds(text2))  # Output: 9000
    print(text_to_seconds(text3))  # Output: 5415
    print(text_to_seconds(text4))  # Output: 150
    print(text_to_seconds(text5))  # Output: 1800
    print(text_to_seconds(text6))  # Output: 5400
    '''
    while True:
        text = input("Test: ")
        new_extract_information(text)
    '''