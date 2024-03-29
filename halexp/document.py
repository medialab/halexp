from .author import Author


class Document:
    """
    Object representing a piece of text (i.e.: a serie of phrases)
    to be embedded together with the metadatq from the HAL document
    to wich it belongs to.
    """

    def __init__(self, phrases, max_length, **kwargs):
        """

        include_title [boolean]: wheter to include or not the title of HAL
        document in the text to be embedded.

        include_author [boolean]: wheter to include or not the author
        (first name and last name) of HAL document in the text to be embedded.

        include_keywords [boolean]: wheter to include or not the keywords of
        the HAL document in the text to be embedded.

        """
        self.metadata = {}
        self.title = None
        self.publication_date = -1
        self.year = -1
        self.uri = ""
        self.halId = ""
        self.authors = []
        self.keywords = []
        self.open_acces = None
        self.subtitle = ""
        self.phrases = []

        self.max_length = max_length
        self.setPhrases(phrases)

    def __str__(self):
        _str = f"{self.title}\n\t{self.publication_date}\n\t{self.halId}"
        for n, a in enumerate(self.authors):
            _str += f"\n\tAuthor {n}: {a}"
        _str += f"\n\t`{self.getPhrasesForEmbedding()}`"
        return _str

    def __eq__(self, other):
        return self.halId == other.halId

    def __hash__(self):
        return hash(self.halId+self.title)

    def setPhrases(self, phrases):
        l0 = len(phrases)
        if l0 > self.max_length:
            m = f"Document: crop phrases from ({l0})"
            m += f" to max number ({self.max_length})."
            # print(m)
            phrases = phrases[:self.max_length]
        self.phrases = phrases

    def setMetadata(self, metadata):
        self.metadata = metadata

    def setTitle(self, title):
        self.title = title+'.'

    def setUri(self, uri):
        self.uri = uri

    def setHalId(self, halId):
        self.halId = halId

    def setSubtitle(self, subtitle):
        self.subtitle = subtitle

    def setOpenAccess(self, open_access):
        self.open_acces = open_access

    def setPublicationDate(self, publication_date):
        self.publication_date = publication_date
        self.publication_year = int(publication_date.split('-')[0])

    def setKeywords(self, keywords):
        self.keywords = keywords

    def setAuthors(self, authorsData):
        self.authors = [
        Author(
            authFullNameId,
            data['authId_i'],
            data['authFullName_s'],
            data['authPrimStrucId'],
            data['authPrimStrucName'],
                    ) for authFullNameId, data in authorsData.items()]

    def setAuthLastName(self, authLastName):
        self.authLastName = authLastName

    def getHalId(self):
        return self.halId

    def getAuthors(self):
        return self.authors

    def getAuthorsFullNamesStr(self):
        return ', '.join(self.getAuthorsFullNames())

    def getAuthorsFullNames(self):
        return [a.fullName for a in self.authors]

    def getPhrasesForEmbedding(self):
        return ' '.join(self.phrases)
