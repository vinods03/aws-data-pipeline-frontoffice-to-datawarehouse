import sys
import os
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from pyspark.sql.functions import col
from pyspark.sql.functions import explode
from pyspark.sql.functions import split 
# split is not used here because we get a struct after explode. we use the "." notation to access columns within a struct.
# if we had got a string after explode, split might have helped in accessing individual columns
from pyspark.sql.functions import year, month, dayofmonth, hour
from pyspark.context import SparkContext

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'appName', 'tgt_file_format', 'tgt_bucket'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

appName = args['appName']
tgt_file_format = args['tgt_file_format']
tgt_bucket = args['tgt_bucket']
    
# print('The appName is ', appName)
# print('The target file format is ', tgt_file_format)
# print('The target bucket is ', tgt_bucket)
    
# spark.sql('select current_date()').show()

print('****************************************** Source DF ************************************************')


S3bucket_node1 = glueContext.create_dynamic_frame.from_options(
    format_options={},
    connection_type="s3",
    format="json",
    connection_options={
        "paths": ["s3://vinod-streaming-project-bucket"],
        "recurse": True,
    },
    transformation_ctx="S3bucket_node1",
)

# source_df = spark.read.json('s3://vinod-streaming-project-bucket/orders/')
# source_df.printSchema()
# source_df.show(truncate=False)
# source_dyn_df = DynamicFrame.fromDF(source_df,  glueContext)

source_dyn_df_trnsf_ctx = ApplyMapping.apply(
        frame = S3bucket_node1, 
        mappings = [
        ("order_id", "string", "order_id", "string"),
        ("customer_id", "string", "customer_id", "string"),
        ("seller_id", "string", "seller_id", "string"),
        ("products", "array", "products", "array"),
        ("order_value", "int", "order_value", "int"),
        ("order_purchase_timestamp", "string", "order_purchase_timestamp", "string")
        ], 
        transformation_ctx="source_dyn_df_trnsf_ctx"
    )
new_source_df = DynamicFrame.toDF(source_dyn_df_trnsf_ctx)

print('****************************************** Source exploded DF ************************************************')
# multiple products are exploded into multiple rows
# if an order has 3 products in the column 'products', that row will be exploded into 3 rows here

source_exploded_df = new_source_df.withColumn('exploded_products', explode('products'))
# source_exploded_df.printSchema()
# source_exploded_df.show(truncate=False)
source_exploded_dyn_df = DynamicFrame.fromDF(source_exploded_df,  glueContext)
source_exploded_dyn_df_trnsf_ctx = ApplyMapping.apply(
        frame = source_exploded_dyn_df,
        mappings = [
           ("order_id", "string", "order_id", "string"),
           ("customer_id", "string", "customer_id", "string"),
           ("seller_id", "string", "seller_id", "string"),
           ("products", "array", "products", "array"),
           ("exploded_products", "map", "exploded_products", "map"),
           ("order_value", "int", "order_value", "int"),
           ("order_purchase_timestamp", "string", "order_purchase_timestamp", "string")
            ], 
         transformation_ctx="source_exploded_dyn_df_trnsf_ctx"
        )
new_source_exploded_df = DynamicFrame.toDF(source_exploded_dyn_df_trnsf_ctx)
    
print('****************************************** Source transformed DF ************************************************')
# to access individual columns in struct, use the "." notation as shown below

source_transformed_df = new_source_exploded_df.withColumn('product_code',col('exploded_products.product_code')).withColumn('product_name',col('exploded_products.product_name')).withColumn('product_price',col('exploded_products.product_price')).withColumn('product_qty',col('exploded_products.product_qty'))
# source_transformed_df.printSchema()
# source_transformed_df.show()
source_transformed_dyn_df = DynamicFrame.fromDF(source_transformed_df,  glueContext)
source_transformed_dyn_df_trnsf_ctx = ApplyMapping.apply(
        frame = source_transformed_dyn_df,
        mappings = [
           ("order_id", "string", "order_id", "string"),
           ("customer_id", "string", "customer_id", "string"),
           ("seller_id", "string", "seller_id", "string"),
           ("products", "array", "products", "array"),
           ("exploded_products", "map", "exploded_products", "map"),
           ("product_code", "string", "product_code", "string"),
           ("product_name", "string", "product_name", "string"),
           ("product_price", "int", "product_price", "int"),
           ("product_qty", "int", "product_qty", "int"),
           ("order_value", "int", "order_value", "int"),
           ("order_purchase_timestamp", "string", "order_purchase_timestamp", "string")
            ], 
         transformation_ctx="source_transformed_dyn_df_trnsf_ctx"
        )
