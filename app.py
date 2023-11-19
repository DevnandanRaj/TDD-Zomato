import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Define file paths for data persistence
menu_file = "menu_data.json"
orders_file = "orders_data.json"

# Initialize data dictionaries
menu = {}
orders = []

# Load menu and orders data from JSON files


def load_data():
    global menu, orders
    try:
        with open(menu_file, "r") as menu_data:
            loaded_menu = json.load(menu_data)
            # Convert keys from strings to integers
            menu = {int(key): value for key, value in loaded_menu.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        menu = {}

    try:
        with open(orders_file, "r") as orders_data:
            orders = json.load(orders_data)
    except (FileNotFoundError, json.JSONDecodeError):
        orders = []

# Save menu and orders data to JSON files


def save_data():
    with open(menu_file, "w") as menu_data, open(orders_file, "w") as orders_data:
        json.dump(menu, menu_data, indent=4)
        json.dump(orders, orders_data, indent=4)


# Initialize data
load_data()

# Function to add a new dish to the menu


@app.route('/menu/add', methods=['POST'])
def add_dish():
    data = request.json
    dish_id = len(menu)+1

    if dish_id in menu:
        return jsonify({"message": f"Dish with ID {dish_id} already exists."}), 400

    name = data.get('name')
    price = data.get('price')
    availability = data.get('availability', "yes")

    menu[dish_id] = {"name": name, "price": price,
                     "availability": availability}
    save_data()
    return jsonify({"message": f"Dish with ID {dish_id} has been added to the menu."}), 201

# Function to remove a dish from the menu


@app.route('/menu/remove/<int:dish_id>', methods=['DELETE'])
def remove_dish(dish_id):
    if dish_id in menu:
        del menu[dish_id]
        save_data()
        return jsonify({"message": f"Dish with ID {dish_id} has been removed from the menu."}), 200
    else:
        return jsonify({"message": f"Dish with ID {dish_id} not found in the menu."}), 404

# Function to update dish availability


@app.route('/menu/update-availability/<int:dish_id>', methods=['PUT'])
def update_availability(dish_id):
    if dish_id in menu:
        data = request.json
        availability = data.get('availability')
        menu[dish_id]["availability"] = availability
        save_data()
        return jsonify({"message": f"Availability of dish with ID {dish_id} has been updated."}), 200
    else:
        return jsonify({"message": f"Dish with ID {dish_id} not found in the menu."}), 404


# Function to take a new customer order
@app.route('/order', methods=['POST'])
def take_order():
    data = request.json
    customer_name = data.get("customer_name")
    order_items = data.get("items", [])

    valid_order_items = []

    total_amount = 0.0  # Initialize total amount

    for item_id in order_items:
        # Ensure that the item_id is an integer and exists in the menu
        if isinstance(item_id, int) and item_id in menu and menu[item_id]["availability"]:
            dish = menu[item_id]
            valid_order_items.append({
                "dish_id": item_id,
                "name": dish["name"],
                "price": dish["price"]
            })
            total_amount += dish["price"]

    if valid_order_items:
        order_id = len(orders) + 1
        order = {
            "order_id": order_id,
            "customer_name": customer_name,
            "items": valid_order_items,
            "status": "received",
            "total_amount": total_amount
        }
        orders.append(order)
        save_data()
        return jsonify({"message": f"Order with ID {order_id} has been received. Total amount: ${total_amount:.2f}"}), 201
    else:
        return jsonify({"message": "Invalid order items or item availability."}), 400


# Function to update order status


@app.route('/order/update-status/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    data = request.json
    new_status = data.get('status')

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = new_status
            save_data()
            return jsonify({"message": f"Status of order with ID {order_id} has been updated."}), 200

    return jsonify({"message": f"Order with ID {order_id} not found."}), 404

# Function to review orders


@app.route('/orders', methods=['GET'])
def review_orders():
    review_options = request.args.get('status', 'all')

    review_filters = {
        'all': lambda order: True,
        'preparing': lambda order: order["status"] == "preparing",
        'ready': lambda order: order["status"] == "ready",
        'delivered': lambda order: order["status"] == "delivered"
    }

    selected_orders = [
        order for order in orders if review_filters[review_options](order)
    ]

    reviewed_orders = []

    for order in selected_orders:
        reviewed_order = {
            "order_id": order["order_id"],
            "customer_name": order["customer_name"],
            "status": order["status"],
            "items": []
        }

        for item_id in order["items"]:
            if isinstance(item_id, int) and item_id in menu:
                dish = menu.get(item_id)
                if isinstance(dish, dict) and dish is not None:
                    reviewed_order["items"].append({
                        "dish_id": item_id,
                        "dish_name": dish.get("name", "N/A"),
                        "price": dish.get("price", 0.0)
                    })

        reviewed_orders.append(reviewed_order)

    return jsonify(reviewed_orders)

# Function to retrieve the menu


@app.route('/menu', methods=['GET'])
def get_menu():
    return jsonify(menu)


if __name__ == '__main__':
    app.run(debug=True)
