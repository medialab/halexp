from unidecode import unidecode


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


    def __init__(self, authFullNameId, authIdHal, fullName, labStructId_is, labStructId_names):

        self.authFullNameId = authFullNameId
        self.authIdHal = authIdHal
        self.fullName = fullName
        self.normalizedFullName = unidecode('-'.join(fullName.split(' ')))
        self.authLabs = labStructId_names
        self.authLabIdHals = list(map(int, labStructId_is))

        self.authSciencesPoSignature = [
            self.sciencesPoLabsMap[k] for k in self.authLabIdHals
            if k in self.sciencesPoLabsMap]


    def __str__(self):
        return f"{self.fullName} | {self.authIdHal} | {' AND '.join(self.authLabs)}"

    def __eq__(self, other):
        if self.authIdHal in ['0', 0] and other.authFullNameId in ['0', 0]:
            return self.normalizedFullName == other.normalizedFullName
        else:
            return self.authIdHal == other.authIdHal

    def __hash__(self):
        if self.authIdHal in ['0', 0]:
            return hash(self.normalizedFullName)
        else:
            return hash(self.authIdHal)

    def isSPSignature(self):
        tmp = any([s in self.sciencesPoLabsMap.keys() for s in self.authLabIdHals])
        return tmp