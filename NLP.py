import nltk
from itertools import groupby

# Only needs to be run once
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')


def nltk_ner(text):
    """Named entity recognition via NLTK"""
    # Break text into words
    tokens = nltk.word_tokenize(text)

    # Tag words with grammar using Penn Treebank
    # https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    tagged = nltk.pos_tag(tokens)

    # Chunk sentence into hierarchical tree
    tree = nltk.ne_chunk(tagged)

    # Add IOB labeling
    IOB = nltk.chunk.tree2conlltags(tree)

    # Group proper nouns spread across multiple words
    tags = {
        'gpe': [],
        'person': [],
        'organization': []
    }
    for label, chunk in groupby(IOB, lambda x: x[2][2:]):
        if label.lower() in tags:
            match = " ".join(w for w, t, x in chunk)
            tags[label.lower()].append(match)
            # print("%-12s" % label, match)

    return tags


def nlp_stanford(record):
    # Break text into words
    tokens = nltk.word_tokenize(record.text)

    # Create object that will tag tokens
    tagger = nltk.tag.StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')

    tagger.tag(tokens)
