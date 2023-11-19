import unittest
import json
from app import app, menu, orders, save_data

class FlaskAppTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_add_dish(self):
        data = {
            "name": "Test Dish",
            "price": 10.99,
            "availability": "yes"
        }
        response = self.app.post('/menu/add', json=data)
        self.assertEqual(response.status_code, 201)

    def test_remove_dish(self):
        # Add a dish for testing
        self.app.post('/menu/add', json={"name": "Test Dish", "price": 10.99, "availability": "yes"})
        
        # Get the current length of menu
        initial_menu_length = len(menu)
        
        # Try to remove the dish
        response = self.app.delete('/menu/remove/1')
        
        # Check if the dish was successfully removed
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(menu), initial_menu_length - 1)

    def test_update_availability(self):
        # Add a dish for testing
        self.app.post('/menu/add', json={"name": "Test Dish", "price": 10.99, "availability": "yes"})

        # Try to update availability
        data = {
            "availability": "no"
        }
        response = self.app.put('/menu/update-availability/2', json=data)
        self.assertEqual(response.status_code, 200)

    def test_take_order(self):
        # Add dishes for testing
        self.app.post('/menu/add', json={"name": "Dish1", "price": 10.99, "availability": "yes"})
        self.app.post('/menu/add', json={"name": "Dish2", "price": 15.99, "availability": "yes"})

        # Try to take an order
        data = {
            "customer_name": "Test Customer",
            "items": [1, 2]
        }
        response = self.app.post('/order', json=data)
        self.assertEqual(response.status_code, 201)

    def test_update_order_status(self):
        # Add an order for testing
        self.app.post('/order', json={"customer_name": "Test Customer", "items": [1, 2]})

        # Try to update order status
        data = {
            "status": "preparing"
        }
        response = self.app.put('/order/update-status/1', json=data)
        self.assertEqual(response.status_code, 200)

    def test_review_orders(self):
        # Add orders for testing
        self.app.post('/order', json={"customer_name": "Customer1", "items": [1]})
        self.app.post('/order', json={"customer_name": "Customer2", "items": [2]})
        self.app.post('/order', json={"customer_name": "Customer3", "items": [3]})
        
        # Try to review orders
        response = self.app.get('/orders?status=all')
        self.assertEqual(response.status_code, 200)

        # Check content
        orders_data = json.loads(response.get_data(as_text=True))
        self.assertIsInstance(orders_data, list)
        self.assertTrue(len(orders_data) > 0)

    def test_get_menu(self):
        # Try to get the menu
        response = self.app.get('/menu')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')


if __name__ == '__main__':
    unittest.main()
