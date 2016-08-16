class Plugin(TransformPlugin):

    def __init__(self):
        TransformPlugin.__init__(self, params={'add':1},
                name='add')

    def run(self):
        # 1D data has length 2, as in (x,y)
        if len(self.data) == 2:
            return (self.data[0], self.data[1] + self.params['add'])
        else:
            return self.data + self.params['add']
