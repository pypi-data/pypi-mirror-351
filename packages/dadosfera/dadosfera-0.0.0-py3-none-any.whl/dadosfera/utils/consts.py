import os

CUSTOMER_NAME = os.getenv("CUSTOMER_NAME", "")

DADOSFERA_LANDING_ZONE = f'dadosfera-landing-{CUSTOMER_NAME}-prd-us-east-1-611330257153'
DADOSFERA_DEMO_SECRET_ID = f'prd/root/snowflake_credentials/{CUSTOMER_NAME}'

PAGE_LOGO = "https://s3.amazonaws.com/gupy5/production/companies/1286/career/2122/images/2022-01-05_13-07_logo.png"
LOGO = "https://cdn-images-1.medium.com/max/1200/1*OPrCFbKQFOeL0QKCuDeR1g.png"
