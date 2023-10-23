        userID = session['id']
        with open('order.json', 'r') as f:
            order = json.load(f)
        # add cart to existing order
        for userID in order:
            if userID == session['id']:
                for orderID in order[userID]:
                    if orderID['orderId'] == 1:
                        orderID['order'].append(cart)
                        break
                else:
                    order[userID].append({"orderId": order[userID][-1]['orderId'] + 1, "order": [cart], "status": "pending"})
        else:
            order.append({session['id']: {"orderId": 1, "order": {cart}}})