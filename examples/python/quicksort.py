# Função para implementar o Quicksort
def quicksort(array):
    if len(array) <= 1:  # Caso base: vetor com 0 ou 1 elementos já está ordenado
        return array
    else:
        pivot = array[0]  # Escolhe o primeiro elemento como pivô
        menores = [x for x in array[1:] if x <= pivot]  # Elementos menores ou iguais ao pivô
        maiores = [x for x in array[1:] if x > pivot]   # Elementos maiores que o pivô
        return quicksort(menores) + [pivot] + quicksort(maiores)

# Função para exibir interface simples de texto
def exibir_interface():
    print("==== Ordenação com Quicksort ====")
    print("Insira os elementos do vetor separados por espaço:")
    
    try:
        # Leitura do vetor
        array = list(map(int, input().strip().split()))
        print(f"Vetor original: {array}")
        
        # Aplicar o Quicksort
        vetor_ordenado = quicksort(array)
        print(f"Vetor ordenado: {vetor_ordenado}")
    except ValueError:
        print("Por favor, insira apenas números separados por espaço.")
        exibir_interface()  # Reinicia a interface em caso de erro

# Executa o programa
if __name__ == "__main__":
    exibir_interface()