import json
import boto3
import pymysql
from decimal import Decimal


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
    params = get_event_params(event, ["skip", "limit"])

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
                SELECT 
                    c.*,
                    COUNT(s.customerId) AS interventionCount
                FROM Customer c
                LEFT JOIN Status s 
                    ON c.id = s.customerId
                WHERE c.id > %s
                GROUP BY c.id
                LIMIT %s
                """,
                (int(params["skip"]), int(params["limit"])),
            )
            rows = cursor.fetchall()
            formatted_result = []
            columns = [desc[0] for desc in cursor.description]
            for row in rows:
                formatted_row = []
                for item in row:
                    if type(item) == Decimal:
                        formatted_row.append(float(item))
                    else:
                        formatted_row.append(item)

                formatted_result.append(dict(zip(columns, formatted_row)))

            print(formatted_result)

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",  # allow all origins
                    "Access-Control-Allow-Headers": "Content-Type,x-api-key",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
                },
                "body": json.dumps(formatted_result),
            }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(str(e))}
