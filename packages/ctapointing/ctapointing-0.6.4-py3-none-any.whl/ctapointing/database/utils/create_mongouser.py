import argparse
import json

from ctapointing.database.mongodb import (
    create_mongo_config,
    create_mongo_account,
    read_mongo_config,
)

parser = argparse.ArgumentParser(description="Create an account for a new mongodb user")

parser.add_argument("user", type=str, help="user name")
parser.add_argument("passwd", type=str, help="password")

parser.add_argument(
    "--host",
    type=str,
    help="mongodb server host address",
)
parser.add_argument("--port", type=int, help="mongodb server port")
parser.add_argument(
    "--write-config", action="store_true", default=True, help="write JSON config file"
)
parser.add_argument(
    "--grant-write-access", action="store_true", help="grant write access for user"
)
parser.add_argument("--databases", type=str, nargs="*", help="databases")

args = parser.parse_args()

config = create_mongo_config(
    args.user,
    args.passwd,
    args.host,
    args.port,
    write_access=args.grant_write_access,
    databases=args.databases,
)


create_mongo_account(config)

if args.write_config:
    filename = args.user + ".mongorc"
    try:
        with open(filename, "w") as outfile:
            json.dump(config, outfile, indent=4)
    except Exception as e:
        print(f"problem in writing configuration to file {filename}: {e}")
