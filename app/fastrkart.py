KART_CHECKOUT_TAX = 10

class Fastrkart:
    def __init__(self, kart=None):
        self.kart = kart if kart else {
                "products": {},
                "tax": 0,
                "sub_total": 0,
                "total": 0
            }
        
    @staticmethod
    def fastkart_sub_total(products):
        sub_total = 0
        if products:
            for product_id, product in products.items():
                product_price = product["rate"] * product["quantity"]
                sub_total += product_price
            return sub_total
        return sub_total
        
    def add_product(self, product, quantity=1):
        product_id = str(product["id"])
        quantity = int(quantity)
        if product_id not in self.kart["products"]:
            self.kart["products"][product_id] = product
            self.kart["products"][product_id]["quantity"] = 0
        self.kart["products"][product_id]["quantity"] += quantity
        # process billing
        self.kart["sub_total"] = Fastrkart.fastkart_sub_total(self.kart["products"])
        self.kart["tax"] = self.kart["sub_total"] * round((KART_CHECKOUT_TAX/100),2)
        self.kart["total"] = self.kart["sub_total"] + self.kart["tax"]

    def remove_product(self, product, quantity=1):
        product_id = str(product["id"])
        quantity = int(quantity)
        if product_id in self.kart["products"]:
            if self.kart["products"][product_id]["quantity"] <= quantity:
                del self.kart["products"][product_id]
                # process billing
                self.kart["sub_total"] = Fastrkart.fastkart_sub_total(self.kart["products"])
                self.kart["tax"] = self.kart["sub_total"] * round((KART_CHECKOUT_TAX/100),2)
                self.kart["total"] = self.kart["sub_total"] + self.kart["tax"]

            # if self.kart["products"][product_id]["quantity"] > quantity:
            else:
                self.kart["products"][product_id]["quantity"] -= quantity
                # process billing
                self.kart["sub_total"] = Fastrkart.fastkart_sub_total(self.kart["products"])
                self.kart["tax"] = self.kart["sub_total"] * round((KART_CHECKOUT_TAX/100),2)
                self.kart["total"] = self.kart["sub_total"] + self.kart["tax"]

    def clear_kart(self):
        self.kart = {
                "products": {},
                "tax": 0,
                "sub_total": 0,
                "total": 0
            }
        print(self)
        print('cleared')

# SAMPLE SCHEMA
# kart = {
# 	"kart": {
# 		"products": {
# 			"1": {
# 				"id": 1,
# 				"tag_id": "A7 E4 H5 3Q",
# 				"title": "Sweatshirt",
# 				"rate": 250,
#                 "quantity": 3
# 			},
# 			"2": {
# 				"id": 2,
# 				"tag_id": "A7 E4 H5 3Q",
# 				"title": "Sweatshirt",
# 				"rate": 250,
#                 "quantity": 2
# 			}
# 		},
# 		"tax": 50,
# 		"sub_total": 500,
# 		"total": 550
# 	}
# }