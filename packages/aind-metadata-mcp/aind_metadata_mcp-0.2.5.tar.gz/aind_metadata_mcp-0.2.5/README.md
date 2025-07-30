# AIND Metadata access MCP server

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
![Interrogate](https://img.shields.io/badge/interrogate-94.4%25-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=codecov)
![Python](https://img.shields.io/badge/python->=3.11-blue?logo=python)

## Instructions for use in MCP clients

JSON Config files to add MCP servers in clients should be structured like this
```bash
{
    "mcpServers": {

    }
}
```
Insert the following lines into the mcpServers dictionary
```bash

"aind_data_access": {
    "command": "uvx",
    "args": ["aind-metadata-mcp"]
}

```

### Claude Desktop App
- Click the three lines at the top left of the screen.
- File > Settings > Developer > Edit config

### Cline in VSCode
- Ensure that Cline is downloaded to VScode
- Click the three stacked rectangles at the top right of the Cline window
- Installed > Configure MCP Servers

