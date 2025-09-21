import json
import boto3


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
    required_params = [
        "id",
        "probability",
        "churn",
        "name",
        "seniorCitizen",
        "married",
        "dependents",
        "numberOfDependents",
        "referredAFriend",
        "numberOfReferrals",
        "tenureMonths",
        "phoneService",
        "multipleLines",
        "internetService",
        "internetType",
        "onlineSecurity",
        "onlineBackup",
        "deviceProtection",
        "premiumTechSupport",
        "streamingTV",
        "streamingMovies",
        "streamingMusic",
        "unlimitedData",
        "contractType",
        "paymentMethod",
        "paperlessBilling",
        "avgMonthlyLongDistanceCharges",
        "avgMonthlyGBDownload",
        "monthlyCharge",
        "totalCharges",
        "totalRefunds",
        "totalExtraDataCharges",
        "totalLongDistanceCharges",
        "totalRevenue",
        "cltv",
        "satisfactionScore",
        "interventionCount",
    ]
    params = get_event_params(event, required_params)
    id = params.pop("id")  # keep for later
    name = params.pop("name")  # keep for later
    params.pop("probability")
    params.pop("churn")
    params.pop("interventionCount")

    internet_type = params["internetType"]
    values = list(params.values())
    for index, (key, value) in enumerate(params.items()):
        if key == "internetType":
            if value == "dsl":
                values.insert(index + 1, 0)
                values.insert(index + 2, 1)
                values.insert(index + 3, 0)
            elif value == "fibre":
                values.insert(index + 1, 0)
                values.insert(index + 2, 0)
                values.insert(index + 3, 1)
            elif value == "cable":
                values.insert(index + 1, 1)
                values.insert(index + 2, 0)
                values.insert(index + 3, 0)
            else:
                values.insert(index + 1, 0)
                values.insert(index + 2, 0)
                values.insert(index + 3, 0)

            values.pop(index)  # remove internetType

        elif key == "contractType":
            if value == "monthly":
                values.insert(index + 3, 1)
                values.insert(index + 4, 0)
                values.insert(index + 5, 0)
            elif value == "one year":
                values.insert(index + 3, 0)
                values.insert(index + 4, 1)
                values.insert(index + 5, 0)
            else:
                values.insert(index + 3, 0)
                values.insert(index + 4, 0)
                values.insert(index + 5, 1)

            values.pop(index + 2)  # remove contractType

        elif key == "paymentMethod":
            if value == "bank withdrawal":
                values.insert(index + 6, 1)
                values.insert(index + 7, 0)
                values.insert(index + 8, 0)
            elif value == "credit card":
                values.insert(index + 6, 0)
                values.insert(index + 7, 1)
                values.insert(index + 8, 0)
            else:
                values.insert(index + 6, 0)
                values.insert(index + 7, 0)
                values.insert(index + 8, 1)

            values.pop(index + 4)  # remove paymentMethod

    runtime_client = boto3.client("sagemaker-runtime")

    response = runtime_client.invoke_endpoint(
        EndpointName="xgboost-churn-model",  # replace with your endpoint name
        ContentType="text/csv",  # or "text/csv" depending on your model
        Body=",".join([str(v) for v in values]),
    )

    # Response body is a stream -> decode it
    result = float(response["Body"].read().decode("utf-8"))
    rounded_result = round(result, 4)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # allow all origins
            "Access-Control-Allow-Headers": "Content-Type,x-api-key",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
        },
        "body": json.dumps(rounded_result),
    }


lambda_handler(
    {
        "id": 37,
        "probability": 0.4907,
        "churn": 1,
        "name": "Phillip Mull",
        "seniorCitizen": 0,
        "married": 1,
        "dependents": 0,
        "numberOfDependents": 0,
        "referredAFriend": 1,
        "numberOfReferrals": 1,
        "tenureMonths": 20,
        "phoneService": 0,
        "multipleLines": 0,
        "internetService": 1,
        "internetType": "dsl",
        "onlineSecurity": 0,
        "onlineBackup": 0,
        "deviceProtection": 0,
        "premiumTechSupport": 0,
        "streamingTV": 0,
        "streamingMovies": 0,
        "streamingMusic": 0,
        "unlimitedData": 1,
        "contractType": "monthly",
        "paymentMethod": "bank withdrawal",
        "paperlessBilling": 1,
        "avgMonthlyLongDistanceCharges": 0,
        "avgMonthlyGBDownload": 10,
        "monthlyCharge": 24.45,
        "totalCharges": 482.8,
        "totalRefunds": 0,
        "totalExtraDataCharges": 0,
        "totalLongDistanceCharges": 0,
        "totalRevenue": 482.8,
        "cltv": 3298,
        "satisfactionScore": 3,
        "interventionCount": 0,
    },
    None,
)

