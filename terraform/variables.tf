
variable "function_name" {
  default = "ecstatic"
}

variable "description" {
  default = "monitor and update ecs agents"
}

variable "subnet_ids" {
  type = "list"
}

variable "security_group_ids" {
  type = "list"
}

variable "s3_bucket" {
  default = "code.firstlook.media"
}

variable "s3_key" {
  default = "ecstatic/ecstatic.zip"
}
