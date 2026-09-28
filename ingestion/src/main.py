from pathlib import Path

import yaml

def load_config():
    config_path = Path("config/sources.yml")

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def main():
    config = load_config()

    project = config["project"]
    economic = config["economic"]
    weather = config["weather"]

    print("Kenya Economic & Weather Pipeline")
    print("***********************************")
    print(f"Country: {project['country']}")
    print(f"Economic indicators: {len(economic['indicators'])}")
    print(f"Weather locations: {len(weather['locations'])}")
    print(f"Weather variables: {len(weather['variables'])}")


if __name__ == "__main__":
    main()