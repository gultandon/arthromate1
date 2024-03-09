terraform {
  backend "s3" {
    bucket       = "my-terraform-state-bucket-gul1234"
    key          = "backend/terraform.tfstate"
    region       = "ap-south-1"
    use_lockfile = true
    encrypt      = true
  }
}
