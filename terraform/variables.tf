
variable "function_name" {
  description = "name for the lambda function"
  default = "ecstatic"
  type = "string"
}

variable "description" {
  description = "description for the lambda function"
  default = "monitor and update ecs agents"
  type = "string"
}

variable "webhook_url" {
  description = "webhook for sending slack-style notifications"
  default = ""
  type = "string"
}

variable "s3_bucket" {
  description = "S3 bucket with the initial lambda zip resides"
  default = "code.firstlook.media"
  type = "string"
}

variable "s3_key" {
  description = "S3 key for the initial lambda zip"
  default = "ecstatic/ecstatic.zip"
  type = "string"
}

variable "subnet_ids" {
  description = "list of subnet ids for the function"
  type = "list"
}

variable "security_group_ids" {
  description = "list of security group ids for the function"
  type = "list"
}

