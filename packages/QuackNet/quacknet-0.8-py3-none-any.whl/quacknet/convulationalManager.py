from quacknet.convulationalFeutures import ConvulationalNetwork
from quacknet.convulationalBackpropagation import CNNbackpropagation
from quacknet.activationDerivativeFunctions import ReLUDerivative
from quacknet.convulationalOptimiser import CNNoptimiser
import numpy as np

class CNNModel(CNNoptimiser):
    def __init__(self, NeuralNetworkClass):
        self.layers = []
        self.weights = []
        self.biases = []
        self.NeuralNetworkClass = NeuralNetworkClass
    
    def addLayer(self, layer):
        self.layers.append(layer)
    
    def forward(self, inputTensor):
        allTensors = [inputTensor]
        for layer in self.layers:
            inputTensor = layer.forward(inputTensor)
            allTensors.append(inputTensor)
        return allTensors

    def backpropagation(self, allTensors, trueValues):
        weightGradients, biasGradients, errorTerms = self.layers[-1].backpropagation(trueValues) # <-- this is a neural network 
        allWeightGradients = [weightGradients]
        allBiasGradients = [biasGradients]
        for i in range(len(self.layers) - 2, -1, -1):
            if(type(self.layers[i]) == PoolingLayer or type(self.layers[i]) == ActivationLayer):
                errorTerms = self.layers[i].backpropagation(errorTerms, allTensors[i])
            elif(type(self.layers[i]) == ConvLayer):
                weightGradients, biasGradients, errorTerms = self.layers[i].backpropagation(errorTerms, allTensors[i])
                allWeightGradients.insert(0, weightGradients)
                allBiasGradients.insert(0, biasGradients)
        
        return allWeightGradients, allBiasGradients
    
    def optimser(self, inputData, labels, useBatches, weights, biases, batchSize, alpha, beta1, beta2, epsilon):
        if(useBatches == True):
            return CNNoptimiser.AdamsOptimiserWithBatches(self, inputData, labels, weights, biases, batchSize, alpha, beta1, beta2, epsilon)
        else:
            return CNNoptimiser.AdamsOptimiserWithoutBatches(self, inputData, labels, weights, biases, alpha, beta1, beta2, epsilon)
    
    def train(self, inputData, labels, useBatches, batchSize, alpha = 0.001, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8):
        correct, totalLoss = 0, 0
        
        nodes, self.weights, self.biases = self.optimser(inputData, labels, useBatches, self.weights, self.biases, batchSize, alpha, beta1, beta2, epsilon)        
        
        lastLayer = len(nodes[0]) - 1
        for i in range(len(nodes)): 
            totalLoss += self.NeuralNetworkClass.lossFunction(nodes[i][lastLayer], labels[i])
            nodeIndex = np.argmax(nodes[i][lastLayer])
            labelIndex = np.argmax(labels[i])
            if(nodeIndex == labelIndex):
                correct += 1
        return 100 * (correct / len(labels)), totalLoss / len(labels)
    
    def createWeightsBiases(self):
        for i in range(len(self.layers)):
            if(type(self.layers[i]) == ConvLayer):
                kernalSize = self.layers[i].kernalSize
                numKernals = self.layers[i].numKernals
                depth = self.layers[i].depth

                bounds =  np.sqrt(2 / kernalSize) # He initialisation

                self.weights.append(np.random.normal(0, bounds, size=(numKernals, depth, kernalSize, kernalSize)))
                self.biases.append(np.zeros((numKernals)))

                self.layers[i].kernalWeights = self.weights[-1]
                self.layers[i].kernalBiases = self.biases[-1]
            elif(type(self.layers[i]) == DenseLayer):
                self.weights.append(self.layers[i].NeuralNetworkClass.weights)
                self.biases.append(self.layers[i].NeuralNetworkClass.biases)

    def saveModel(self, NNweights, NNbiases, CNNweights, CNNbiases, filename = "modelWeights.npz"):
        CNNweights = np.array(CNNweights, dtype=object)
        CNNbiases = np.array(CNNbiases, dtype=object)
        NNweights = np.array(NNweights, dtype=object)
        NNbiases = np.array(NNbiases, dtype=object)
        np.savez_compressed(filename, CNNweights = CNNweights, CNNbiases = CNNbiases, NNweights = NNweights, NNbiases = NNbiases, allow_pickle = True)

    def loadModel(self, neuralNetwork, filename = "modelWeights.npz"):
        data = np.load(filename, allow_pickle = True)
        CNNweights = data["CNNweights"]
        CNNbiases = data["CNNbiases"]
        NNweights = data["NNweights"]
        NNbiases = data["NNbiases"]

        self.layers[-1].NeuralNetworkClass.weights = NNweights
        self.layers[-1].NeuralNetworkClass.biases = NNbiases
        neuralNetwork.weights = NNweights
        neuralNetwork.biases = NNbiases
        self.weights = CNNweights
        self.biases = CNNbiases

        currWeightIndex = 0
        for i in range(len(self.layers)):
            if(type(self.layers[i]) == ConvLayer):
                self.layers[i].kernalWeights = CNNweights[currWeightIndex]
                self.layers[i].kernalBiases = CNNbiases[currWeightIndex]
                currWeightIndex += 1

