# gstpy Module

The `gstpy` module provides an easy and flexible way to calculate GST (Goods and Services Tax) for various item formats such as lists, dictionaries, and integers. It supports both exclusive and inclusive tax calculations and presents the output in multiple formats: list, dictionary, or a well-formatted table using the tabulate package.

## Installation

You can install this module using pip:
&nbsp;

```bash
pip install gstpy
```
# GST Class
&nbsp;
```from gstpy import GST```
&nbsp;

## Constructor
&nbsp;
```GST(items=0, rate=18, mode="exclusive")```

Initializes a GST object.
&nbsp;

### Parameters:
- **items**: (int, list, dict) — Item(s) to calculate GST on. Defaults to 0.
- **rate**: (int, float) — GST rate. Defaults to 18.
- **mode**: (str) — Either "exclusive" or "inclusive" to specify GST type. Defaults to "exclusive".
&nbsp;

### Behavior:
- Automatically processes the provided items if valid.
- Supports multiple formats:
  - List of integers or tuples/lists
  - Dictionary with item names as keys and prices or [price, quantity] as values
  - Single integer price
&nbsp;

## Methods
&nbsp;

### 1. exclusive
&nbsp;
Calculates GST using the exclusive method (GST is added to the price).
&nbsp;

#### Parameters:
- **items**: Items to calculate GST for (int, list, dict)
- **rate**: GST rate (int, float)
- **out**: Output format - "list", "dict", or "table"
&nbsp;

#### Returns:
- List or dictionary of results (if out is "list" or "dict")
- Table printed on screen (if out is "table")
&nbsp;

#### Format Supported:
- Single price (int)
- List of prices (list)
- List of [item_name, price]
- List of [item_name, price, qty]
- Dict of {item_name: price} or {item_name: [price, qty]}
&nbsp;

### 2. inclusive
&nbsp;

Calculates GST using the inclusive method (price already includes GST).
&nbsp;

#### Parameters:
- **items**: Items to calculate GST for (int, list, dict)
- **rate**: GST rate (int, float)
- **out**: Output format - "list", "dict", or "table"
&nbsp;

#### Returns:
- List or dictionary of results (if out is "list" or "dict")
- Table printed on screen (if out is "table")
&nbsp;

#### Format Supported:
- Single price (int)
- List of prices (list)
- List of [item_name, price]
- List of [item_name, price, qty]
- Dict of {item_name: price} or {item_name: [price, qty]}
&nbsp;

## Special Functions
&nbsp;

- `ingst(total_price, gst_rate)` → returns only the GST amount
- `exgst(base_price, gst_rate)` → returns only the GST amount

## Documentation
&nbsp;

[![Download Documentation](https://img.shields.io/badge/Download%20Documentation-blue.svg)](https://drive.google.com/file/d/1lzf739rKKWUfgOODhblDckchwvmaKUYR/view?usp=sharing)
&nbsp;

You can download the full documentation for the `gstpy` module by clicking the button above.

## Author
&nbsp;

Developed by: Ankush  
- [LinkedIn Profile](https://www.linkedin.com/in/ankush-dhingraa/)  
- [GitHub Profile](https://github.com/ankush-dhingraa)  
&nbsp;

For any issues or bug reports, please [open an issue on GitHub.](https://github.com/ankush-dhingraa/gstpy/issues)