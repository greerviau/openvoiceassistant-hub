from flair.data import Sentence
from flair.nn import Classifier
import time

# make a sentence
sentence = Sentence('set a timer for 15 minutes 60 seconds')

# load the NER tagger
tagger = Classifier.load('ner-ontonotes-large')

start = time.time()
# run NER over sentence
tagger.predict(sentence)
print('Elapsed: ', time.time()-start)

# print the sentence with all annotations
print(sentence)