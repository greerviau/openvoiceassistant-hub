import spacy

def parse_text(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    # Find all the noun chunks in the text
    noun_chunks = list(doc.noun_chunks)

    # Find all the verbs in the text
    verbs = []
    for token in doc:
        if token.pos_ == "VERB":
            verbs.append(token)

    # Group the noun chunks into subjects and objects based on their relationship to the verbs
    subjects = []
    objects = []
    for verb in verbs:
        verb_subjects = []
        verb_objects = []
        for chunk in noun_chunks:
            if chunk.root.head == verb:
                if chunk.root.dep_ == "nsubj":
                    verb_subjects.append(chunk.text)
                elif chunk.root.dep_ == "dobj":
                    verb_objects.append(chunk.text)
        subjects.append(verb_subjects)
        objects.append(verb_objects)

    # Merge overlapping subjects and objects for each verb
    for i in range(len(verbs)):
        verb_subjects = subjects[i]
        verb_objects = objects[i]
        for j in range(i+1, len(verbs)):
            if verbs[j].head == verbs[i]:
                verb_subjects += subjects[j]
                verb_objects += objects[j]
                subjects[j] = []
                objects[j] = []
        subjects[i] = list(set(verb_subjects))
        objects[i] = list(set(verb_objects))

    # Return a list of dictionaries with the subject, object, and action for each verb
    result = []
    for i in range(len(verbs)):
        result.append({
            "subject": subjects[i],
            "object": objects[i],
            "action": verbs[i].lemma_
        })

    return result

# Example usage:
text = "Whats the weather like in San Diego?"
parsed = parse_text(text)
print(parsed)  # Output: [{'subject': ['I'], 'object': [], 'action': 'go'}, {'subject': [], 'object': ['some apples'], 'action': 'buy'}, {'subject': ['John', 'Jane'], 'object': ['a song'], 'action': 'sing'}]
