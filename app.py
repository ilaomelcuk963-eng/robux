from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Файл для хранения данных
DATA_FILE = 'data.json'

def load_data():
    """Загрузка данных из JSON файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Возвращаем структуру по умолчанию
        return {
            "visitors": [],
            "orders": [],
            "reviews": [
                {
                    "id": 1,
                    "name": "Алексей",
                    "rating": 5,
                    "text": "Отличный сервис! Robux пришли быстро, без проблем.",
                    "timestamp": "2024-01-15 14:30:00"
                }
            ],
            "promotions": [
                {
                    "id": 1,
                    "robux": 1000,
                    "price": 299,
                    "quantity": 50
                }
            ],
            "next_review_id": 2,
            "next_order_id": 1,
            "next_promotion_id": 2,
            "stats": {
                "total_sold": 15847,
                "happy_clients": 2394
            }
        }

def save_data(data):
    """Сохранение данных в JSON файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Получение всех отзывов"""
    data = load_data()
    return jsonify(data['reviews'])

@app.route('/api/reviews', methods=['POST'])
def add_review():
    """Добавление нового отзыва"""
    data = load_data()
    
    review_data = request.json
    new_review = {
        "id": data['next_review_id'],
        "name": review_data.get('name'),
        "rating": review_data.get('rating'),
        "text": review_data.get('text'),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data['reviews'].append(new_review)
    data['next_review_id'] += 1
    save_data(data)
    
    return jsonify({"success": True, "review": new_review})

@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """Удаление отзыва"""
    data = load_data()
    data['reviews'] = [r for r in data['reviews'] if r['id'] != review_id]
    save_data(data)
    
    return jsonify({"success": True})

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Получение всех заказов"""
    data = load_data()
    return jsonify(data['orders'])

@app.route('/api/orders', methods=['POST'])
def add_order():
    """Добавление нового заказа"""
    data = load_data()
    
    order_data = request.json
    new_order = {
        "id": data['next_order_id'],
        "robux": order_data.get('robux'),
        "cost": order_data.get('cost'),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Обрабатывается",
        "payment_method": order_data.get('payment_method', 'Карта')
    }
    
    data['orders'].append(new_order)
    data['next_order_id'] += 1
    
    # Обновляем статистику
    if 'stats' not in data:
        data['stats'] = {}
    data['stats']['total_sold'] = data['stats'].get('total_sold', 0) + new_order['robux']
    data['stats']['happy_clients'] = data['stats'].get('happy_clients', 0) + 1
    
    save_data(data)
    
    return jsonify({"success": True, "order": new_order})

@app.route('/api/promotions', methods=['GET'])
def get_promotions():
    """Получение всех акций"""
    data = load_data()
    return jsonify(data['promotions'])

@app.route('/api/promotions', methods=['POST'])
def add_promotion():
    """Добавление новой акции"""
    data = load_data()
    
    promotion_data = request.json
    new_promotion = {
        "id": data['next_promotion_id'],
        "robux": promotion_data.get('robux'),
        "price": promotion_data.get('price'),
        "quantity": promotion_data.get('quantity')
    }
    
    data['promotions'].append(new_promotion)
    data['next_promotion_id'] += 1
    save_data(data)
    
    return jsonify({"success": True, "promotion": new_promotion})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Получение статистики"""
    data = load_data()
    return jsonify(data.get('stats', {}))

@app.route('/api/data', methods=['GET'])
def get_all_data():
    """Получение всех данных"""
    data = load_data()
    return jsonify(data)

if __name__ == '__main__':
    # Создаем файл данных если его нет
    if not os.path.exists(DATA_FILE):
        initial_data = load_data()
        save_data(initial_data)
        print("Файл data.json создан с начальными данными")
    
    print("Запуск сервера...")
    print("Откройте в браузере: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)