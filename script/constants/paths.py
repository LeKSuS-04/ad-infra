from pathlib import Path

CWD = Path.cwd()
ROOT = Path("/")

GENERATED_PATH = CWD / "generated"
TERRAFORM_PATH = CWD / "terraform"
ANSIBLE_PATH = CWD / "ansible"
RESOURCES_PATH = CWD / "resources"
INTERNAL_PATH = ROOT / "internal"
