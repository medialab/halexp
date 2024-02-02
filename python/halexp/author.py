

class Author:
    """
    Object representing one of the authors of a document.
    """

    def __init__(self, full_name, id_hal, lab):

        self.fullName = full_name
        self.authIdHal = id_hal
        self.authLab = lab

    def __str__(self):
         return f"{self.fullName} | {self.authIdHal} | {self.authLab}"

    def __eq__(self, other):
        return self.authIdHal == other.authIdHal

    def __hash__(self):
        return hash(self.authIdHal)
