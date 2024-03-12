

class Author:
    """
    Object representing one of the authors of a document.
    """

    sciencesPoLabsMap = {
        301587: 'https://sciencespo.hal.science',
        1846: 'https://sciencespo.hal.science/CDSP',
        94080: 'https://sciencespo.hal.science/CEE',
        1011: 'https://sciencespo.hal.science/CERI',
        1009: 'https://sciencespo.hal.science/CEVIPOF',
        45663: 'https://sciencespo.hal.science/CHSP',
        1140212: 'https://sciencespo.hal.science/CRIS',
        109691: 'https://sciencespo.hal.science/DROIT-SCPO',
        226874: 'https://sciencespo.hal.science/ECON-SCPO',
        394361: 'https://sciencespo.hal.science/MEDIALAB',
        250936: 'https://sciencespo.hal.science/OFCE',
        218465: 'https://sciencespo.hal.science/LIEPP',
        1059: 'https://sciencespo.hal.science/CSO',
        237254: 'https://sciencespo.hal.science/MAXPO',
        # 0: 'https://sciencespo.hal.science/PHD-SCPO',
    }


    def __init__(self, full_name, id_hal, labStructId_i, labStructId_name):

        self.fullName = full_name
        self.authIdHal = id_hal
        self.authLab = labStructId_name
        self.authLabIdHal = labStructId_i
        self.authSciencesPoSignature = None
        if labStructId_i in self.sciencesPoLabsMap:
            self.authSciencesPoSignature = self.sciencesPoLabsMap[labStructId_i]

    def __str__(self):
        return f"{self.fullName} | {self.authIdHal} | {self.authLab}"

    def __eq__(self, other):
        return self.authIdHal == other.authIdHal

    def __hash__(self):
        return hash(self.authIdHal)