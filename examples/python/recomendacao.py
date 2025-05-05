import math


def read_data():
    # Função para ler os dados de avaliação dos usuários para produtos
    # Os dados são representados como um dicionário de dicionários
    user_ratings = {
        'user1': {'product1': 5, 'product2': 3, 'product3': 4},
        'user2': {'product1': 4, 'product2': 2, 'product3': 5},
        'user3': {'product2': 5, 'product3': 3},
        'user4': {'product1': 3, 'product3': 4},
    }
    return user_ratings


def calculate_similarity(user1_ratings, user2_ratings):
    # Calcula a similaridade entre dois usuários usando similaridade de cosseno
    common_products = set(user1_ratings.keys()) & set(user2_ratings.keys())
    if not common_products:
        return 0

    sum1_sq = sum(user1_ratings[product] ** 2 for product in common_products)
    sum2_sq = sum(user2_ratings[product] ** 2 for product in common_products)

    product_sum = sum(
        user1_ratings[product] * user2_ratings[product]
        for product in common_products
    )

    numerator = product_sum
    denominator = math.sqrt(sum1_sq) * math.sqrt(sum2_sq)
    if denominator == 0:
        return 0
    return numerator / denominator


def get_recommendations(user_ratings, target_user):
    # Obtém recomendações de produtos para o usuário-alvo
    totals = {}
    sim_sums = {}

    for other_user in user_ratings:
        if other_user == target_user:
            continue
        similarity = calculate_similarity(
            user_ratings[target_user], user_ratings[other_user]
        )
        if similarity <= 0:
            continue

        # Debug: Print user similarities
        print(f'Similaridade entre {target_user} e {other_user}: {similarity}')

        for product, rating in user_ratings[other_user].items():
            if product not in user_ratings[target_user]:
                if product not in totals:
                    totals[product] = 0
                totals[product] += rating * similarity
                if product not in sim_sums:
                    sim_sums[product] = 0
                sim_sums[product] += similarity

    rankings = [
        (total / sim_sums[product], product)
        for product, total in totals.items()
        if sim_sums[product] != 0
    ]
    rankings.sort(reverse=True)
    recommendations = [product for score, product in rankings]
    return recommendations


def main():
    user_ratings = read_data()
    while True:
        print('\nBem-vindo ao Sistema de Recomendação de E-commerce')
        print('Usuários disponíveis:', list(user_ratings.keys()))
        target_user = input(
            "Digite o usuário para o qual deseja recomendações (ou 'sair' para finalizar): "
        ).strip()
        if target_user.lower() == 'sair':
            print('Saindo do sistema de recomendação.')
            break
        if target_user not in user_ratings:
            print('Usuário não encontrado. Tente novamente.')
            continue
        recommendations = get_recommendations(user_ratings, target_user)
        if recommendations:
            print(f'Recomendações para {target_user}: {recommendations}')
        else:
            print(f'Nenhuma recomendação disponível para {target_user}.')


if __name__ == '__main__':
    main()

# python recommendation_system.py

# Bem-vindo ao Sistema de Recomendação de E-commerce
# Usuários disponíveis: ['user1', 'user2', 'user3', 'user4']
# Digite o usuário para o qual deseja recomendações (ou 'sair' #para finalizar): user1
# Similaridade entre user1 e user2: 0.9759000729485332
# Similaridade entre user1 e user3: 0.31622776601683794
# Similaridade entre user1 e user4: 0.9922778767136677
# Recomendações para user1: ['product2']
# Digite o usuário para o qual deseja recomendações (ou 'sair' #para finalizar): user2
# Similaridade entre user2 e user1: 0.9759000729485332
# Similaridade entre user2 e user3: 0.5976143046671968
# Similaridade entre user2 e user4: 0.8944271909999159
# Recomendações para user2: []
# Digite o usuário para o qual deseja recomendações (ou 'sair' #para finalizar): user3
# Similaridade entre user3 e user1: 0.31622776601683794
# Similaridade entre user3 e user2: 0.9999999999999999
# Similaridade entre user3 e user4: 0.7071067811865475
# Recomendações para user3: ['product1']
# Digite o usuário para o qual deseja recomendações (ou 'sair' #para finalizar): user4
# Similaridade entre user4 e user1: 0.9922778767136677
# Similaridade entre user4 e user2: 0.8944271909999159
# Similaridade entre user4 e user3: 0.7071067811865475
# Recomendações para user4: ['product2']
# Digite o usuário para o qual deseja recomendações (ou 'sair' #para finalizar): sair
# Saindo do sistema de recomendação.
