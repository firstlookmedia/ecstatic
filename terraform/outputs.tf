
output "function_arn" {
  description = "the arn of the lambda function"
  value = "${aws_lambda_function.this.arn}"
}
