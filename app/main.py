import tkinter as tk
# import tkmacosx as tkmac
from PIL import Image, ImageTk
import os
import serial.tools.list_ports
import platform
import csv
import datetime
import requests


class FastrkartAPI:
    @staticmethod
    def get_product_by_tag_id(tag_id):
        # Make an API request to get the product details based on the tag_id
        url = f"http://localhost:8000/product/products?tag_id={tag_id}"
        response = requests.get(url)

        if response.status_code == 200:
            product = response.json()
            return product

        return None

class FastrkartGUI:
    def __init__(self, root):
        self.api = FastrkartAPI()
        self.root = root
        self.kart = {
            "products": {},
            "tax": 0,
            "sub_total": 0,
            "total": 0
        }

        self.serial_port = self.get_serial_port()
        if self.serial_port is not None:
            self.arduino = serial.Serial(self.serial_port, 9600, timeout=1)  # Adjust the baud rate as per your Arduino setup

        self.create_widgets()
        self.read_rfid()

    def create_widgets(self):
        # Create and configure GUI elements (labels, buttons, entry fields, etc.)
        self.header_frame = tk.Frame(self.root, bg="black")
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.header_label = tk.Label(self.header_frame, text="Welcome!", font=("Arial", 36), fg="white", bg="black")
        self.header_label.pack(pady=20)

        self.product_frame = tk.Frame(self.root)
        self.product_frame.pack()

        self.footer_frame = tk.Frame(self.root, bg="black", pady=20)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.sub_total_label = tk.Label(self.footer_frame, text="Sub Total: ₹0", fg="white", bg="black", font=("Arial", 18))
        self.sub_total_label.pack(side=tk.LEFT, padx=10)

        self.tax_label = tk.Label(self.footer_frame, text="Tax: ₹0", fg="white", bg="black", font=("Arial", 18))
        self.tax_label.pack(side=tk.LEFT, padx=10)

        self.total_label = tk.Label(self.footer_frame, text="Total: ₹0", fg="white", bg="black", font=("Arial", 18))
        self.total_label.pack(side=tk.LEFT, padx=10)

        self.pay_now_button = tk.Button(self.footer_frame, text="Pay Now", bg="#4CBB17", highlightbackground='#4CBB17', command=self.pay_now, fg="white", font=("Arial", 18))
        self.pay_now_button.pack(side=tk.RIGHT, padx=10)

        self.display_products()

    def get_serial_port(self):
        # Get the serial port for Arduino communication
        if 'mac' in platform.platform():
            PORT_SEARCH_STRING = 'usbmodem'
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if PORT_SEARCH_STRING in port.device:  # Adjust the device name as per your Arduino setup
                return port.device
        return None

    def add_product(self):
        if self.serial_port is not None:
            # Retrieve the tag_id from the Arduino
            tag_id = self.arduino.readline().decode().strip()

            # Get the product details from the API based on the tag_id
            product = self.api.get_product_by_tag_id(tag_id)

            if product:
                print(product)
                self.update_kart(product)
                self.update_total_label()
                self.display_products()

    def update_kart(self, product):
        # Update the kart with the added product
        product_id = product["id"]

        if product_id not in self.kart["products"]:
            self.kart["products"][product_id] = product
            self.kart["products"][product_id]["quantity"] = 0

        self.kart["products"][product_id]["quantity"] += 1
        self.kart["sub_total"] = self.fastkart_sub_total(self.kart["products"])
        self.kart["tax"] = self.kart["sub_total"] * 0.18
        self.kart["total"] = self.kart["sub_total"] + self.kart["tax"]

    @staticmethod
    def fastkart_sub_total(products):
        sub_total = 0
        for product in products.values():
            sub_total += product["rate"] * product["quantity"]
        return sub_total

    def update_total_label(self):
        # Update the total label with the current total value
        self.sub_total_label["text"] = f"Sub Total: ₹{self.kart['sub_total']:.2f}"
        self.tax_label["text"] = f"Tax: ₹{self.kart['tax']:.2f}"
        self.total_label["text"] = f"Total: ₹{self.kart['total']:.2f}"

    def display_products(self):
        # Display the products in the kart with their quantities
        for widget in self.product_frame.winfo_children():
            widget.destroy()

        for product in self.kart["products"].values():
            product_frame = tk.Frame(self.product_frame)
            product_frame.pack()

            image_path = os.path.join("images", product["image"])
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((80, 80), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(image)
                image_label = tk.Label(product_frame, image=photo)
                image_label.image = photo
                image_label.pack(side=tk.LEFT)

            title_label = tk.Label(product_frame, text=f"Title: {product['title']}", font=("Arial", 18))
            title_label.pack(side=tk.LEFT)

            rate_label = tk.Label(product_frame, text=f"Rate: ₹{product['rate']}", font=("Arial", 18))
            rate_label.pack(side=tk.LEFT)

            tag_id_label = tk.Label(product_frame, text=f"Tag ID: {product['tag_id']}", font=("Arial", 18))
            tag_id_label.pack(side=tk.LEFT)

            size_label = tk.Label(product_frame, text=f"Size: {product['size']}", font=("Arial", 18))
            size_label.pack(side=tk.LEFT)

            quantity_label = tk.Label(product_frame, text="Quantity: ", font=("Arial", 18))
            quantity_label.pack(side=tk.LEFT)

            quantity_frame = tk.Frame(product_frame)
            quantity_frame.pack(side=tk.LEFT)

            quantity_decrease_button = tk.Button(quantity_frame, text="-",
                                                command=lambda id=product["id"]: self.decrease_quantity(id),
                                                font=("Arial", 18))
            quantity_decrease_button.pack(side=tk.LEFT)

            quantity_value = tk.Label(quantity_frame, text=str(product["quantity"]), font=("Arial", 18))
            quantity_value.pack(side=tk.LEFT)

            quantity_increase_button = tk.Button(quantity_frame, text="+",
                                                command=lambda id=product["id"]: self.increase_quantity(id),
                                                font=("Arial", 18))
            quantity_increase_button.pack(side=tk.LEFT)

            remove_button = tk.Button(product_frame, text="❌", command=lambda id=product["id"]: self.remove_product(id),
                                      fg="red", font=("Arial", 18))
            remove_button.pack(side=tk.LEFT)

    def increase_quantity(self, product_id):
        # Increase the quantity of a product in the kart
        if product_id in self.kart["products"]:
            self.kart["products"][product_id]["quantity"] += 1
            self.kart["sub_total"] = self.fastkart_sub_total(self.kart["products"])
            self.kart["tax"] = self.kart["sub_total"] * 0.18
            self.kart["total"] = self.kart["sub_total"] + self.kart["tax"]
            self.update_total_label()
            self.display_products()

    def decrease_quantity(self, product_id):
        # Decrease the quantity of a product in the kart
        if product_id in self.kart["products"]:
            if self.kart["products"][product_id]["quantity"] > 1:
                self.kart["products"][product_id]["quantity"] -= 1
            else:
                del self.kart["products"][product_id]
            self.kart["sub_total"] = self.fastkart_sub_total(self.kart["products"])
            self.kart["tax"] = self.kart["sub_total"] * 0.18
            self.kart["total"] = self.kart["sub_total"] + self.kart["tax"]
            self.update_total_label()
            self.display_products()

    def remove_product(self, product_id):
        # Remove a product from the kart
        if product_id in self.kart["products"]:
            del self.kart["products"][product_id]
            self.kart["sub_total"] = self.fastkart_sub_total(self.kart["products"])
            self.kart["tax"] = self.kart["sub_total"] * 0.18
            self.kart["total"] = self.kart["sub_total"] + self.kart["tax"]
            self.update_total_label()
            self.display_products()

    def pay_now(self):
        # Export the kart products to a CSV file
        self.export_to_csv()
        # Empty the kart when Pay Now button is clicked
        self.kart = {
            "products": {},
            "tax": 0,
            "sub_total": 0,
            "total": 0
        }
        self.update_total_label()
        self.display_products()

    def read_rfid(self):
        # Read the RFID tag ID from the Arduino and add the corresponding product to the kart
        if self.serial_port is not None:
            self.add_product()

        # Continue reading RFID tags
        self.root.after(100, self.read_rfid)

    def export_to_csv(self):
        # Generate a timestamp for the file name
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # Define the directory path
        directory = "../exports"

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Define the CSV file path with the timestamp in the name
        file_path = f"../exports/kart_products_{timestamp}.csv"

        # Check if the file exists
        file_exists = os.path.isfile(file_path)

        # Open the CSV file in append mode if it exists, otherwise open in write mode
        with open(file_path, mode='a' if file_exists else 'w', newline='') as file:
            writer = csv.writer(file)

            # Write the header row if the file is newly created
            if not file_exists:
                writer.writerow(["Product ID", "Title", "Rate", "Quantity"])

            # Write the product details for each product in the kart
            for product in self.kart["products"].values():
                writer.writerow([product["id"], product["title"], product["rate"], product["quantity"]])

        print(f"CSV file '{file_path}' has been created or updated successfully.")

# Create the main window
root = tk.Tk()
root.title("fastr")
root.attributes('-fullscreen', True)

# Create an instance of FastrkartGUI
fastrkart_gui = FastrkartGUI(root)

# Start the Tkinter event loop
root.mainloop()