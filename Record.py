from newspaper import Article
import nltk
from itertools import groupby


class Record(object):
    def __init__(self, url, nlp=False):
        # newspaper library to extract basic article details
        article = Article(url)
        article.download()
        article.parse()

        # Data fields to fulfill
        self.identifier = article.publish_date.year
        self.location = None
        self.hijack_location = None
        self.hijack_found = None
        self.date_incident = None
        self.date_reported = str(article.publish_date.day) + '/' + str(article.publish_date.month) + '/' + str(article.publish_date.year)
        self.incident_tag = None
        self.incident_summary = None
        self.incident_type_primary = None
        self.incident_type_secondary = None
        self.violent = None
        self.incident_type = None
        self.weapon = None
        self.notes = None
        self.time_operation = None
        self.time_incident = None
        self.motive = None
        self.suspect_occupation = None
        self.suspect_age = None
        self.suspect_name = None
        self.suspect_gender = None
        self.victim_occupation = None
        self.victim_age = None
        self.victim_name = None
        self.victim_gender = None
        self.money = None
        self.valuables = None
        self.url = url
        self.title = article.title
        self.linkage = None

        # Additional data fields
        self.text = article.text
        self.tags = article.tags
        self.meta_keywords = article.meta_keywords
        self.authors = article.authors

        # Gleaned from nlp
        self.keywords = []
        print(self.url)

        self.nlp_computed = nlp
        if nlp:
            print('Analyzing')
            article.nlp()
            print(article.summary)
            self.incident_summary = article.summary
            self.keywords = article.keywords
            print(self.text)

    def nlp_builtin(self):
        # Prevent builtin nlp from being re-run
        if not self.nlp_computed:
            self.nlp_computed = True

            # Download, parse process article
            article = Article(self.url)
            article.download()
            article.parse()
            article.nlp()

            self.incident_summary = article.summary
            self.keywords = article.keywords

    def nlp_nltk(self):
        # Break text into words
        tokens = nltk.word_tokenize(self.text)

        # Tag words with grammar using Penn Treebank
        # https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
        tagged = nltk.pos_tag(tokens)

        # Chunk sentence into hierarchical tree
        tree = nltk.ne_chunk(tagged)

        # Add IOB labeling
        IOB = nltk.chunk.tree2conlltags(tree)

        # Group proper nouns spread across multiple words
        for tag, chunk in groupby(IOB, lambda x: x[1]):
            if tag != "O":
                print("%-12s" % tag, " ".join(w for w, t in chunk))

    def nlp_stanford(self):
        # Break text into words
        tokens = nltk.word_tokenize(self.text)

        # Create object that will tag tokens
        tagger = nltk.tag.StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')

        tagger.tag(tokens)

    def elements(self):
        return [self.identifier, self.location, self.hijack_location, self.hijack_found, self.date_incident,
                self.date_reported, self.incident_tag, self.incident_summary, self.incident_type_primary,
                self.incident_type_secondary, self.violent, self.incident_type, self.weapon, self.notes,
                self.time_operation, self.time_incident, self.motive, self.suspect_occupation, self.suspect_age,
                self.suspect_name, self.suspect_gender, self.victim_occupation, self.victim_age,
                self.victim_name, self.victim_gender, self.money, self.valuables, self.url, self.title, self.linkage]

    @staticmethod
    def header():
        return ['Identifier', 'Location', 'If Hijacking, location of crime',
                'If hijacking_location where car/boat was found', 'Date_of_in', 'Date_repor', 'Incident_T',
                'Incident_s', 'Primary_Incident_Type', 'Secondary_Incident_Type', 'Violent_NonV', 'Incident_Type',
                'Weapon', 'Notes', 'Time of operation', 'Estimated Time of Incident', 'Primary_Mo',
                'Suspect_occupation', 'Suspect_age', "Suspect's_name", "Suspect's_gender", 'Victim_Occupation',
                'Victim_Age', "Victim's_name", "Victim's_gender", 'Money_', 'Valuables', 'Link_to_story', 'Title',
                'More_detai']
