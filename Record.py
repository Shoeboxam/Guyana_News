from newspaper import Article
import sqlite3

connection = sqlite3.connect('Newspaper_Records.db')
cursor = connection.cursor()


class Record(object):
    def __init__(self, url, memoize=True):

        selection = cursor.execute('SELECT * FROM articles WHERE Link_to_story = ? LIMIT 1', (str(url),)).fetchall()

        if memoize and selection:
            # Data fields to fulfill
            entry = selection[0]

            self.identifier = entry[0]
            self.location = entry[1]
            self.hijack_location = entry[2]
            self.hijack_found = entry[3]
            self.date_incident = entry[4]
            self.date_reported = entry[5]
            self.incident_tag = entry[6]
            self.incident_summary = entry[7]
            self.incident_type_primary = entry[8]
            self.incident_type_secondary = entry[9]
            self.violent = entry[10]
            self.incident_type = entry[11]
            self.weapon = entry[12]
            self.notes = entry[13]
            self.time_operation = entry[14]
            self.time_incident = entry[15]
            self.motive = entry[16]
            self.suspect_occupation = entry[17]
            self.suspect_age = entry[18]
            self.suspect_name = entry[19]
            self.suspect_gender = entry[20]
            self.victim_occupation = entry[21]
            self.victim_age = entry[22]
            self.victim_name = entry[23]
            self.victim_gender = entry[24]
            self.money = entry[25]
            self.valuables = entry[26]
            self.url = entry[27]
            self.title = entry[28]
            self.linkage = entry[29]

            # Additional data fields
            self.text = entry[30]
            self.tags = entry[31]
            self.meta_keywords = entry[32]
            self.authors = entry[33]

            # Gleaned from nlp
            self.keywords = entry[34]

        # Create new record with most fields unpopulated
        else:
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
            self.date_reported = str(article.publish_date.day) + '/' + str(article.publish_date.month) + '/' + \
                                 str(article.publish_date.year)
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
            self.tags = str(article.tags)
            self.meta_keywords = str(article.meta_keywords)
            self.authors = str(article.authors)

            # Gleaned from nlp
            self.keywords = str([])

    @staticmethod
    def header_csv():
        return ('Identifier', 'Location', 'If Hijacking, location of crime',
                'If hijacking_location where car/boat was found', 'Date_of_in', 'Date_repor', 'Incident_T',
                'Incident_s', 'Primary_Incident_Type', 'Secondary_Incident_Type', 'Violent_NonV', 'Incident_Type',
                'Weapon', 'Notes', 'Time of operation', 'Estimated Time of Incident', 'Primary_Mo',
                'Suspect_occupation', 'Suspect_age', "Suspect's_name", "Suspect's_gender", 'Victim_Occupation',
                'Victim_Age', "Victim's_name", "Victim's_gender", 'Money_', 'Valuables', 'Link_to_story', 'Title',
                'More_detai')

    def get_csv_elements(self):
        return (self.identifier, self.location, self.hijack_location, self.hijack_found, self.date_incident,
                self.date_reported, self.incident_tag, self.incident_summary, self.incident_type_primary,
                self.incident_type_secondary, self.violent, self.incident_type, self.weapon, self.notes,
                self.time_operation, self.time_incident, self.motive, self.suspect_occupation, self.suspect_age,
                self.suspect_name, self.suspect_gender, self.victim_occupation, self.victim_age,
                self.victim_name, self.victim_gender, self.money, self.valuables, self.url, self.title, self.linkage)

    @staticmethod
    def header_db():
        return ('Identifier', 'Location', 'If Hijacking, location of crime',
                'If hijacking_location where car/boat was found', 'Date_of_in', 'Date_repor', 'Incident_T',
                'Incident_s', 'Primary_Incident_Type', 'Secondary_Incident_Type', 'Violent_NonV', 'Incident_Type',
                'Weapon', 'Notes', 'Time of operation', 'Estimated Time of Incident', 'Primary_Mo',
                'Suspect_occupation', 'Suspect_age', "Suspect's_name", "Suspect's_gender", 'Victim_Occupation',
                'Victim_Age', "Victim's_name", "Victim's_gender", 'Money_', 'Valuables', 'Link_to_story', 'Title',
                'More_detai', 'Fulltext', 'Tags', 'Keywords_Meta', 'Authors', 'Keywords')

    def get_db_elements(self):
        return (self.identifier, self.location, self.hijack_location, self.hijack_found, self.date_incident,
                self.date_reported, self.incident_tag, self.incident_summary, self.incident_type_primary,
                self.incident_type_secondary, self.violent, self.incident_type, self.weapon, self.notes,
                self.time_operation, self.time_incident, self.motive, self.suspect_occupation, self.suspect_age,
                self.suspect_name, self.suspect_gender, self.victim_occupation, self.victim_age,
                self.victim_name, self.victim_gender, self.money, self.valuables, self.url, self.title, self.linkage,
                self.text, self.tags, self.meta_keywords, self.authors, self.keywords)

    def store_to_database(self):
        if cursor.execute('SELECT * FROM articles WHERE Link_to_story = ? LIMIT 1', (self.url,)).fetchall():
            assignment = ''
            for header, element in zip(self.header_db(), self.get_db_elements()):
                assignment += str(header) + ' = ' + str(element) + ', '
            cursor.execute("UPDATE articles SET " + assignment + " WHERE Link_to_story = ?", (str(self.url),))
        else:
            elements = self.get_db_elements()
            cursor.execute("INSERT INTO articles VALUES (" + "?, " * (len(elements) - 1) + "?)", (*elements,))
        connection.commit()
