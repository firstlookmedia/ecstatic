
# Ecstatic

An AWS Lambda for updating and monitoring ECS agents

## Quick Install

module "ecstatic" {
  source = "git@github.com:firstlookmedia/ecstatic//terraform"
  subnet_ids = [ "${split( ",", module.network.private_subnet_ids ) }" ]
  security_group_ids = [ "${module.network.aws_security_group.allow_all_vpc.id}" ]
}


## Environment Variables

* ECSTATIC_LOG_LEVEL
    * Log level passed to Python logging facility
    * See more: https://docs.python.org/3/library/logging.html#logging-levels
    * Defaults to `INFO`

* ECSTATIC_WEBHOOK_URL
    * (Optional) Slack-style webhook for update and error notifications
    * Messages are not sent if this is unset

