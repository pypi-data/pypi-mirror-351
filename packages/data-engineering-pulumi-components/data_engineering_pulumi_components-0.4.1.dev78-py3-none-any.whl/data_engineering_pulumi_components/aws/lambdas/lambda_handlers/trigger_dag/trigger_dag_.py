import os
import boto3
import http.client
import base64
import ast
import time

client = boto3.client("mwaa")


def handler(event, context):
    mwaa_env_name = os.environ["MWAA_ENV_NAME"]
    dag_name = os.environ["DAG_NAME"]
    wait = int(os.environ["WAIT"])
    mwaa_cli_command = "dags trigger"
    time.sleep(wait)

    # get web token
    mwaa_cli_token = client.create_cli_token(Name=mwaa_env_name)

    conn = http.client.HTTPSConnection(mwaa_cli_token["WebServerHostname"])
    payload = mwaa_cli_command + " " + dag_name
    headers = {
        "Authorization": "Bearer " + mwaa_cli_token["CliToken"],
        "Content-Type": "text/plain",
    }

    conn.request("POST", "/aws_mwaa/cli", payload, headers)
    res = conn.getresponse()
    data = res.read()
    dict_str = data.decode("UTF-8")
    mydata = ast.literal_eval(dict_str)
    return base64.b64decode(mydata["stdout"])
