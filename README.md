
# Ecstatic

An AWS Lambda for updating and monitoring ECS agents.

## How It Works

Each time ecstatic's default handler – `lambda_handler()` or `main()` – is called, the script does the following:

1. Loops through each ECS cluster one-by-one
2. Loops through each container instance in the current cluster
3. If an ECS agent is in a disconnect state or if a previous attempt to update the agent failed:
    - A warning will be logged and the cluster will not be updated
4. If all ECS agents in a cluster are healthy:
    - [UpdateContainerAgent](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_UpdateContainerAgent.html) will be called one agent at a time
5. If a call to `UpdateContainerAgent` is accepted – because an agent is out-of-date:
    - Further updates in the current cluster will be delayed until later runs
    - This is to affect an incremental roll-out of agent updates across a cluster

Also, if an agent update request is accepted or if an agents is in an error state, a [Slack-style](https://api.slack.com/incoming-webhooks) message will be sent to `ECSTATIC_WEBHOOK_URL`, if set.

## Using Terraform

Add and edit the following module block to your [AWS provider](https://www.terraform.io/docs/providers/aws/) enabled [Terraform](https://www.terraform.io/) configs:

```
module "ecstatic" {
  source             = "git@github.com:firstlookmedia/ecstatic//terraform?ref=v0.0.1"
  subnet_ids         = [ "${aws_subnet.vpc_subnet_1.id}", "${aws_subnet.vpc_subnet_2.id}" ]
  security_group_ids = [ "${aws_security_group.vpc_allow_all.id}" ]
  webhook_url        = "https://hooks.slack.com/services/JGKDLKTJDKG/FJSKFJGJKSKG/GJDKSKGJ"
}
```

The lambda is configured to require a VPC, therefore, you'll need to edit the following variables in the block:

1. `subnet_ids` – at least one VPC subnet must be specified
2. `security_group_ids` – the security group specified must allow network access to target ECS clusters
3. `webhook_url` – _(optional)_ should be set or removed to enable or disable webhook messages, respectively
    - See Slack's [Incoming Webhooks](https://api.slack.com/incoming-webhooks) for more information.

Once the module block is added and edited, run:

```
terraform init --upgrade
terraform apply --target=module.ecstatic
```

This will create the following:

1. `aws_lambda_function` named `ecstatic`
1. `aws_iam_role` named `ecstatic_lambda`
1. `aws_iam_role_policy` named `ecstatic_lambda`
1. `aws_iam_role_policy_attachment`
    - Attaches the lambda IAM role to `service-role/AWSLambdaVPCAccessExecutionRole`

The initial Terraform `apply` will pull the most recent released version of `ecstatic` from S3:

* e.g. https://s3.amazonaws.com/code.firstlook.media/ecstatic/archive/ecstatic-v0.0.1.zip

## Using the Command-Line

Ecstatic can also be run manually from the command-line.

1\. Install prerequisites

We use [Homebrew](https://brew.sh/), [PyEnv](https://github.com/pyenv/pyenv), and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv).  The latter two tools are great for managing multiple installed versions of Python and required modules.

```
$ brew install pyenv pyenv-virtualenv
$ pyenv install 3.7.1
$ pyenv virtualenv 3.7.1 ecstatic
```

2\. Clone the repo and install required modules

```
$ git clone git@github.com:firstlookmedia/ecstatic.git
$ cd ./ecstatic
$ pyenv local ecstatic
$ pip install -r requirements.txt
```

3\. Run `ecstatic.py`

```
$ AWS_PROFILE=ecs-admin ./ecstatic.py
```

You can learn how to configure your AWS credentials to work with [Boto3](https://github.com/boto/boto3) here: [Credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)

#### aws-profile-gpg

Additionally, we recommend using [aws-profile-gpg](https://github.com/firstlookmedia/aws-profile-gpg), a tool that generates role-specific IAM access tokens while safely storing your secret access keys in a [GPG](https://www.gnupg.org/) encrypted file.

```
# run ecstatic using aws-profile-gpg
$ AWS_PROFILE=ecs-admin aws-profile-gpg ./ecstatic.py
```

## Environment Variables

The following environment variables are used by `ecstatic`:

* ECSTATIC_LOG_LEVEL
    * Log level passed to Python logging facility
    * See more: https://docs.python.org/3/library/logging.html#logging-levels
    * Defaults to `INFO`

* ECSTATIC_WEBHOOK_URL
    * (Optional) Slack-style webhook for update and error notifications
    * Messages are not sent if this is unset

## Future Enhancements

We have a few ideas for enhancements, including

- Checking for available [Docker](https://www.docker.com) updates
- Comparing the actual and target AMI versions of container instances in [Auto Scaling Groups](https://docs.aws.amazon.com/autoscaling/ec2/userguide/AutoScalingGroup.html)
- Including or skipping container instances based on a [Tags](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_Tags.html)

If you have ideas or feedback, feel free to send feedback via [GitHub Issues](https://github.com/firstlookmedia/ecstatic/issues).

## Resources

* Amazon ECS Container Agent Versions
    - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/container_agent_versions.html

