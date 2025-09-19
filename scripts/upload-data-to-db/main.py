import csv
import boto3
from decimal import Decimal

# DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Customers")


def normalize_row(row):
    """Convert raw CSV row to clean DynamoDB format"""
    item = {}

    # ID and probability
    item["probability"] = Decimal(row["Probability"])
    item["churn"] = int(row["Churn"])
    item["name"] = row["Name"]
    item["customerId"] = row.get("Customer ID") or None

    # Core demographics
    item["seniorCitizen"] = int(row["Senior Citizen"])
    item["married"] = int(row["Married"])
    item["dependents"] = int(row["Dependents"])
    item["numberOfDependents"] = int(row["Number of Dependents"])
    item["referredAFriend"] = int(row["Referred a Friend"])
    item["numberOfReferrals"] = int(row["Number of Referrals"])
    item["tenureMonths"] = int(row["Tenure in Months"])

    # Services
    item["phoneService"] = int(row["Phone Service"])
    item["multipleLines"] = int(row["Multiple Lines"])
    item["internetService"] = int(row["Internet Service"])

    # Internet type (one-hot collapse)
    if row["Internet Cable"] == "1":
        item["internetType"] = "cable"
    elif row["Internet DSL"] == "1":
        item["internetType"] = "dsl"
    elif row["Internet Fiber Optic"] == "1":
        item["internetType"] = "fiber"
    else:
        item["internetType"] = "none"

    # Extra services
    item["onlineSecurity"] = int(row["Online Security"])
    item["onlineBackup"] = int(row["Online Backup"])
    item["deviceProtection"] = int(row["Device Protection Plan"])
    item["premiumTechSupport"] = int(row["Premium Tech Support"])
    item["streamingTV"] = int(row["Streaming TV"])
    item["streamingMovies"] = int(row["Streaming Movies"])
    item["streamingMusic"] = int(row["Streaming Music"])
    item["unlimitedData"] = int(row["Unlimited Data"])

    # Contract type
    if row["Contract Month to Month"] == "1":
        item["contractType"] = "month_to_month"
    elif row["Contract One Year"] == "1":
        item["contractType"] = "one_year"
    elif row["Contract Two Year"] == "1":
        item["contractType"] = "two_year"
    else:
        item["contractType"] = "unknown"

    # Payment method
    if row["Bank Withdrawal"] == "1":
        item["paymentMethod"] = "bank_withdrawal"
    elif row["Credit Card"] == "1":
        item["paymentMethod"] = "credit_card"
    elif row["Mailed Check"] == "1":
        item["paymentMethod"] = "mailed_check"
    else:
        item["paymentMethod"] = "unknown"

    # Charges & revenue
    item["paperlessBilling"] = int(row["Paperless Billing"])
    item["avgMonthlyLongDistanceCharges"] = Decimal(
        row["Avg Monthly Long Distance Charges"]
    )
    item["avgMonthlyGBDownload"] = Decimal(row["Avg Monthly GB Download"])
    item["monthlyCharge"] = Decimal(row["Monthly Charge"])
    item["totalCharges"] = Decimal(row["Total Charges"])
    item["totalRefunds"] = Decimal(row["Total Refunds"])
    item["totalExtraDataCharges"] = Decimal(row["Total Extra Data Charges"])
    item["totalLongDistanceCharges"] = Decimal(row["Total Long Distance Charges"])
    item["totalRevenue"] = Decimal(row["Total Revenue"])
    item["cltv"] = Decimal(row["CLTV"])
    item["satisfactionScore"] = int(row["Satisfaction Score"])

    # Empty interventions array
    item["interventions"] = []

    return item


def load_csv_to_dynamodb(csv_file):
    dataset_id = 1
    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            # Update dataset_id
            if i == 353:
                dataset_id = 2

            # Normalize csv data into dictionary
            item = normalize_row(row)
            # Add datasetId
            item["datasetId"] = dataset_id

            table.put_item(Item=item)

            if i % 50 == 0:
                print(f"Inserted {i} records...")


if __name__ == "__main__":
    load_csv_to_dynamodb("../../dataset/business-data-final.csv")
    print("✅ Upload complete!")
