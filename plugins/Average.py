class Average(AnalysisPlugin):

    def __init__(self):
        super(Average, self).__init__(params={'param1':0, 'param2':42},
            name='Average')

    def run(self):
        if len(self.data) != 2:
            raise Exception('Only works with 1D plots')
        return {'Average': numpy.average(self.data[1][self.params['param1']:self.params['param2']])}

global Average
plugin = Average()
