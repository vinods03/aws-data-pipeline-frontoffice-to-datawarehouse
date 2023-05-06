import json
import boto3
import logging
import sys
import time
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

def publish_order(args):

    stream_name = args[1]
    logging.info(f'Starting to write orders into the stream {stream_name}')

    while True:

        order = make_order()

        try:
            response = kinesis.put_record(StreamName = stream_name, Data = json.dumps(order).encode('utf-8'), PartitionKey = order['order_id'])
            logging.info(f'Successfully transferred {order} into the data stream {stream_name}')
            logging.info(f"The order is delivered in the shard {response['ShardId']} with sequence no {response['SequenceNumber']}")
        except Exception as e:
            logging.error(f'Failed to deliver order {order} into the stream {stream_name}. The exception is {e}')

        time.sleep(10)

if __name__ == '__main__':
    publish_order(sys.argv)
