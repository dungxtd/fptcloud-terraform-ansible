# Terraform backend configuration
# Uncomment and configure for remote state storage

# terraform {
#   backend "s3" {
#     bucket = "your-terraform-state-bucket"
#     key    = "terraform/state"
#     region = "us-east-1"
#   }
# }

# Local backend (default)
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
