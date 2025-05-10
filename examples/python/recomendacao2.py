import math

# Histórico de compras do usuário
user_purchase_history = ['Smartphone', 'Jeans', 'Micro-ondas', 'Ficção']

# Categorias de produtos e seus itens
product_categories = {
    'Eletrônicos': ['Smartphone', 'Laptop', 'Tablet', 'Fones de ouvido'],
    'Roupas': ['Camisa', 'Jeans', 'Jaqueta', 'Sapatos'],
    'Eletrodomésticos': [
        'Geladeira',
        'Micro-ondas',
        'Máquina de lavar',
        'Ar condicionado',
    ],
    'Livros': ['Ficção', 'Não-ficção', 'Ficção científica', 'Fantasia'],
}


# Função para codificar o histórico de compras do usuário
def encode_purchase_history(user_purchase_history, product_categories):
    all_products = [
        product
        for products in product_categories.values()
        for product in products
    ]
    encoded_history = [0] * len(all_products)
    for product in user_purchase_history:
        if product in all_products:
            encoded_history[all_products.index(product)] = 1
    return encoded_history


# Função para criar a rede neural
def create_neural_network(input_size, hidden_size, output_size):
    W1 = [[0.5 for _ in range(hidden_size)] for _ in range(input_size)]
    b1 = [0.5] * hidden_size
    W2 = [[0.5 for _ in range(output_size)] for _ in range(hidden_size)]
    b2 = [0.5] * output_size
    return W1, b1, W2, b2


# Função para ativação ReLU
def relu(x):
    return [max(0, i) for i in x]


# Função para ativação Sigmoid
def sigmoid(x):
    return [1 / (1 + math.exp(-i)) for i in x]


# Função para a propagação da rede neural
def forward_propagation(X, W1, b1, W2, b2):
    Z1 = [
        sum(X[j] * W1[j][i] for j in range(len(X))) + b1[i]
        for i in range(len(b1))
    ]
    A1 = relu(Z1)
    Z2 = [
        sum(A1[j] * W2[j][i] for j in range(len(A1))) + b2[i]
        for i in range(len(b2))
    ]
    A2 = sigmoid(Z2)
    return A2


# Função para recomendar produtos
def recommend_products(user_purchase_history, product_categories):
    encoded_history = encode_purchase_history(
        user_purchase_history, product_categories
    )

    input_size = len(encoded_history)
    hidden_size = 10  # Tamanho da camada oculta
    output_size = len(encoded_history)

    W1, b1, W2, b2 = create_neural_network(
        input_size, hidden_size, output_size
    )

    recommendations_encoded = forward_propagation(
        encoded_history, W1, b1, W2, b2
    )

    all_products = [
        product
        for products in product_categories.values()
        for product in products
    ]

    recommendations = [
        all_products[i]
        for i in range(len(all_products))
        if recommendations_encoded[i] > 0.5
        and all_products[i] not in user_purchase_history
    ]

    return recommendations


# Obter recomendações de produtos
recommendations = recommend_products(user_purchase_history, product_categories)

# Imprimir as recomendações
print('Produtos recomendados para você:')
for product in recommendations:
    print(product)
