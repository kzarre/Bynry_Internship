"""
ASSUMPTIONS
===========
1) We have a table for alerts

alert = (
		(inventory.warehouse_id, inventory.product_id): Primary Key,
		time_of_below_threshold: date and time,
		days_until_stockout: inventory.quantity / inventory.daily_sales
)

2) There is a theshold column in the products table

3)There is a column for daily_sales and last_sale column

 [ 	last sale column to make sure we reset daily_sales, 
 	if we make a sale and the last_sale!=today, we reset daily_sales ]
 
 [ WE WILL USE THIS TO PREDICT WHEN WE WILL BE OUT OF STOCK ]

4) The puchase route checks whenever someone makes 
   a purchase whether the quantity is below
   threshold or not, if yes, add it to alerts.

Questions for the Product Team:
=======================
1) If one warehouse is below threshold and other is above, should there be an alert?

2) should we make periodic checks for which product is below threshold?
	OR
   add an alert whenever there is a purchase and the no of products goes below threshold
   and the product_id, warehouse_id is not present in the table

   I prefer the latter as it takes less resources

3) Are we supposed to add remove alert whenever more product is added to the warehouse?
"""



@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alert(company_id):
	try:
		query = """
            SELECT 
                    a.product_id, 
                    p.name AS product_name, 
                    p.sku,           
                    p.threshold,     
                    a.warehouse_id, 
                    w.name AS warehouse_name,
                    i.quantity, 
                    i.daily_sales,
                    s.id AS supplier_id,            
                    s.name AS supplier_name,        
                    s.contact_email                 
                FROM alerts a
                JOIN inventory i ON a.warehouse_id = i.warehouse_id AND a.product_id = i.product_id
                JOIN products p ON a.product_id = p.id
                JOIN warehouses w ON a.warehouse_id = w.id
                JOIN suppliers s ON p.supplier_id = s.id 
                WHERE p.company_id = ?
        """

        cursor.execute(query, (company_id,))
        rows = cursor.fetchall()

        results = []

        for row in rows:
            sales_velocity = row['daily_sales'] if row['daily_sales'] > 0 else 0.1
            stockout_days = int(row['quantity'] / sales_velocity)
        	
            results.append({
                            "product_id": row['product_id'],
                            "product_name": row['product_name'],
                            "sku": row['sku'],
                            "warehouse_id": row['warehouse_id'],
                            "warehouse_name": row['warehouse_name'],
                            "current_stock": row['quantity'],
                            "threshold": row['threshold'],
                            "days_until_stockout": stockout_days,
                            "supplier": {
                                "id": row['supplier_id'],
                                "name": row['supplier_name'],
                                "contact_email": row['contact_email']
                            }
                        })


        return jsonify({
            "alerts": results,
            "total_alerts": len(results)
        }), 201

	except Exception as e:
        return jsonify({"error": str(e)}), 500