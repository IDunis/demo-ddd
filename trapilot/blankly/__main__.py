import trapilot.blankly.deployment.new_cli
from trapilot.blankly.persistence.models import init_db

if __name__ == "__main__":
    init_db("sqlite:///tradesv3.sqlite")
    trapilot.blankly.deployment.new_cli.main()
