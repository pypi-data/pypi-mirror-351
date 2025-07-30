import random
import subprocess
import json
from typing import List, Optional

import requests
from mcp.server.fastmcp import FastMCP

from .tools.nuclei import run_nuclei
from .tools.ffuf import run_ffuf
from .tools.wfuzz import run_wfuzz
from .tools.sqlmap import run_sqlmap
from .tools.nmap import run_nmap
from .tools.hashcat import run_hashcat
from .tools.httpx import run_httpx
from .tools.subfinder import run_subfinder
from .tools.tlsx import run_tlsx
from .tools.xsstrike import run_xsstrike
from .tools.amass import amass_wrapper
from .tools.dirsearch import dirsearch_wrapper
from .tools.ipinfo import run_ipinfo
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")

def register_tools(mcp, selected_tools, verbose=False):
    if "nuclei" in selected_tools:
        @mcp.tool()
        def nuclei(target: str, templates: Optional[List[str]] = None, severity: Optional[str] = None, output_format: str = "json") -> str:
            if verbose: print("Registrando nuclei_scan")
            return run_nuclei(target, templates, severity, output_format)

    if "ffuf" in selected_tools:
        @mcp.tool()
        def ffuf(url: str, wordlist: str, filter_code: Optional[str] = "404") -> str:
            if verbose: print("Registrando ffuf")
            return run_ffuf(url, wordlist, filter_code)

    if "wfuzz" in selected_tools:
        @mcp.tool()
        def wfuzz(url: str, wordlist: str, filter_code: Optional[str] = "404") -> str:
            if verbose: print("Registrando wfuzz")
            return run_wfuzz(url, wordlist, filter_code)

    if "sqlmap" in selected_tools:
        @mcp.tool()
        def sqlmap(url: str, risk: Optional[int] = 1, level: Optional[int] = 1) -> str:
            if verbose: print("Registrando sqlmap")
            return run_sqlmap(url, risk, level)

    if "nmap" in selected_tools:
        @mcp.tool()
        def nmap(target: str, ports: Optional[str] = None, scan_type: Optional[str] = "sV") -> str:
            if verbose: print("Registrando nmap")
            return run_nmap(target, ports, scan_type)

    if "hashcat" in selected_tools:
        @mcp.tool()
        def hashcat(hash_file: str, wordlist: str, hash_type: str) -> str:
            if verbose: print("Registrando hashcat")
            return run_hashcat(hash_file, wordlist, hash_type)

    if "httpx" in selected_tools:
        @mcp.tool()
        def httpx(urls: List[str], status_codes: Optional[List[int]] = None) -> str:
            if verbose: print("Registrando httpx")
            return run_httpx(urls, status_codes)

    if "subfinder" in selected_tools:
        @mcp.tool()
        def subfinder(domain: str, recursive: bool = False) -> str:
            if verbose: print("Registrando subfinder")
            return run_subfinder(domain, recursive)

    if "tlsx" in selected_tools:
        @mcp.tool()
        def tlsx(host: str, port: Optional[int] = 443) -> str:
            if verbose: print("Registrando tlsx")
            return run_tlsx(host, port)

    if "xsstrike" in selected_tools:
        @mcp.tool()
        def xsstrike(url: str, crawl: bool = False) -> str:
            if verbose: print("Registrando xsstrike")
            return run_xsstrike(url, crawl)

    if "ipinfo" in selected_tools:
        @mcp.tool()
        def ipinfo(ip: Optional[str] = None) -> str:
            if verbose: print("Registrando ipinfo")
            return run_ipinfo(ip)

    if "amass" in selected_tools:
        @mcp.tool()
        def amass(domain: str, passive: bool = True) -> str:
            if verbose: print("Registrando amass_wrapper")
            return amass_wrapper(domain=domain, passive=passive)

    if "dirsearch" in selected_tools:
        @mcp.tool()
        def dirsearch(url: str, extensions: Optional[List[str]] = None, wordlist: Optional[str] = None) -> str:
            if verbose: print("Registrando dirsearch_wrapper")
            return dirsearch_wrapper(url, extensions, wordlist)


if __name__ == "__main__":
    mcp.run(transport="stdio")
