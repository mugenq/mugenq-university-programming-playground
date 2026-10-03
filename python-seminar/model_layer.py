### SETUP
import numpy
###





class Layer:

  @staticmethod
  def sigmoid(z):
    return 1/(1 + numpy.exp(-z))

  @staticmethod
  def ReLU(z):
    return z * (z > 0)



  def __init__(self, weights, bias, activation=sigmoid): ## initialize
        self.weights = numpy.array(weights)
        self.activation = activation
        self.bias = numpy.array(bias)

  def __repr__(self): ## represent (when you put the variable alone)
    return f"({self.weights}, activation={self.activation.__name__})"
  def __str__(self): ## string (you can call str() on the function or even print() without having python print "an object at memory location")
    return f"Mat:{self.weights}, Activation:{self.activation.__name__}"
  


  def propagate(self, input):
    return self.activation(numpy.dot(input, self.weights) + self.bias)
  





class Model:
    
    def __init__(self, layers=[]): ## initialize
        self.layers = layers

    def __repr__(self): 
        return f"1"
    def __str__(self): 
        return f"1"



    def forward_propagate(self, input):
      prop = input
      for layer in self.layers:
        prop = layer.propagate(prop)
      return prop


