import argparse
from core import PortManagerCore

def main():
    parser = argparse.ArgumentParser(description="Portmaster CLI")
    parser.add_argument('--yes', '-y', action='store_true', help="Auto-confirm actions")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # List connections
    subparsers.add_parser('list', help="List active network connections")

    # Check port
    parser_check = subparsers.add_parser('check-port', help="Check if a port is in use")
    parser_check.add_argument('port', help="Port number to check")

    # Kill process
    parser_kill = subparsers.add_parser('kill', help="Kill a process by PID")
    parser_kill.add_argument('pid', help="PID to terminate")

    # Block port
    parser_block = subparsers.add_parser('block', help="Block a port using firewall")
    parser_block.add_argument('port', help="Port number to block")
    parser_block.add_argument('protocol', choices=['TCP', 'UDP'], help="Protocol to block")

    # Unblock port
    parser_unblock = subparsers.add_parser('unblock', help="Unblock a port")
    parser_unblock.add_argument('port', help="Port number to unblock")
    parser_unblock.add_argument('protocol', choices=['TCP', 'UDP'], help="Protocol to unblock")

    # Start server
    parser_start = subparsers.add_parser('start-server', help="Start a server on a port")
    parser_start.add_argument('port', help="Port number for server")
    parser_start.add_argument('protocol', choices=['TCP', 'UDP'], help="Protocol for server")

    # Stop server
    subparsers.add_parser('stop-server', help="Stop the running server")

    # Reserve port
    parser_reserve = subparsers.add_parser('reserve', help="Reserve a port for an executable")
    parser_reserve.add_argument('port', help="Port number to reserve")
    parser_reserve.add_argument('protocol', choices=['TCP', 'UDP'], help="Protocol to reserve")
    parser_reserve.add_argument('--exe-path', required=True, help="Path to executable")

    # Release port
    parser_release = subparsers.add_parser('release', help="Release a reserved port")
    parser_release.add_argument('port', help="Port number to release")

    # Save connections
    parser_save = subparsers.add_parser('save', help="Save connections to a file")
    parser_save.add_argument('filename', help="Output file path")

    args = parser.parse_args()
    core = PortManagerCore()

    if args.command == 'list':
        print(core.list_connections())

    elif args.command == 'check-port':
        output, rc = core.check_port(args.port)
        print(output)
        exit(rc)

    elif args.command == 'kill':
        output, rc = core.kill_process(args.pid, confirm=args.yes)
        print(output)
        exit(rc)

    elif args.command == 'block':
        output, rc = core.block_port(args.port, args.protocol, confirm=args.yes)
        print(output)
        exit(rc)

    elif args.command == 'unblock':
        output, rc = core.unblock_port(args.port, args.protocol, confirm=args.yes)
        print(output)
        exit(rc)

    elif args.command == 'start-server':
        output, rc = core.start_server(args.port, args.protocol, confirm=args.yes)
        print(output)
        exit(rc)

    elif args.command == 'stop-server':
        output, rc = core.stop_server(confirm=args.yes)
        print(output)
        exit(rc)

    elif args.command == 'reserve':
        output, rc = core.reserve_port(args.port, args.protocol, args.exe_path, confirm=args.yes)
        print(output)
        exit(rc)

    elif args.command == 'release':
        output, rc = core.release_port(args.port, confirm=args.yes)
        print(output)
        exit(rc)

    elif args.command == 'save':
        output, rc = core.save_connections(args.filename)
        print(output)
        exit(rc)

if __name__ == "__main__":
    main()