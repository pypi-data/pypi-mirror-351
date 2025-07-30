# web_etl

**web_etl** is an end-to-end ETL (Extract, Transform, Load) Python package designed for extracting tables from HTML web pages, transforming the data, and loading it into various destinations such as CSV, Excel, or PostgreSQL databases.

---

## Features

- **Extract:** Retrieve tables from HTML web pages using BeautifulSoup and pandas.
- **Transform:** Clean and manipulate your data with functions for dropping columns, renaming columns, converting data types, handling missing values, and more.
- **Load:** Save your transformed data to CSV, Excel, or directly to a PostgreSQL database.

---

## Installation

Install from PyPI:
```sh
pip install web_etl
```

Or install from source:
```sh
git clone https://github.com/yourusername/web_etl.git
cd web_etl
pip install .
```

---

## Requirements

- pandas
- requests
- beautifulsoup4
- sqlalchemy

---

## Usage

```python
from web_etl.extract import Extract
from web_etl.transform import Transformer
from web_etl.load import Load

# Extract table from HTML page
df = Extract.from_html_table("https://example.com/table.html")

# Transform data
df = Transformer.drop_columns(df, columns_to_drop=['LOW RANGE', 'HIGH RANGE'])
df = Transformer.rename_columns(df, {'old_name': 'new_name'})
df = Transformer.to_lowercase(df)

# Load data to CSV
Load.to_csv(df, "output.csv")

# Load data to PostgreSQL
Load.to_postgres(df, "table_name", "postgresql://user:password@host:port/dbname")
```

---

## License

MIT

---

## Author

Rose Wabere
