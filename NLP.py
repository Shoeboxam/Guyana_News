import nltk
from itertools import groupby
from newspaper import Article


def nltk_ner(record):
    """Named entity recognition via NLTK"""
    # Break text into words
    tokens = nltk.word_tokenize(record.text)

    # Tag words with grammar using Penn Treebank
    # https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    tagged = nltk.pos_tag(tokens)

    # Chunk sentence into hierarchical tree
    tree = nltk.ne_chunk(tagged)

    # Add IOB labeling
    IOB = nltk.chunk.tree2conlltags(tree)

    # Group proper nouns spread across multiple words
    print()
    print(record.url)
    for tag, chunk in groupby(IOB, lambda x: x[2][2:]):
        if tag != "":
            print("%-12s" % tag, " ".join(w for w, t, x in chunk))

    return record


def nlp_stanford(record):
    # Break text into words
    tokens = nltk.word_tokenize(record.text)

    # Create object that will tag tokens
    tagger = nltk.tag.StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')

    tagger.tag(tokens)


def newspaper_summary(record):
    """Update the summary with representative sentences"""
    # This function is inefficient, because it has to redownload and parse the article to make an Article object

    # Prevent builtin nlp from being re-run
    if not record.nlp_computed:
        record.nlp_computed = True

        # Download, parse process article
        article = Article(record.url)
        article.download()
        article.parse()
        article.nlp()

        record.incident_summary = article.summary
        record.keywords = article.keywords

    return record