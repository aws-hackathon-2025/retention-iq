## Backend
The backend of the app consists of the **lambda functions** used with **API Gateway** to create and manage the serverless backend. 

### Notes on Architecture:

- Development requirements (dev_requirements.txt) contain the packages needed for development on a local machine.

- Main requirements (main_requirements.txt) contain ONLY the external packages needed by AWS Lambda. Other packages are already provided, such as *boto3*.

- A deployment.zip file exists for each Lambda function. This is the latest deployment zip imported for the respective Lambda function.