from .Collection import Collection

class Queryable:
    """
    Queryable Class
    
    The Queryable class provides a fluent interface for building queries on a Collection instance.
    It allows users to apply filtering, transformation, and sorting operations on a Collection, similar to SQL-like queries.
    The methods in this class return the modified instance of Queryable, allowing for method chaining.
    
    Methods included:
    - Where: Filters items based on a condition.
    - Select: Transforms items in the collection using a provided function.
    - OrderBy: Sorts items based on a key function.
    - Distinct: Removes duplicate items.
    - Limit: Limits the number of items in the collection.
    - Count: Returns the number of items in the collection.
    - ForEach: Executes an action for each item.
    - Reverse: Reverses the order of items.
    - Get: Retrieves an item at a given index with optional default value.
    - AsGenerator: Returns a generator for lazy evaluation.
    - ToCollection: Converts the internal list to a Collection instance.
    - __str__: Provides a string representation of the collection being managed.
    
    Usage:
    Queryable allows for advanced querying operations such as filtering, transformation, and sorting.
    It is used through the Query method on a Collection instance, supporting chained calls to build complex queries.
    """
    def __init__(self, *args):
        """
        Initializes a new instance of the Queryable class with a given collection, list, or any number of parameters.

        Parameters:
        *args: Can be a Collection, a list, or any number of individual elements.
        """
        if len(args) == 1:
            if isinstance(args[0], Collection):
                self.collection = args[0].ToList()
            elif isinstance(args[0], list):
                self.collection = args[0][:]
            else:
                self.collection = [args[0]]
        else:
            self.collection = list(args)

    def Where(self, condition, allow_none=False):
        """
        Filters the collection based on a provided condition.

        Parameters:
        condition (function): A function that returns True for items that should be included.
        allow_none (bool): If True, allows None values in the filtered collection.

        Returns:
        Queryable: The modified Queryable instance.
        """
        if not callable(condition):
            raise TypeError("The condition parameter must be a callable function.")
        self.collection = [item for item in self.collection if (item is not None or allow_none) and condition(item)]
        return self

    def Select(self, func):
        """
        Applies a transformation function to each item in the collection.

        Parameters:
        func (function): A function to apply to each item.

        Returns:
        Queryable: The modified Queryable instance.
        """
        if not callable(func):
            raise TypeError("The func parameter must be a callable function.")
        self.collection = [func(item) for item in self.collection]
        return self

    def OrderBy(self, key=None, reverse=False, comparer=None):
        """
        Sorts the collection based on a key function or custom comparer.

        Parameters:
        key (function): A function that serves as a key for sorting.
        reverse (bool): If True, sorts in descending order.
        comparer (function): A custom comparison function for sorting.

        Returns:
        Queryable: The modified Queryable instance.
        """
        if comparer is not None:
            self.collection = sorted(self.collection, key=key, reverse=reverse, cmp=comparer)
        else:
            self.collection.sort(key=key, reverse=reverse)
        return self

    def Distinct(self):
        """
        Removes duplicate items from the collection.

        Returns:
        Queryable: The modified Queryable instance.
        """
        self.collection = list(set(self.collection))
        return self

    def Limit(self, n):
        """
        Limits the number of items in the collection to the first n items.

        Parameters:
        n (int): The maximum number of items to include.

        Returns:
        Queryable: The modified Queryable instance.
        """
        if not isinstance(n, int) or n < 0:
            raise ValueError("The limit must be a non-negative integer.")
        self.collection = self.collection[:n]
        return self

    def Count(self):
        """
        Returns the number of items in the collection.

        Returns:
        int: The count of items in the collection.
        """
        return len(self.collection)

    def Each(self, action):
        """
        Executes an action for each item in the collection.

        Parameters:
        action (function): A function to execute for each item.

        Returns:
        Queryable: The modified Queryable instance.
        """
        if not callable(action):
            raise TypeError("The action parameter must be a callable function.")
        for item in self.collection:
            action(item)
        return self

    def Reverse(self):
        """
        Reverses the order of the items in the collection.

        Returns:
        Queryable: The modified Queryable instance.
        """
        self.collection.reverse()
        return self

    def Get(self, index, default=None):
        """
        Retrieves an item at a given index with optional default value.

        Parameters:
        index (int): The index of the item to retrieve.
        default: The value to return if the index is out of bounds.

        Returns:
        The item at the given index, or the default value if the index is invalid.
        """
        if 0 <= index < len(self.collection):
            return self.collection[index]
        return default

    def AsGenerator(self):
        """
        Returns a generator for the items in the collection.

        Yields:
        Items in the collection one by one.
        """
        for item in self.collection:
            yield item

    def ToCollection(self):
        """
        Converts the internal list back to a Collection instance.

        Returns:
        Collection: A new Collection containing the queried items.
        """
        return Collection(self.collection)

    def __str__(self):
        """
        Returns a string representation of the collection managed by the Queryable.

        Returns:
        str: A string that represents the collection.
        """
        return str(self.collection)
