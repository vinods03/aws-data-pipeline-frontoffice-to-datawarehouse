import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket
S3bucket_node1 = glueContext.create_dynamic_frame.from_options(
    format_options={},
    connection_type="s3",
    format="parquet",
    connection_options={
        "paths": ["s3://vinod-streaming-project-staging-bucket"],
        "recurse": True,
    },
    transformation_ctx="S3bucket_node1",
)

# Script generated for node ApplyMapping
ApplyMapping_node2 = ApplyMapping.apply(
    frame=S3bucket_node1,
    mappings=[
        ("order_id", "string", "order_id", "string"),
        ("customer_id", "string", "customer_id", "string"),
        ("seller_id", "string", "seller_id", "string"),
        ("product_code", "string", "product_code", "string"),
        ("product_name", "string", "product_name", "string"),
        ("product_price", "bigint", "product_price", "long"),
        ("product_qty", "bigint", "product_qty", "long"),
        ("order_value", "bigint", "order_value", "long"),
        ("order_purchase_timestamp", "string", "order_purchase_timestamp", "string"),
    ],
    transformation_ctx="ApplyMapping_node2",
)

# Script generated for node Amazon Redshift
AmazonRedshift_node1681046762753 = glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_node2,
    database="ecommerce-database",
    table_name="redshift_dev_ecommerce_staging_orders",
    redshift_tmp_dir=args["TempDir"],
    additional_options={
        "aws_iam_role": "arn:aws:iam::100163808729:role/MyRedshiftRoleWithAdminAccess"
    },
    transformation_ctx="AmazonRedshift_node1681046762753",
)

job.commit()
