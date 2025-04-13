import pandas as pd
import random

class AddressGenerator:
    def __init__(self, csv_data_path):
        # Load CSV data into a DataFrame
        self.df = pd.read_csv(csv_data_path)
        print(self.df.head())
    
    def generate_address(self, format_string, seed=None):
        # Randomly select a row
        if seed:
            random.seed(seed)
        random_row = self.df.sample().iloc[0]
        
        # Extract the necessary values from the selected row
        print(random_row)
        postal_code = random_row['Індекс НП']
        village = random_row['Населений пункт']
        region = random_row['Область']
        street = random_row['Назва вулиці']
        
        # Extract available house numbers as a list from the "№ будинку" column
        house_numbers = random_row['№ будинку'].split(',')
        house_number = random.choice(house_numbers).strip()
        
        # Generate the address based on the format string
        formatted_address = format_string
        formatted_address = formatted_address.replace("{index}", str(postal_code))
        formatted_address = formatted_address.replace("{village}", village)
        formatted_address = formatted_address.replace("{region}", region)
        formatted_address = formatted_address.replace("{street}", street)
        formatted_address = formatted_address.replace("{house_number}", house_number)
        
        return formatted_address


# Create the AddressGenerator object
address_generator = AddressGenerator("./dict/address.csv")

# Generate an address based on a format string
generated_address = address_generator.generate_address("{index}, {village}, {street}, {house_number}")
print(generated_address)
