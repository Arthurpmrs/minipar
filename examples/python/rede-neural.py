#Este código cria uma rede neural com uma camada oculta de três neurônios
#e uma camada de saída com um neurônio, utilizando a função de ativação sigmóide.
#Ele treina a rede para aprender a função XOR usando feedforward e backpropagation.
#Todos os cálculos são realizados manualmente, sem o uso de bibliotecas externas.

import random
import math

# Função de ativação sigmóide
def sigmoid(x):
    return 1 / (1 + math.exp(-x))

# Derivada da função de ativação sigmóide
def sigmoid_derivative(x):
    return x * (1 - x)

# Dados de entrada (função XOR)
inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
# Saídas desejadas (função XOR)
outputs = [0, 1, 1, 0]

# Inicialização dos pesos com valores aleatórios
weights_input_hidden = [[random.random() for _ in range(3)] for _ in range(2)]
weights_hidden_output = [random.random() for _ in range(3)]
bias_hidden = [random.random() for _ in range(3)]
bias_output = random.random()

# Taxa de aprendizado
learning_rate = 0.2

# Número de iterações
for epoch in range(20000):
    for i in range(len(inputs)):
        # Fase de feedforward
        hidden_layer_input = [inputs[i][j] * weights_input_hidden[j][k] for k in range(3) for j in range(2)]
        hidden_layer_output = [sigmoid(sum(hidden_layer_input[i*2:(i+1)*2]) + bias_hidden[i]) for i in range(3)]
        output_layer_input = sum([hidden_layer_output[j] * weights_hidden_output[j] for j in range(3)]) + bias_output
        predicted_output = sigmoid(output_layer_input)
        
        # Cálculo do erro
        error = outputs[i] - predicted_output
        
        # Fase de backpropagation
        d_predicted_output = error * sigmoid_derivative(predicted_output)
        d_hidden_layer = [d_predicted_output * weights_hidden_output[j] * sigmoid_derivative(hidden_layer_output[j]) for j in range(3)]
        
        # Atualização dos pesos e bias
        weights_hidden_output = [weights_hidden_output[j] + hidden_layer_output[j] * d_predicted_output * learning_rate for j in range(3)]
        bias_output += d_predicted_output * learning_rate
        for j in range(2):
            for k in range(3):
                weights_input_hidden[j][k] += inputs[i][j] * d_hidden_layer[k] * learning_rate
                bias_hidden[k] += d_hidden_layer[k] * learning_rate

# Testando a rede neural treinada
for i in range(len(inputs)):
    hidden_layer_input = [inputs[i][j] * weights_input_hidden[j][k] for k in range(3) for j in range(2)]
    hidden_layer_output = [sigmoid(sum(hidden_layer_input[i*2:(i+1)*2]) + bias_hidden[i]) for i in range(3)]
    output_layer_input = sum([hidden_layer_output[j] * weights_hidden_output[j] for j in range(3)]) + bias_output
    predicted_output = sigmoid(output_layer_input)
    print(f"Input: {inputs[i]}, Predicted Output: {predicted_output}")