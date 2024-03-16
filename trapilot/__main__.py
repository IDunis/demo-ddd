import trapilot.deployment.new_cli

from trapilot.persistence.models import init_db

if __name__ == '__main__':
    init_db("sqlite:///tradesv3.sqlite")
    trapilot.deployment.new_cli.main()
