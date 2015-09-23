class Plugin(TransformPlugin):

    def __init__(self):
        TransformPlugin.__init__(self, params={'base':10},
                name='Log')

    def run(self):
        return numpy.log(self.data)
