class VMWriter:
    def __init__(self, output_file):
        self.output_file = output_file
        self.output_file = open(output_file, 'w')

    def write_push(self, segment, index):
        self.output_file.write('push ' + segment + ' ' + str(index) + '\n')

    def write_pop(self, segment, index):
        self.output_file.write('pop ' + segment + ' ' + str(index) + '\n')

    def write_arithmetic(self, command):
        self.output_file.write(command + '\n')

    def write_label(self, label):
        self.output_file.write('label ' + label + '\n')

    def write_goto(self, label):
        self.output_file.write('goto ' + label + '\n')

    def write_if(self, label):
        self.output_file.write('if-goto ' + label + '\n')

    def write_call(self, name, n_args):
        self.output_file.write('call ' + name + ' ' + str(n_args) + '\n')

    def write_function(self, name, n_locals):
        self.output_file.write('function ' + name + ' ' + str(n_locals) + '\n')

    def write_return(self):
        self.output_file.write('return\n')

    def close(self):
        self.output_file.close()
