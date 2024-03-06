output "codebuild_project_name" {
  description = "Name of the CodeBuild project"
  value       = aws_codebuild_project.main.name
}

output "artifact_bucket" {
  description = "S3 bucket used for pipeline artifacts"
  value       = aws_s3_bucket.artifacts.bucket
}

output "pipeline_name" {
  description = "Name of the CodePipeline"
  value       = aws_codepipeline.main.name
}
