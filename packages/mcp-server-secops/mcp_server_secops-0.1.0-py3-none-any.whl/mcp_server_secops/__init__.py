

from .server import mcp, register_tools

def main():
    import argparse

    parser = argparse.ArgumentParser(description="MCP SecOps Server (stdio only)")
    parser.add_argument(
        "--tools",
        nargs="+",
        default=[
            "nmap", "sqlmap", "ffuf", "wfuzz", "nuclei", "httpx", "hashcat",
            "subfinder", "tlsx", "xsstrike", "amass", "dirsearch", "ipinfo"
        ],
        help="Herramientas a registrar (ej: nmap sqlmap)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra información de depuración"
    )

    args = parser.parse_args()

    register_tools(mcp, args.tools, args.verbose)

    if args.verbose:
        print("[INFO] Iniciando servidor MCP en stdio...")

    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()