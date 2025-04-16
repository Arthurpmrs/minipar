# Código Simples de um Neuronio

input_val = 1
output_desire = 0

input_weight = 0.5
learning_rate = 0.01

# Função de Ativação
def activation(sum):
    if sum >= 0:
        return 1
    else:
        return 0

print("Entrada: ", input_val, " Desejado: ", output_desire)

# Inicializar erro
error = 1000.0
iteration = 0
bias = 1
bias_weight = 0.5

while error != 0:
    iteration += 1
    print("#### Iteração: ", iteration)
    print("Peso: ", input_weight)
    
    sum_val = (input_val * input_weight) + (bias * bias_weight)

    output = activation(sum_val)
    print("Saída: ", output)

    error = output_desire - output
    print("Erro: ", error)

    if error != 0:
        input_weight = input_weight + (learning_rate * input_val * error)
        print("Peso do bias: ", bias_weight)
        bias_weight = bias_weight + (learning_rate * bias * error)

print("Parabéns!!! A Rede de um Neurônio Aprendeu")
print ("Valor desejadao: ", output_desire)