import argparse
from deplacecli.commands import Command

def main():

    parser = argparse.ArgumentParser(description="adlcli - Azure Data Lake CLI with token")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments for all commands
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--token", required=True)
    
    # Download
    list_parser = subparsers.add_parser("download", parents=[common])
    list_parser.add_argument("--path", required=True)

    args = parser.parse_args()

    if args.command == "download":
        Command.download(args.token, args.path)