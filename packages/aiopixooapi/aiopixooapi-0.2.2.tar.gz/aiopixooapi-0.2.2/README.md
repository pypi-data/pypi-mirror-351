
# AioPixooAPI

A Python library for interacting with Divoom Pixoo devices and the Divoom online API.

## Installation

Install the library using pip:

```bash
pip install aiopixooapi
```

## Usage

### Pixoo64 (Device API)

The `Pixoo64` class is used to interact with a Pixoo64 device on your local network.

```python
import asyncio
from aiopixooapi.pixoo64 import Pixoo64

async def main():
    async with Pixoo64("192.168.1.100") as pixoo:
        # Reboot the device
        response = await pixoo.sys_reboot()
        print(response)

        # Get all settings
        settings = await pixoo.get_all_settings()
        print(settings)

asyncio.run(main())
```

### Divoom (Online API)

The `Divoom` class is used to interact with the Divoom online API.

```python
import asyncio
from aiopixooapi.divoom import Divoom

async def main():
    async with Divoom() as divoom:
        # Get dial types
        dial_types = await divoom.get_dial_type()
        print(dial_types)

        # Get dial list for a specific type and page
        dial_list = await divoom.get_dial_list("Social", 1)
        print(dial_list)

asyncio.run(main())
```

## Development
### Setup
To set up the development environment, clone the repository, create a virtual environment and install the required packages

```bash
pip install -e .
pip install -e .[test]
```

## Running Tests

To run the tests using pytest, execute:

```bash
pytest
```

Or to run tests in a specific file:

```bash
pytest tests/test_pixoo64.py
```

## Documentation

http://docin.divoom-gz.com/web/#/5/23

### Sources used

#### Divoom

* https://divoom.com/apps/help-center#hc-pixoo64developeropen-sourcesdkapiopen-source

That gives us:

* http://doc.divoom-gz.com/web/#/12?page_id=89

Where the contact page:

* http://doc.divoom-gz.com/web/#/12?page_id=143

Send us to

* http://docin.divoom-gz.com/web/#/5/23

OLDER REFERENCES

* http://doc.divoom-gz.com/web/#/12
* http://doc.divoom-gz.com/web/#/7
* http://doc.divoom-gz.com/web/#/5

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the LICENSE file for details.
