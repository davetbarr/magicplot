class Plugin(AnalysisPlugin):

    def __init__(self):
        #super(ShowData, self).__init__(name='Data')
        AnalysisPlugin.__init__(self, name='Data')

    def run(self):
        return self.data
