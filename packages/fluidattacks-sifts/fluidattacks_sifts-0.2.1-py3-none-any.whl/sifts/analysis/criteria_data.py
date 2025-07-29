import requests
import yaml

from sifts.config.settings import YAML_PATH

if not YAML_PATH.exists():
    response = requests.get(
        (
            "https://gitlab.com/fluidattacks/universe/-/raw/b225074bfeb542069e46a2bd952f"
            "d493ecc04830/common/criteria/src/vulnerabilities/data.yaml"
        ),
        timeout=30,
    )
    YAML_PATH.write_text(response.text)

handler = YAML_PATH.read_text()
CRITERIA_VULNERABILITIES: dict[str, dict[str, dict[str, str]]] = yaml.safe_load(handler)
