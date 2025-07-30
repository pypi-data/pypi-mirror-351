# pytelmbot

A collection of utilities to use for automated embedded testing

Designed with pyserial in mind, but could be used for others

## Installation

Install the latest version of the package with:

```sh
pip install pytelmbot
```

## Examples

Example scripts are available in the source distribution or on GitHub.
To install the dependencies required to run the examples, use:

```sh
pip install pytelmbot[examples]
```

## SDWire

Support for managing files on a usb-connected SDWire device by [3MDEB](https://shop.3mdeb.com/shop/open-source-hardware/sdwire/)

### Usage

```python
from pytelmbot import SDWire

# List the available devices to find device-name
SDWire.list_devices() 

sdw = SDWire(device-name)

# Select the Test Server to access files
sdw.select_ts()

# Write a local file to the SD card at its root 
sdw.write_file('./testing/test.txt', '')        

# Copy a file on the SD card to another location
sdw.copy_file('test.txt', 'test_copy.txt')

# Rename a file on the SD card 
sdw.rename_file('test.txt', 'test_renamed.txt')

# Get a file from the SD card and store at a local path
sdw.get_file('test_renamed.txt', './testing')

# Delete a file on the SD card
sdw.delete_file('test_renamed.txt')

# Select the Device Under Test to give the device access
sdw.select_dut()                                 

# Close the SDWire connection
sdw.close()
```
