# Collective

**Collective** is a versatile Python package that brings powerful, C#-like collection and query capabilities to your projects. It provides intuitive, fluent interfaces for managing and transforming data collections with ease.

## What's New?

The latest version of Collective includes:
- **Modification Tracking:** Each modifying operation increments the `modification_count` attribute for precise operation auditing.
- **Expanded API:** Additional methods for data transformations (`FlatMap`, `Distinct`, `Fuse`, etc.).
- **Metadata Enrichment:** The `Metadata` method now includes `ModificationCount`, `LifetimeSeconds`, and more insights.

## Installation
```bash
pip install pz-collective
```

_(Replace this with your actual installation command, e.g., if you’re hosting it on GitHub or PyPI)_

## Quick Example
```python
from pz_collective import Collection, Queryable

# Create a collection
data = Collection(1, 2, 3, 4, 5)

# Use Collection methods
data.Add(6).Remove(3).Insert(0, 0).Sort().Reverse()
print(data.ToList())  # [6, 5, 4, 2, 1, 0]

# Metadata inspection
print(data.Metadata())  # includes 'ModificationCount' and more!

# Query with Queryable
result = Queryable(data).Where(lambda x: x % 2 == 0).Select(lambda x: x * 10).ToCollection()
print(result.ToList())  # [60, 40, 20, 0]
```

## Features

✅ Add, remove, and manage items easily  
✅ Track modifications (`modification_count`)  
✅ Flexible slicing and index-based access  
✅ LINQ-like querying with filtering, mapping, sorting  
✅ Metadata insights (like type distribution, modification history)  
✅ Advanced data manipulations (reduce, zip, flatten, etc.)  
✅ Fluent, chainable interface for expressive data handling  

## License

MIT License

---

Let me know if you’d like to expand it further with badges, contributing guidelines, or examples of complex usage! 🚀
