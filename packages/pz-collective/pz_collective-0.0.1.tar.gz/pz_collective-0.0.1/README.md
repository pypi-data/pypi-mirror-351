# Collective

**Collective** is a versatile Python package that brings powerful, C#-like collection and query capabilities to your projects.

It includes two main classes:

- **Collection**: a flexible container for your data, supporting operations like sorting, filtering, mapping, reducing, and more.
- **Queryable**: a fluent querying engine built on top of Collection, enabling complex, SQL-like data transformations and retrievals.

## Installation

```bash
pip install pz-collective
```
(Replace this with your actual installation command, e.g., if you’re hosting it on GitHub or PyPI)

## Quick Example

```py
from pz_collective import Collection, Queryable

# Create a collection
data = Collection(1, 2, 3, 4, 5)

# Use Collection methods
data.Add(6).Remove(3)
print(data.ToList())  # [1, 2, 4, 5, 6]

# Query with Queryable
result = Queryable(data).Where(lambda x: x % 2 == 0).Select(lambda x: x * 10).ToCollection()
print(result.ToList())  # [20, 40, 60]
```

## Features

- Add, remove, and manage items easily
- LINQ-like querying with filtering, mapping, and sorting
- Advanced data manipulations (reduce, zip, flatten, etc.)
- Fluent, chainable interface

## License

MIT License