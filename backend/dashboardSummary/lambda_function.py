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
    body_parameters = {}

    # Get body parameters
    if "body" in event and event["body"] is not None:
        try:
            # Parse the JSON string from the body and store them
            body_params = json.loads(event["body"])
            for param in params:
                body_parameters[param] = body_params.get(param)

        except:
            return None

    # Get event parameters (for testing, not https)
    elif event:
        for param in params:
            body_parameters[param] = event.get(param)

    # If neither is present, throw error
    else:
        return None

    return body_parameters


def lambda_handler(event, context):
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
            # Total count
            cursor.execute("SELECT COUNT(*) FROM Customer")
            total_count = cursor.fetchone()[0]

            # Count with probability > 0.75
            cursor.execute("SELECT COUNT(*) FROM Customer WHERE probability >= 0.2")
            high_prob_count = cursor.fetchone()[0]

            # Count grouped by satisfactionScore
            cursor.execute(
                "SELECT satisfactionScore, COUNT(*) FROM Customer GROUP BY satisfactionScore"
            )
            satisfaction_counts = cursor.fetchall()
            formatted_satis_counts = dict(
                (str(score), count) for score, count in satisfaction_counts
            )

            # Count grouped by risk category
            cursor.execute(
                """
                SELECT 
                    CASE
                        WHEN probability >= 0.75 THEN 'High Risk'
                        WHEN probability >= 0.2 AND probability < 0.75 THEN 'Medium Risk'
                        ELSE 'Low Risk'
                    END AS riskCategory,
                    COUNT(*) AS customerCount
                FROM Customer
                GROUP BY riskCategory;
                """
            )
            risk_counts = cursor.fetchall()
            formatted_risk_counts = dict(risk_counts)

            # Count grouped by interventions
            cursor.execute(
                """
                SELECT 
                    SUM(CASE WHEN s.customerId IS NULL THEN 1 ELSE 0 END) AS noInterventionCount,
                    SUM(CASE WHEN s.customerId IS NOT NULL THEN 1 ELSE 0 END) AS interventionCount
                FROM Customer c
                LEFT JOIN (
                    SELECT DISTINCT customerId 
                    FROM Status
                ) s ON c.id = s.customerId;
                """
            )
            intervention_row = [int(value) for value in cursor.fetchone()]
            intervention_columns = [desc[0] for desc in cursor.description]
            intervention_counts = dict(zip(intervention_columns, intervention_row))

            results = {
                "totalCount": total_count,
                "highProbCount": high_prob_count,
                "satisfactionCounts": formatted_satis_counts,
                "riskCounts": formatted_risk_counts,
                "interventionCounts": intervention_counts,
            }

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",  # allow all origins
                    "Access-Control-Allow-Headers": "Content-Type,x-api-key",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
                },
                "body": json.dumps(results),
            }

    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps("Internal server error")}
