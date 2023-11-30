import json
import random

with open('order.json', 'r') as f:
  order = json.load(f)
with open('user.json', 'r') as f:
  user = json.load(f)

restaurant = user['deliveryPersonnel']

for item in order:
  for orders in item['order']:
      random_index = random.randint(0, len(restaurant) - 1)
      if 'deliveryPersonnel' in orders:
        orders['deliveryPersonnel'] = restaurant[random_index].get('id')
      else:
        orders['deliveryPersonnel']= None
        orders['deliveryPersonnel'] = restaurant[random_index].get('id')

with open('order.json', 'w') as f:
  json.dump(order, f, indent=2)