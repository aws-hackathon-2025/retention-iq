import json
import boto3
import pymysql


def get_secret():
    secret_name = "hackathon-db-secret"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    secret_value = client.get_secret_value(SecretId=secret_name)
    secret_dict = json.loads(secret_value["SecretString"])

    return secret_dict


def get_event_params(event, params):
    request_parameters = {}

    # Access the queryStringParameters
    query_params = event.get("queryStringParameters")

    # Get body parameters
    if "body" in event and event["body"] is not None:
        try:
            # Parse the JSON string from the body and store them
            body_params = json.loads(event["body"])
            for param in params:
                request_parameters[param] = body_params.get(param)

        except:
            return None

    # Get query parameters
    elif query_params:
        for param in params:
            request_parameters[param] = query_params.get(param)

    # Get event parameters (for testing, not https)
    elif event:
        for param in params:
            request_parameters[param] = event.get(param)

    # If neither is present, throw error
    else:
        return None

    return request_parameters


def lambda_handler(event, context):
    params = get_event_params(event, ["id", "emailType"])

    if params["emailType"] == "support":
        intervention_desc = "Send a support email to customer."
        subject = {"Data": "Telecom Support Email"}
        body = {
            "Text": {
                "Data": "Hello, this is a support email from Telecom! It seems you've had some troubles recently with our services; we would love to help you. Please let us know what challenges you are facing and how we can help support you."
            }
        }
    else:
        intervention_desc = "Offer a discount of 20% to the user."
        subject = {"Data": "Telecom Discount"}
        body = {
            "Text": {
                "Data": "Hi! Here's a 20% discount voucher for your next month with Telecom: [VOUCHER CODE: 937413]"
            }
        }

    ses = boto3.client("ses", region_name="us-east-1")

    source = "rrtel2fi0@mozmail.com"
    destination = "pakdad@duck.com"

    ses.send_email(
        Source=source,  # must be verified
        Destination={"ToAddresses": [destination]},  # must also be verified in sandbox
        Message={
            "Subject": subject,
            "Body": body,
        },
    )

    # Get secret
    secret = get_secret()

    # Connect to db
    user = secret["username"]
    password = secret["password"]
    host = secret["host"]
    database = "telecom"

    conn = pymysql.connect(
        user=user,
        password=password,
        database=database,
        host=host,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Status (customerId, createdAt, description)
                VALUES (%s, NOW(), %s);
                """,
                (int(params["id"]), intervention_desc),
            )
            conn.commit()

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",  # allow all origins
                    "Access-Control-Allow-Headers": "Content-Type,x-api-key",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
                },
                "body": json.dumps({"message": "Successfully sent message"}),
            }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(str(e))}



lambda_handler({"id": 37, "emailType": "support"}, None)