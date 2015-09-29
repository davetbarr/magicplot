class Plugin(TransformPlugin):

    def __init__(self):
        TransformPlugin.__init__(self, params={'base':10},
                name='Log')

    def run(self):
        if len(self.data) == 2:
            return numpy.log(self.data[1])
        else:
            return numpy.log(self.data)
