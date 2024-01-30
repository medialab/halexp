from .author import Author


class Document:
    """
    Object representing a piece of text (i.e.: a serie of phrases)
    to be embedded together with the metadatq from the HAL document
    to wich it belongs to.
    """

    def __init__(self, max_length, include_title, include_author, **kwargs):
        """
        max_length [int]: maximum lenght of the serie of phrases.

        include_title [boolean]: wheter to include or not the title of HAL
        document in the text to be embedded.

        include_author [boolean]: wheter to include or not the author
        (first name and last name) of HAL document in the text to be embedded.
        """
        self.phrases = []
        self.metadata = {}
        self.max_length = -1

        self.title = ""
        self.publication_date = -1
        self.uri = ""
        self.authors = []
        self.open_acces = None

        self.max_length = max_length
        self.include_title = include_title
        self.include_author = include_author

    def __str__(self):
        _str = f"Document:\n\t{self.title}\n\t{self.publication_date}"
        for n, a in enumerate(self.authors):
            _str += f"\n\tAuthor {n}: {a}"
        return _str

    def setMetadata(self, metadata):
        self.metadata = metadata

    def setTitle(self, title):
        self.title = title

    def setUri(self, uri):
        self.uri = uri

    def setOpenAccess(self, open_access):
        self.open_acces = open_access

    def setPublicationDate(self, publication_date):
        self.publication_date = publication_date

    def setAuthors(self, authors_full_names, authors_idhal, authors_labs):
        assert type(authors_full_names) == list
        assert type(authors_idhal) == list
        assert type(authors_labs) == list
        assert set(map(type, authors_labs)) == {str}
        assert set(map(type, authors_full_names)) == {str}
        assert set(map(type, authors_idhal)) == {int}
        self.authors = [
            Author(n, i, l)
            for n, i, l in zip(authors_full_names, authors_idhal, authors_labs)]


    def setAuthLastName(self, authLastName):
        self.authLastName = authLastName

    def add_phrase(self, new_phrase):
        if len(self.phrases) >= self.max_length:
            raise ValueError(
                f"Number of max phrases ({self.max_length}) already attended.")
        self.phrases.append(new_phrase)

    def getPhrasesForEmbedding(self):
        data = self.phrases
        if self.include_title:
            data += [self.title]
        if self.include_author:
            data += [self.authFirstName, self.authLastName]
        return ' '.join(data)