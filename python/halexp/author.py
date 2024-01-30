

class Author:
    """
    Object representing one of the authors of a document.
    """

    def __init__(self, full_name, id_hal, lab):

        self.authFullName = full_name
        self.authIdHal = id_hal
        self.authLab = lab

    def __str__(self):
         return f"{self.authFullName} | {self.authIdHal} | {self.authLab}"