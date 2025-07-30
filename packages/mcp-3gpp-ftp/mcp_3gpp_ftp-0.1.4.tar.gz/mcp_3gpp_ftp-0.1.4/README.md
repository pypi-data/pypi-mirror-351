MCP 3GPP FTP Explorer
======================

A FastMCP-based server exposing tools to browse, download, and extract files from the 3GPP FTP site, plus utilities for Excel and Word documents.


Installation
------------

Install the package from PyPI:

```bash
pip install mcp-3gpp-ftp
```

Usage
-----

Start the MCP server and expose its tools on localhost:

```bash
mcp-3gpp-ftp
```

By default, the server listens on `http://localhost:8000/mcp`.  
Clients can then introspect and invoke tools via the MCP protocol:

- **list_directories(path: str) → List[str]**  
- **list_directories_files(path: str, file_pattern: str) → List[str]**  
- **crawl_ftp(path: str, depth: int, delay: float) → List[str]**  
- **list_files(path: str) → List[str]**  
- **list_excel_columns(file_url: str) → List[str]**  
- **filter_excel_columns_from_url(file_url: str, columns: List[str], filters: Dict[str,Any]) → List[Dict[str,Any]]**  
- **download_and_extract(file_url: str) → Dict[str,Any]**  
- **read_word_doc(doc_path: str) → Dict[str,Any]**  

Configuration
-------------

- Base FTP URL: `https://www.3gpp.org/ftp/`  
- Cache directory: created at runtime under `download_cache/`  
- Proxy settings: modify the `proxies` dict in `server.py` if necessary  

Author & License
----------------

**Author:** Hanwen Cao
**Email:** hanwen.cao@gmail.com
**License:** MIT  