new_source_transformed_df = DynamicFrame.toDF(source_transformed_dyn_df_trnsf_ctx)

print('****************************************** extract partition columns **********************************************')

source_further_transformed_df = new_source_transformed_df.withColumn('order_purchase_year', year(col('order_purchase_timestamp'))) \
    .withColumn('order_purchase_month', month(col('order_purchase_timestamp'))) \
    .withColumn('order_purchase_day', dayofmonth(col('order_purchase_timestamp'))) \
    .withColumn('order_purchase_hour', hour(col('order_purchase_timestamp')))
# source_further_transformed_df.printSchema()
# source_further_transformed_df.show()
source_further_transformed_dyn_df = DynamicFrame.fromDF(source_further_transformed_df,  glueContext)
source_further_transformed_dyn_df_trnsf_ctx = ApplyMapping.apply(
        frame = source_further_transformed_dyn_df,
        mappings = [
           ("order_id", "string", "order_id", "string"),
           ("customer_id", "string", "customer_id", "string"),
           ("seller_id", "string", "seller_id", "string"),
           ("products", "array", "products", "array"),
           ("exploded_products", "map", "exploded_products", "map"),
           ("product_code", "string", "product_code", "string"),
           ("product_name", "string", "product_name", "string"),
           ("product_price", "int", "product_price", "int"),
           ("product_qty", "int", "product_qty", "int"),
           ("order_purchase_year", "int", "order_purchase_year", "int"),
           ("order_purchase_month", "int", "order_purchase_month", "int"),
           ("order_purchase_day", "int", "order_purchase_day", "int"),
           ("order_purchase_hour", "int", "order_purchase_hour", "int"),
           ("order_value", "int", "order_value", "int"),
           ("order_purchase_timestamp", "string", "order_purchase_timestamp", "string")
            ], 
         transformation_ctx="source_further_transformed_dyn_df_trnsf_ctx"
        )
new_source_further_transformed_df = DynamicFrame.toDF(source_further_transformed_dyn_df_trnsf_ctx)

print('****************************************** final DF ************************************************')
# we select only the required columns. products and exploded_products columns are not needed any more because we have extracted the rows / columns from these columns

final_df = new_source_further_transformed_df.select('order_id','customer_id','seller_id','product_code','product_name','product_price','product_qty','order_value','order_purchase_timestamp','order_purchase_year','order_purchase_month','order_purchase_day', 'order_purchase_hour')
# final_df.printSchema()
# final_df.show()
final_dyn_df = DynamicFrame.fromDF(final_df,  glueContext)
final_dyn_df_trnsf_ctx = ApplyMapping.apply(
        frame = final_dyn_df,
        mappings = [
           ("order_id", "string", "order_id", "string"),
           ("customer_id", "string", "customer_id", "string"),
           ("seller_id", "string", "seller_id", "string"),
           ("product_code", "string", "product_code", "string"),
           ("product_name", "string", "product_name", "string"),
           ("product_price", "int", "product_price", "int"),
           ("product_qty", "int", "product_qty", "int"),
           ("order_value", "int", "order_value", "int"),
           ("order_purchase_timestamp", "string", "order_purchase_timestamp", "string"),
           ("order_purchase_year", "int", "order_purchase_year", "int"),
           ("order_purchase_month", "int", "order_purchase_month", "int"),
           ("order_purchase_day", "int", "order_purchase_day", "int"),
           ("order_purchase_hour", "int", "order_purchase_hour", "int")
        ], 
         transformation_ctx="final_dyn_df_trnsf_ctx"
        )
        
# new_final_df = DynamicFrame.toDF(final_dyn_df_trnsf_ctx)

print('****************************************** write the transformed data *********************************************')
# write(new_final_df, tgt_file_format, tgt_bucket, 'order_purchase_year','order_purchase_month','order_purchase_day', 'order_purchase_hour')
    
# Script generated for node S3 bucket
S3bucket_node3 = glueContext.write_dynamic_frame.from_options(
    frame=final_dyn_df_trnsf_ctx,
    connection_type="s3",
    format="glueparquet",
    connection_options={
        "path": "s3://vinod-streaming-project-staging-bucket",
        "partitionKeys": ["order_purchase_year","order_purchase_month","order_purchase_day","order_purchase_hour"],
    },
transformation_ctx="S3bucket_node3",
)
    
job.commit()
