import sys
import json
import boto3
import time

redshift_client = boto3.client('redshift-data')
session = boto3.session.Session()
secretsmanager_client = session.client(service_name = 'secretsmanager', region_name = 'us-east-1')

secret_name = 'ecommerce_redshift_secret'
get_secret_value_response = secretsmanager_client.get_secret_value(SecretId = secret_name)
secret_arn = get_secret_value_response['ARN']
secret = get_secret_value_response['SecretString']
secret_json = json.loads(secret)
cluster_id = secret_json['dbClusterIdentifier']

final_load_stmt = "call enriched_orders_sp();"

print('The cluster_id is ', cluster_id)
print('The secret_arn is ', secret_arn)
print('The final_load_stmt is ', final_load_stmt)

try:
        
    final_load_response = redshift_client.execute_statement(ClusterIdentifier = cluster_id, Database = 'dev', SecretArn = secret_arn, Sql = final_load_stmt)
    print('The final_load_response is ', final_load_response)
        
    final_sql_id = final_load_response['Id']
    print('The final_sql_id is ', final_sql_id)
        
    print('The status of the final load is ', redshift_client.describe_statement(Id = final_sql_id)['Status'])
        
    while not(redshift_client.describe_statement(Id = final_sql_id)['Status']) == 'FINISHED':
        time.sleep(15)
            
    print('The status of the final load is ', redshift_client.describe_statement(Id = final_sql_id)['Status'])
        
except Exception as e:
        
        print('Redshift final load failed with exception ', e)
    
