from customer import CustomerClient

client = CustomerClient()

def test_all_methods():
    # Тест создания клиента
    new_customer = client.create("Иван Иванов", "ivan@example.com")
    print("Создан клиент:", new_customer)

    # Тест получения клиента
    customer = client.get(new_customer["id"])
    print("Получен клиент:", customer)

    # Тест обновления клиента
    updated_customer = client.update(new_customer["id"], "Иван Петров", "ivan_petrov@example.com")
    print("Обновлённый клиент:", updated_customer)

    # Тест списка клиентов
    customers = client.list_customers(page=1, limit=10)
    print(f"Список клиентов (всего {customers['total']}):")
    for c in customers["customers"]:
        print(f"  - {c['name']} ({c['email']})")

    # Тест удаления клиента
    delete_result = client.delete(new_customer["id"])
    print("Результат удаления:", delete_result)

if __name__ == "__main__":
    test_all_methods()