class ConvLayer(ConvulationalNetwork, CNNbackpropagation):
    def __init__(self, kernalSize, depth, numKernals, stride, padding = "no"):
        self.kernalSize = kernalSize
        self.numKernals = numKernals
        self.kernalWeights = []
        self.kernalBiases = []
        self.depth = depth
        self.stride = stride
        self.padding = padding
        if(padding.lower() == "no" or padding.lower() == "n"):
            self.usePadding = False
        else:
            self.padding = int(self.padding)
            self.usePadding = True
    
    def forward(self, inputTensor):
        return ConvulationalNetwork.kernalisation(self, inputTensor, self.kernalWeights, self.kernalBiases, self.kernalSize, self.usePadding, self.padding, self.stride)

    def backpropagation(self, errorPatch, inputTensor):
        return CNNbackpropagation.ConvolutionDerivative(self, errorPatch, self.kernalWeights, inputTensor, self.stride)

class PoolingLayer(CNNbackpropagation):
    def __init__(self, gridSize, stride, mode = "max"):
        self.gridSize = gridSize
        self.stride = stride
        self.mode = mode.lower()
    
    def forward(self, inputTensor):
        if(self.mode == "gap" or self.mode == "global"):
            return ConvulationalNetwork.poolingGlobalAverage(self, inputTensor)
        return ConvulationalNetwork.pooling(self, inputTensor, self.gridSize, self.stride, self.mode)

    def backpropagation(self, errorPatch, inputTensor):
        if(self.mode == "max"):
            return CNNbackpropagation.MaxPoolingDerivative(self, errorPatch, inputTensor, self.gridSize, self.stride)
        elif(self.mode == "ave"):
            return CNNbackpropagation.AveragePoolingDerivative(self, errorPatch, inputTensor, self.gridSize, self.stride)
        else:
            return CNNbackpropagation.GlobalAveragePoolingDerivative(self, inputTensor)

class DenseLayer: # basically a fancy neural network
    def __init__(self, NeuralNetworkClass):
        self.NeuralNetworkClass = NeuralNetworkClass
        self.orignalShape = 0
        
    def forward(self, inputTensor):
        self.orignalShape = np.array(inputTensor).shape
        inputArray = ConvulationalNetwork.flatternTensor(self, inputTensor)
        self.layerNodes = self.NeuralNetworkClass.forwardPropagation(inputArray)
        return self.layerNodes[-1]
    
    def backpropagation(self, trueValues): #return weigtGradients, biasGradients, errorTerms
        weightGradients, biasGradients, errorTerms = self.NeuralNetworkClass.backPropgation(
            self.layerNodes, 
            self.NeuralNetworkClass.weights,
            self.NeuralNetworkClass.biases,
            trueValues,
            True
        )
        #errorTerms = np.array(self.NeuralNetworkClass.weights).T @ errorTerms 
        #errorTerms = errorTerms.reshape(self.orignalShape)

        for i in reversed(range(len(self.NeuralNetworkClass.weights))):
            errorTerms = self.NeuralNetworkClass.weights[i] @ errorTerms
        errorTerms = errorTerms.reshape(self.orignalShape)

        return weightGradients, biasGradients, errorTerms

class ActivationLayer: # basically aplies an activation function over the whole Tensor (eg. leaky relu)
    def forward(self, inputTensor):
        return ConvulationalNetwork.activation(self, inputTensor)

    def backpropagation(self, errorPatch, inputTensor):
        return CNNbackpropagation.ActivationLayerDerivative(self, errorPatch, ReLUDerivative, inputTensor)
    