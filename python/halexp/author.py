

class Author:
    """
    Object representing one of the authors of a document.
    """

    sciencesPoLabsMapping = {
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
        0: 'https://sciencespo.hal.science/PHD-SCPO',
        0: 'https://sciencespo.hal.science/CSO',
        0: 'https://sciencespo.hal.science/MAXPO',
    }


    def __init__(self, full_name, id_hal, lab, lab_id):

        self.fullName = full_name
        self.authIdHal = id_hal
        self.authLab = lab
        self.authLabIdHal = lab_id
        self.authSciencesPoSignature = None
        if lab_id in self.sciencesPoLabsMapping:
            self.authSciencesPoSignature = self.sciencesPoLabsMapping[lab_id]

    def __str__(self):
         return f"{self.fullName} | {self.authIdHal} | {self.authLab}"

    def __eq__(self, other):
        return self.authIdHal == other.authIdHal

    def __hash__(self):
        return hash(self.authIdHal)