# controllers/customer_controller.py
from models.customer_model import CustomerModel

class CustomerController:
    def __init__(self):
        self.model = CustomerModel()

    def get_customers(self, search_term=None):
        return self.model.get_customers(search_term)

    def add_customer(self, nama, alamat, telepon):
        return self.model.add_customer(nama, alamat, telepon)

    def update_customer(self, customer_id, nama, alamat, telepon):
        return self.model.update_customer(customer_id, nama, alamat, telepon)

    def delete_customer(self, customer_id):
        return self.model.delete_customer(customer_id)

    def get_customer_by_id(self, customer_id):
        return self.model.get_customer_by_id(customer_id)
    
    def get_customer_by_id(self, customer_id):
        return self.model.get_customer_by_id(customer_id)
        
    def load_all_customers(self):
        return self.model.load_all_customers()
