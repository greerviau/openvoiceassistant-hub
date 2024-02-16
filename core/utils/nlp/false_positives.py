import os

FALSE_POSITIVES = []
false_positives_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'false_positives.txt')
with open(false_positives_path, 'r') as file:
    print(false_positives_path)
    FALSE_POSITIVES = file.readlines()
    print("Loaded false positives")

def add_false_positive(text: str):
    print("False positive saved")
    with open(false_positives_path, 'a') as file:
        file.write(f"\n{text}")

if __name__ == "__main__":
    from nlp import clean_text
    filtered = "\n".join(list(set([f"\"{clean_text(phrase)}\"," for phrase in FALSE_POSITIVES])))
    with open(false_positives_path, 'w') as file:
        file.write(filtered)