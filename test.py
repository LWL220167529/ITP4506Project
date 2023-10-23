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





{%if foods%} {% for item in foods %}
          <tr>
            <td>
              <img
                src="{{url_for('static', filename=item.image)}}"
                alt="{{item.image}}"
                width="50"
                height="50"
              />
            </td>
            <td>{{item.name}}</td>
            <td>{{item.category}}</td>
            <td>{{item.description}}</td>
            <td>${{item.price}}</td>
            <td>
              <button class="btn btn-sm btn-warning">Edit</button>
              <button class="btn btn-sm btn-danger">Delete</button>
            </td>
          </tr>
          {%endfor%} {% endif %}