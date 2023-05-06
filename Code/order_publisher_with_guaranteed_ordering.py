import boto3
import logging
import json
import time
import sys
from order_generator import make_order

logging.basicConfig(
  format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S',
  level=logging.INFO,
  handlers=[
      logging.FileHandler("producer.log"),
      logging.StreamHandler(sys.stdout)
  ]
)

kinesis = boto3.client('kinesis')
shard_seq_num = {}

def publish_order(args):

    stream_name = args[1]
    
    while True:

        order = make_order()
        kwargs = {'StreamName': stream_name, 'Data': json.dumps(order).encode('utf-8'), 'PartitionKey': order['seller_id']}
        # I tried to use a different variable but the put_record failed with error "put_record() only accepts keyword arguments"
        # order_object = {'StreamName': stream_name, 'Data': json.dumps(order).encode('utf-8'), 'PartitionKey': order['seller_id']}

        # Note that we are using seller_id and not order_id as the partition key here
        # This is because, we want to see that for the same partition key, when a record is loaded into the same shard, sequencing is maintained
        # order_id is a running number and we will not be able to test the "same partition key" concept
        # All records with same partition key go into the same shard
        # The record published first will have a lower sequence number in the kinesis data stream compared to the record published later
        

        if order['seller_id'] in shard_seq_num:
            sequence_num = shard_seq_num.get(order['seller_id'])
            kwargs.update(SequenceNumberForOrdering = sequence_num)
            # order_object.update('SequenceNumberForOrdering': sequence_num) This was an invalid syntax

        try:
            response = kinesis.put_record(**kwargs)
            # response = kinesis.put_record(order_object)
            logging.info(f'The order {order} has been successfully published into the kinesis stream {stream_name}')
            logging.info(f"The seller id is {order['seller_id']}")
            logging.info(f"The order is delivered in the shard {response['ShardId']} with sequence no {response['SequenceNumber']}")
        except Exception as e:
            logging.error(f"Failed to publish the order {order} into the kinesis stream {stream_name}. The exception is {e}")

        time.sleep(10)

if __name__ == '__main__':
    publish_order(sys.argv)
    