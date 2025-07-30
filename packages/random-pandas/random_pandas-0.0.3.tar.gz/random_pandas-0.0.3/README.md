# Random Pandas

A Python package for generating random pandas DataFrame objects and other random functionalities, useful for machine learning benchmarking and testing.

## Features

- Generate DataFrames with random numbers of rows and columns.
- Columns can be of various data types (integer, float, boolean, string, datetime).
- Numeric columns can follow different random distributions (uniform, normal) with underlying patterns.
- Introduce controlled randomness suitable for benchmarking machine learning algorithms.

## Installation

```bash
pip install random-pandas
```

## Usage

```python
from random_pandas import generate_random_dataframe

# Generate a random DataFrame
df = generate_random_dataframe()
print(df.head())

# Generate a random DataFrame with specific number of rows
df_rows = generate_random_dataframe(n_rows=100)
print(df_rows.info())

# Generate a random DataFrame with specific number of columns
df_cols = generate_random_dataframe(n_cols=5)
print(df_cols.info())
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
