from pathlib import Path
from typing import Optional

from data_engineering_pulumi_components.utils import Tagger

from pulumi import AssetArchive, ComponentResource, FileArchive, ResourceOptions
import pulumi_aws as aws
from pulumi_aws.lambda_ import Function, FunctionEnvironmentArgs, Permission

from data_engineering_pulumi_components.aws import get_databases


class GetDatabasesFunction(ComponentResource):
    def __init__(
        self,
        name: str,
        tagger: Tagger,
        bucket_name: str,
        bucket_prefix: str,
        account_id: str,
        region: str,
        api: aws.apigateway,
        resource_path: str,
        lambda_role_arn: str,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """
        Provide a Lambda function that gets a list of all the databases in a bucket.
        Parameters
        ----------
        name : str
            The name of the resource.
        tagger : Tagger
            A tagger resource.
        bucket_name : str, Bucket
            The bucket to read data from.
        bucket_prefix : str,
            Sub folder the to read from.
        account_id : str,
            The account number for creation of resources.
        region : str,
            Region the resources to be created.
        api : aws.apigateway,
            The API which uses the lambda to read the list of databases.
        resource_path : str,
            API resource path.
        lambda_role_arn : str
            Lambda role arn for the function to use. Should have ListBucket permission.
        opts : Optional[ResourceOptions]
            Options for the resource. By default, None.
        """
        super().__init__(
            t="data-engineering-pulumi-components:aws:GetDatabasesFunction",
            name=name,
            props=None,
            opts=opts,
        )

        self._bucketname = bucket_name
        self._bucket_prefix = bucket_prefix
        self._region = region
        self._account_id = account_id
        self._resource_path = resource_path
        self._lambda_role_arn = lambda_role_arn

        self.function = Function(
            resource_name=f"{name}-function",
            code=AssetArchive(
                assets={
                    ".": FileArchive(
                        path=str(Path(get_databases.__file__).absolute().parent)
                    )
                }
            ),
            description="Create list of databases in a bucket.",
            role=self._lambda_role_arn,
            handler="get_databases.handler",
            environment=FunctionEnvironmentArgs(
                variables={
                    "bucket_name": f"{self._bucketname}",
                    "prefix": f"{self._bucket_prefix}",
                }
            ),
            runtime="python3.8",
            tags=tagger.create_tags(f"{name}-get-databases"),
            timeout=300,
            opts=ResourceOptions(parent=self),
        )

        self._permission = Permission(
            resource_name=f"{name}-get-databases-permission",
            principal="apigateway.amazonaws.com",
            action="lambda:InvokeFunction",
            function=self.function.arn,
            source_arn=api.id.apply(
                lambda api_id: f"arn:aws:execute-api:{self._region}:"
                + f"{self._account_id}:{api_id}/*/GET/{self._resource_path}"
            ),
            opts=ResourceOptions(parent=self.function),
        )
