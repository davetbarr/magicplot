class Plugin(AnalysisPlugin):

    def __init__(self):
        AnalysisPlugin.__init__(self, params={'param1':0, 'param2':42},
            name='Average')

    def run(self):
        if len(self.data) != 2:
            raise Exception('Only works with 1D plots')
        return {'Average': numpy.average(self.data[1][self.params['param1']:self.params['param2']])}

