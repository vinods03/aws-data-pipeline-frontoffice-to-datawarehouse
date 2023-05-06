import json
import boto3
import base64

transformed_data = []

def lambda_handler(event, context):
    
    print('The event is ', event)
    for record in event['records']:
        # print('The record is ', record)
        
        record_data = json.loads(base64.b64decode(record['data']).decode('utf-8'))
        print('The record_data is ', record_data)
        
        order_id = record_data['order_id']
        customer_id = record_data['customer_id']
        seller_id = record_data['seller_id']
        products = record_data['products']
        order_purchase_timestamp = record_data['order_purchase_timestamp']
        
        order_value = 0
        for i in range(0, len(products)):
            order_value = order_value + (products[i]['product_price'] * products[i]['product_qty'])
            
        transformed_item = {
            'order_id': order_id,
            'customer_id': customer_id,
            'seller_id': seller_id,
            'products': products,
            'order_value': order_value,
            'order_purchase_timestamp': order_purchase_timestamp
        }
        
        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(json.dumps(transformed_item).encode('utf-8'))
        }
        
        transformed_data.append(output_record)
    
    return {
        'records': transformed_data
    }
