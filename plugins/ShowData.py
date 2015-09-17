class ShowData(AnalysisPlugin):

    def __init__(self):
        super(ShowData, self).__init__(name='Data')

    def run(self):
        return {'Data': self.data}

global ShowData
plugin = ShowData()
