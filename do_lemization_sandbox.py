import nltk
import numpy
# http://ufal.mff.cuni.cz/~zabokrtsky/courses/npfl092/html/nlp-frameworks.html


#with open("genesis.txt", "r") as f:
#   genesis = f.read()

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')


sentences = nltk.sent_tokenize('Jmenuji se Jan Hudec a ziju v Praze.')

# just the first sentence
tokens_0 = nltk.word_tokenize(sentences[0])
print(tokens_0[1])
tagged_0 = nltk.pos_tag(tokens_0)
# all sentences
tokenized_sentences = [nltk.word_tokenize(sent) for sent in sentences]
tagged_sentences = nltk.pos_tag_sents(tokenized_sentences)

ne=nltk.ne_chunk(tagged_0)
print(ne)
#ne.draw()