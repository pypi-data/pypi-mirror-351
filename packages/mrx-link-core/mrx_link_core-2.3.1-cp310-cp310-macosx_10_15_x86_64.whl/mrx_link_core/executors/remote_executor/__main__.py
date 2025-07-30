#
#  MAKINAROCKS CONFIDENTIAL
#  ________________________
#
#  [2017] - [2024] MakinaRocks Co., Ltd.
#  All Rights Reserved.
#
#  NOTICE:  All information contained herein is, and remains
#  the property of MakinaRocks Co., Ltd. and its suppliers, if any.
#  The intellectual and technical concepts contained herein are
#  proprietary to MakinaRocks Co., Ltd. and its suppliers and may be
#  covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law. Dissemination
#  of this information or reproduction of this material is
#  strictly forbidden unless prior written permission is obtained
#  from MakinaRocks Co., Ltd.
#
import argparse
import sys
import uuid

from .executor import MRXLinkRemoteComponentExecutor


def main() -> int:
    """Main."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="MRXLinkRemoteExecutor arguments.")
    parser.add_argument(
        "--backend",
        type=str,
        default="redis://localhost:6379",
        required=True,
        help="The result store backend URL",
        dest="backend",
    )
    parser.add_argument(
        "--broker",
        type=str,
        default="redis://localhost:6379",
        required=True,
        help="URL of the default broker used",
        dest="broker",
    )
    parser.add_argument(
        "--loglevel",
        type=str,
        default="INFO",
        required=False,
        choices=["INFO", "DEBUG"],
        help="Log level",
        dest="loglevel",
    )

    parsed_args: argparse.Namespace = parser.parse_args()

    try:
        identifier: str = str(uuid.uuid4())

        remote_executor: MRXLinkRemoteComponentExecutor = MRXLinkRemoteComponentExecutor(
            identifier=identifier,
            name=identifier,
            backend=parsed_args.backend,
            broker=parsed_args.broker,
        )

        remote_executor.run_executor(loglevel=parsed_args.loglevel)
    except (Exception, KeyboardInterrupt) as exp:  # pylint: disable=broad-except
        print(str(exp), file=sys.stderr)
        return 1

    return 0


sys.exit(main())
