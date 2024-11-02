import boto3


class BaseAWSService:
    """Base class of AWS services"""

    service_name = None

    def __init__(self, region: str = "us-east-1", endpoint_url: str = None):
        """
        Constructor that initialize client
        :param  - region: An AWS region where the client will invoke
        :return - None
        """

        if self.service_name is None:
            raise Exception("The service_name must be set on service class")

        if region is None:
            raise Exception("Region cannot be None")

        self.region = region
        self.endpoint_url = endpoint_url
        self.account_id = self.__get_account_id()
        self._client = boto3.client(
            self.service_name, self.region, endpoint_url=self.endpoint_url
        )

    def __get_account_id(self) -> str:
        """
        Retrieve the AWS account id inside current environment credentials
        :return - Current AWS Account ID
        """

        return boto3.client("sts").get_caller_identity().get("Account")
