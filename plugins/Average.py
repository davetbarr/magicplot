class Plugin(AnalysisPlugin):

    def __init__(self):
        AnalysisPlugin.__init__(self, params={},
            name='Average')

    def run(self):
        return {'Average': numpy.average(self.data)}

