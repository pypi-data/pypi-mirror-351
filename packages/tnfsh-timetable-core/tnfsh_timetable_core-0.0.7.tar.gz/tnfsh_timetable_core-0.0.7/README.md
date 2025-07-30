# TNFSH Timetable Core

A Python package for handling TNFSH (Tainan First Senior High School) timetables.

## Features

- Fetch timetables from TNFSH website
- Parse and manipulate timetable data
- Export timetables in various formats (CSV, JSON, ICS)
- Cache support for better performance

## usage

統一 from tnfsh_time_table_core import TNFSHTIMETABLECORE。
因為奇怪的原因 安裝完以後請用底線而不是-

第一次裝會自動跑一次cache

## Installation

```bash
pip install tnfsh-timetable-core
```

## Quick Start

```python
from tnfsh_timetable_core import TNFSHTimetableCore

# Create an instance
core = TNFSHTimetableCore()

# Get timetable for class 307
timetable = await core.fetch_timetable("307")

# Get index of all available timetables
index = core.fetch_index()
```

## Development

1. Clone the repository
2. Create and activate virtual environment
3. Install dependencies:
   ```bash
   uv pip install --editable .
   ```
4. Run tests:
   ```bash
   pytest
   ```

## License

See [LICENSE](LICENSE) file for details.

