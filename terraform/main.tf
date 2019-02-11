
//
// aws_lambda_function
//

resource "aws_lambda_function" "this" {

  function_name = "${var.function_name}"
  description   = "${var.description}"

  role = "${aws_iam_role.this.arn}"

  runtime = "python3.7"
  handler = "ecstatic.lambda_handler"

  s3_bucket = "${var.s3_bucket}"
  s3_key    = "${var.s3_key}"

  vpc_config {
    subnet_ids         = [ "${var.subnet_ids}" ]
    security_group_ids = [ "${var.security_group_ids}" ]
  }

  environment {
    variables = {
      ECSTATIC_WEBHOOK_URL = "${var.webhook_url}"
    }
  }

  lifecycle {
    ignore_changes = [ "description", "environment", "handler", "runtime", "timeout", "memory_size" ]
  }
}

//
// aws_iam_role
//

resource "aws_iam_role" "this" {
  name               = "${var.function_name}_lambda"
  assume_role_policy = "${data.aws_iam_policy_document.assume_role_policy.json}"
}

data "aws_iam_policy_document" "assume_role_policy" {

  statement {
    actions = [ "sts:AssumeRole" ]
    principals {
      type        = "Service"
      identifiers = [ "lambda.amazonaws.com" ]
    }
  }

  statement {
    actions = [ "sts:AssumeRole" ]
    principals {
      type        = "Service"
      identifiers = [ "events.amazonaws.com" ]
    }
  }

}

//
// aws_iam_role_policy
//

resource "aws_iam_role_policy" "this" {
  name   = "${var.function_name}_lambda"
  role   = "${aws_iam_role.this.id}"
  policy = "${data.aws_iam_policy_document.iam_role_policy.json}"
}

data "aws_iam_policy_document" "iam_role_policy" {
  statement {
    sid = "1"
    actions = [
      "ecs:Describe*",
      "ecs:List*",
      "ecs:UpdateContainerAgent"
    ]
    resources = [
      "arn:aws:ecs:*"
    ]
  }
  statement {
    sid = "2"
    actions = [
      "ecs:ListClusters"
    ]
    resources = [
      "*"
    ]
  }
}

//
// aws_iam_role_policy_attachment
//

resource "aws_iam_role_policy_attachment" "this" {
  role       = "${aws_iam_role.this.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

//
// cloudwatch events
//

resource "aws_cloudwatch_event_rule" "hourly" {
  name                = "${var.function_name}_hourly"
  description         = "trigger ${var.function_name} every hour"
  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "hourly" {
  target_id = "${var.function_name}_hourly"
  rule      = "${aws_cloudwatch_event_rule.hourly.name}"
  arn       = "${aws_lambda_function.this.arn}"
  input     = "{}"
}

resource "aws_lambda_permission" "hourly" {
  statement_id  = "${var.function_name}_hourly"
  principal     = "events.amazonaws.com"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.this.function_name}"
  source_arn    = "${aws_cloudwatch_event_rule.hourly.arn}"
}
