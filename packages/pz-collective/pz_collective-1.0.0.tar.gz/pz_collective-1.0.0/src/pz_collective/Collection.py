from datetime import datetime
import pprint
import random
from functools import reduce
import sys

class Collection:
    """
    Collection Class
    
    This class is a simple implementation of a list-like data structure that allows for adding, removing, retrieving,
    and managing items in a list. It provides various methods to manipulate and query the list, similar to
    C#'s List<T> class. The class is not type-restricted, allowing for flexibility in the types of items that can be added.
    
    Methods included:
    - Add: Adds an item to the list.
    - Remove: Removes an item from the list.
    - Get: Retrieves an item by index.
    - Clear: Clears all items from the list.
    - Count: Returns the number of items in the list.
    - Contains: Checks if an item is in the list.
    - IndexOf: Returns the index of a specified item.
    - ToList: Returns a copy of the internal list.
    - Fuse: Fuses the current list with another Collection instance.
    - Sort: Sorts the items in the list.
    - Reverse: Reverses the order of items in the list.
    - Filter: Returns a new collection filtered based on a condition.
    - Map: Applies a function to all items in the list and returns a new collection.
    - Reduce: Reduces the list to a single value using a function.
    - RemoveAt: Removes an item at a specific index.
    - Insert: Inserts an item at a specific index.
    - Distinct: Returns a new collection containing only distinct items.
    - Extend: Adds multiple items to the collection.
    - Find: Finds the first item matching a condition.
    - FlatMap: Applies a function that returns iterables and flattens the result.
    - Min: Finds the minimum value in the collection.
    - Max: Finds the maximum value in the collection.
    - Sample: Randomly samples items from the collection.
    - Zip: Combines two collections into a collection of tuples.
    - All: Checks if all items satisfy a condition.
    - Any: Checks if any item satisfies a condition.
    - IsEmpty: Checks if the collection is empty.
    - PrettyPrint: Prints the collection in a readable format.
    - Metadata: Returns metadata about the collection.
    - FromFile: Creates a Collection from all lines in a File object.
    - __str__: Provides a string representation of the list.
    - __iter__: Makes the list iterable.
    - __getitem__: Enables index-based access with square brackets.
    - __setitem__: Enables assignment to indexes or slices.
    - __delitem__: Enables deletion by index or slice.
    - __eq__: Compares two collections for equality.
    - __copy__: Creates a shallow copy of the collection.
    
    Usage:
    The Collection class can be used to store any type of elements, providing easy-to-use methods to perform common
    list operations, making it versatile for different use cases.
    """
    def __init__(self, *args):
        """
        Initializes a new instance of the Collection class.
        Creates a list to store items, optionally initializing with provided items.

        Parameters:
        *args: Optional items to initialize the list with.
        """
        if len(args) == 1 and isinstance(args[0], list):
            self._items = args[0][:]
        else:
            self._items = list(args)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.modification_count = 0

    def Add(self, item) -> 'Collection':
        """
        Adds an item to the list and returns self for chaining.

        Parameters:
        item: The item to be added to the list.

        Returns:
        Collection: The collection instance.
        """
        self._items.append(item)
        self.updated_at = datetime.now()
        self.modification_count += 1
        return self

    def Remove(self, item) -> 'Collection':
        """
        Removes an item from the list if it exists.
        Returns True if the item was removed, False if the item was not found.

        Parameters:
        item: The item to be removed from the list.
        """
        if item in self._items:
            self._items.remove(item)
            self.updated_at = datetime.now()
            self.modification_count += 1
        return self

    def Get(self, index: int):
        """
        Gets an item by index. Returns None if the index is out of bounds.

        Parameters:
        index (int): The index of the item to retrieve.

        Returns:
        The item at the specified index, or None if the index is invalid.
        """
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def Clear(self) -> 'Collection':
        """
        Clears all items from the list and returns self for chaining.
        """
        self._items.clear()
        self.updated_at = datetime.now()
        self.modification_count += 1
        return self

    def Count(self) -> int:
        """
        Returns the number of items in the list.

        Returns:
        int: The number of items currently in the list.
        """
        return len(self._items)

    def Contains(self, item) -> bool:
        """
        Checks if an item is in the list.

        Parameters:
        item: The item to check for in the list.

        Returns:
        bool: True if the item is in the list, False otherwise.
        """
        return item in self._items

    def IndexOf(self, item) -> int:
        """
        Returns the index of the item if it exists, otherwise returns -1.

        Parameters:
        item: The item to find in the list.

        Returns:
        int: The index of the item if found, -1 if not found.
        """
        try:
            return self._items.index(item)
        except ValueError:
            return -1

    def ToList(self):
        """
        Returns a copy of the internal list.

        Returns:
        list: A copy of the list containing all items.
        """
        return self._items[:]

    def Fuse(self, other: 'Collection') -> 'Collection':
        """
        Fuses the current list with another Collection instance, adding all items from the other list.

        Parameters:
        other (Collection): Another Collection instance to be fused with the current list.
        
        Returns:
        Collection: The collection instance.
        """
        if isinstance(other, Collection):
            self._items.extend(other.ToList())
            self.updated_at = datetime.now()
            self.modification_count += 1
        else:
            raise TypeError("Argument must be of type Collection.")
        return self

    def Sort(self, reverse: bool = False) -> 'Collection':
        """
        Sorts the items in the collection in ascending order by default.
        If reverse is True, sorts in descending order.

        Parameters:
        reverse (bool): If True, sorts the list in descending order.
        
        Returns:
        Collection: The collection instance.
        """
        self._items.sort(reverse=reverse)
        self.updated_at = datetime.now()
        self.modification_count += 1
        return self

    def Reverse(self) -> 'Collection':
        """
        Reverses the order of items in the collection and returns self for chaining.
        
        Returns:
        Collection: The collection instance.
        """
        self._items.reverse()
        self.updated_at = datetime.now()
        self.modification_count += 1
        return self

    def Filter(self, condition) -> 'Collection':
        """
        Filters the items in the collection based on a provided condition.

        Parameters:
        condition (function): A function that returns True for items that should be included.

        Returns:
        Collection: A new collection containing only the items that match the condition.
        """
        self.updated_at = datetime.now()
        self.modification_count += 1
        return Collection([item for item in self._items if condition(item)])

    def Map(self, func) -> 'Collection':
        """
        Applies a function to each item in the collection.

        Parameters:
        func (function): A function to apply to each item.

        Returns:
        Collection: A new collection with the results of applying the function to each item.
        """
        self.updated_at = datetime.now()
        self.modification_count += 1
        return Collection([func(item) for item in self._items])

    def Reduce(self, func, initial=None):
        """
        Reduces the items in the collection to a single value using a binary function.

        Parameters:
        func (function): A binary function to combine items.
        initial: An optional initial value to start the reduction.

        Returns:
        The reduced value.
        """
        self.updated_at = datetime.now()
        self.modification_count += 1
        return reduce(func, self._items, initial)

    def RemoveAt(self, index: int) -> 'Collection':
        """
        Removes an item at a specific index.

        Parameters:
        index (int): The index of the item to remove.

        Raises:
        IndexError: If the index is out of range.
        
        Returns:
        Collection: The collection instance.
        """
        if 0 <= index < len(self._items):
            del self._items[index]
            self.updated_at = datetime.now()
            self.modification_count += 1
        else:
            raise IndexError("Index out of range.")
        return self

    def Insert(self, index: int, item) -> 'Collection':
        """
        Inserts an item at the specified index.

        Parameters:
        index (int): The index at which to insert the item.
        item: The item to insert.

        Raises:
        IndexError: If the index is out of range.
        
        Returns:
        Collection: The collection instance.
        """
        if 0 <= index <= len(self._items):
            self._items.insert(index, item)
            self.updated_at = datetime.now()
            self.modification_count += 1
        else:
            raise IndexError("Index out of range.")
        return self

    def Distinct(self) -> 'Collection':
        """
        Returns a new collection containing only distinct items.

        Returns:
        Collection: A new collection with distinct items.
        """
        self.updated_at = datetime.now()
        self.modification_count += 1
        return Collection(list(set(self._items)))

    def Extend(self, items) -> 'Collection':
        """
        Adds multiple items to the collection.

        Parameters:
        items (iterable): An iterable of items to add to the collection.
        
        Returns:
        Collection: The collection instance.
        """
        self._items.extend(items)
        self.updated_at = datetime.now()
        self.modification_count += 1
        return self

    def Find(self, condition):
        """
        Finds the first item that matches the condition.

        Parameters:
        condition (function): A function that returns True for the item that should be found.

        Returns:
        The first matching item, or None if no match is found.
        """
        for item in self._items:
            if condition(item):
                return item
        return None

    def FlatMap(self, func) -> 'Collection':
        """
        Applies a function to each item in the collection, then flattens the result.

        Parameters:
        func (function): A function to apply to each item, which returns an iterable.

        Returns:
        Collection: A new flat collection with the results of applying the function to each item.
        """
        self.updated_at = datetime.now()
        self.modification_count += 1
        flattened_items = [sub_item for item in self._items for sub_item in func(item)]
        return Collection(flattened_items)

    def Min(self):
        """
        Returns the minimum value in the collection.

        Returns:
        The minimum value in the collection.
        """
        if self._items:
            return min(self._items)
        raise ValueError("Collection is empty.")

    def Max(self):
        """
        Returns the maximum value in the collection.

        Returns:
        The maximum value in the collection.
        """
        if self._items:
            return max(self._items)
        raise ValueError("Collection is empty.")

    def Sample(self, n: int) -> 'Collection':
        """
        Returns a random sample of n items from the collection.

        Parameters:
        n (int): The number of items to sample.

        Returns:
        Collection: A new collection containing n randomly sampled items.
        """
        if n > len(self._items):
            raise ValueError("Sample size cannot be greater than the number of items in the collection.")
        return Collection(random.sample(self._items, n))

    def Zip(self, other: 'Collection') -> 'Collection':
        """
        Zips the current collection with another collection.

        Parameters:
        other (Collection): Another collection to zip with the current collection.

        Returns:
        Collection: A new collection containing tuples of paired items.
        """
        self.updated_at = datetime.now()
        self.modification_count += 1
        return Collection(list(zip(self._items, other.ToList())))

    def All(self, condition) -> bool:
        """
        Checks if all items in the collection satisfy the condition.

        Parameters:
        condition (function): A function that returns True or False for each item.

        Returns:
        bool: True if all items satisfy the condition, False otherwise.
        """
        return all(condition(item) for item in self._items)

    def Any(self, condition) -> bool:
        """
        Checks if any item in the collection satisfies the condition.

        Parameters:
        condition (function): A function that returns True or False for each item.

        Returns:
        bool: True if any item satisfies the condition, False otherwise.
        """
        return any(condition(item) for item in self._items)

    def IsEmpty(self) -> bool:
        """
        Checks if the collection is empty.

        Returns:
        bool: True if the collection is empty, False otherwise.
        """
        return len(self._items) == 0

    def Print(self) -> None:
        """
        Prints the collection in a more human-readable format.
        """
        pprint.pprint(self._items)

    def Metadata(self) -> dict:
        """
        Returns metadata of the collection including creation and last update times, count, data type distribution,
        memory size, modification history, and other details.

        Returns:
        dict: A dictionary containing metadata.
        """
        type_distribution = {}
        for item in self._items:
            item_type = type(item).__name__
            type_distribution[item_type] = type_distribution.get(item_type, 0) + 1

        return {
            "CreateAt": self.created_at,
            "UpdatedAt": self.updated_at,
            "Count": len(self._items),
            "TypeDistribution": type_distribution,
            "MemorySize": sum(sys.getsizeof(item) for item in self._items),
            "LifetimeSeconds": (datetime.now() - self.created_at).total_seconds(),
            "ModificationCount": self.modification_count,
            "IsHomogeneous": len(set(type(item) for item in self._items)) == 1 if self._items else True,
            "AllUnique": len(self._items) == len(set(self._items))
        }

    def __iter__(self):
        """
        Makes the list iterable.

        Returns:
        An iterator for the internal list, allowing iteration over the list items.
        """
        return iter(self._items)

    def __getitem__(self, index):
        """
        Enables index-based access with square brackets, including support for slicing.

        Parameters:
        index (int or slice): The index or slice of items to retrieve.

        Returns:
        The item at the specified index or a Collection if a slice is provided.
        """
        if isinstance(index, slice):
            return Collection(self._items[index])
        elif isinstance(index, int):
            if 0 <= index < len(self._items):
                return self._items[index]
            raise IndexError("Index out of range.")
        else:
            raise TypeError("Index must be an int or a slice.")

    def __setitem__(self, index, value):
        """
        Enables item assignment with square brackets, including support for slicing.

        Parameters:
        index (int or slice): The index or slice of items to set.
        value: The value or values to set in the collection.
        """
        if isinstance(index, slice):
            self._items[index] = value
        elif isinstance(index, int):
            if 0 <= index < len(self._items):
                self._items[index] = value
                self.updated_at = datetime.now()
            else:
                raise IndexError("Index out of range.")
        else:
            raise TypeError("Index must be an int or a slice.")

    def __delitem__(self, index):
        """
        Enables item deletion with square brackets, including support for slicing.

        Parameters:
        index (int or slice): The index or slice of items to delete.
        """
        if isinstance(index, slice) or isinstance(index, int):
            del self._items[index]
            self.updated_at = datetime.now()
        else:
            raise TypeError("Index must be an int or a slice.")

    def __eq__(self, other: 'Collection') -> bool:
        """
        Compares two collections for equality.

        Parameters:
        other (Collection): The collection to compare with.

        Returns:
        bool: True if the collections are equal, False otherwise.
        """
        if not isinstance(other, Collection):
            return False
        return self._items == other._items

    def __copy__(self) -> 'Collection':
        """
        Creates a shallow copy of the collection.

        Returns:
        Collection: A new collection containing the same items.
        """
        return Collection(self._items)

    def __str__(self) -> str:
        """
        Returns a string representation of the list.

        Returns:
        str: A string that represents the list.
        """
        return str(self._items)