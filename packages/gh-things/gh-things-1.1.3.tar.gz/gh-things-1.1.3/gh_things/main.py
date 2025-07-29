import argparse
import json
import subprocess

PARSER = argparse.ArgumentParser(description='')
parsers = PARSER.add_subparsers(dest='command', required=True)
repo_parser = parsers.add_parser('repo', help='')
repo_parser.add_argument("repo", nargs="?")


def main():
    args = PARSER.parse_args()

    match args.command:
        case 'repo':
            main_repo(args)

        case value:
            raise ValueError(value)





def main_repo(args):
    match args.repo:
        case None:
            data = json.loads(subprocess.check_output(["gh", "repo", "view", "--json", "name", "--json", "owner"]).decode('utf8'))
            name = data["name"]
            owner = data["owner"]["login"]
        case value:
            raise ValueError(value)


    print(json.dumps(call(f"repos/{owner}/{name}"), indent=2))


def call(path):
    output = subprocess.check_output(["gh", "api", path])
    return json.loads(output.decode('utf-8'))
