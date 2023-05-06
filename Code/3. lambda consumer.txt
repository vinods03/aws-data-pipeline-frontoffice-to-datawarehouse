import json
import base64
import boto3

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('orders')

items_to_add = []

def lambda_handler(event, context):
    
    print('The event is ', event)
    
    for record in event['Records']:
        
        # print('The record is ', record)
        record_data = json.loads(base64.b64decode(record['kinesis']['data']).decode('utf-8'))
        print('The record data is ', record_data)
        
        item = {
            'order_id': record_data['order_id'],
            'customer_id': record_data['customer_id'],
            'seller_id': record_data['seller_id'],
            'order_purchase_timestamp': record_data['order_purchase_timestamp']
           }
        
        for i in range(0, len(record_data['products'])):
            item['product_code_'+str(i+1)] = record_data['products'][i]['product_code']
            item['product_name_'+str(i+1)] = record_data['products'][i]['product_name']
            item['product_price_'+str(i+1)] = record_data['products'][i]['product_price']
            item['product_qty_'+str(i+1)] = record_data['products'][i]['product_qty']
           
        order_value = 0
        for i in range(0, len(record_data['products'])):
            order_value = order_value + (item['product_price_'+str(i+1)]*item['product_qty_'+str(i+1)])
            
        item['order_value'] = order_value
            
        items_to_add.append(item)
        
    try:
        with orders_table.batch_writer() as batch:
            for item in items_to_add:
                batch.put_item(Item = item)
        print('Orders loaded successfully into DynamoDB')
    except Exception as e:
        print('Unable to process into DynamoDB. The exception is ', e)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Lambda consumer has completed!')
    }
