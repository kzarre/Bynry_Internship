def validate_product_request_data(data):
    # To check if the data is valid to be inserted into the database or not


    requirements = {
                    "name": (str,),
                    "sku": (str,),
                    "price": (int, float),
                    "warehouse_id": (int,),
                    "initial_quantity": (int,)
                    }


    # To make sure all data is present
    for key in requirements:
        if key not in data:
            return False

    # check if data is of the correct type
    for key,value in requirements.items():
        if not isinstance(data[key], value):
            return False

    # check if values are not negative
    if data["price"] <= 0 or data["initial_quantity"] < 0:
        return False

    # make sure SKUs are unique
    if Product.query.filter_by(sku=data['sku']).first():
        return False

    return True



@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json

    # What if request is Invalid,
    # data will be None and the function will throw an err

    if data is None:
        return {'error': "Request Invalid"}, 400

    if not validate_product_request_data(data):
        return {'error': "Data Format Error"}, 400

    
    product = Product(
        name=data['name'],
        sku=data['sku'],
        price=data['price'],
        # Removed Warehouse ID, as this is just the table for Products, not the inventory
    )
    
    db.session.add(product)

    db.session.flush()
    # This will provide ID to the product, as it is needed for the inventory
    
    # db.session.commit()
    # Removed because two commits and if backend fails in between 
    # then the transaction will be half done,
    # which is not how transactions should work

    inventory = Inventory(
        product_id=product.id,
        warehouse_id=data['warehouse_id'],
        quantity=data['initial_quantity']
    )
    
    db.session.add(inventory)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return {"error": "Database error"}, 500
    
    # Error handling when commiting if database goes down


    return {"message": "Product created", "product_id": product.id}, 200
