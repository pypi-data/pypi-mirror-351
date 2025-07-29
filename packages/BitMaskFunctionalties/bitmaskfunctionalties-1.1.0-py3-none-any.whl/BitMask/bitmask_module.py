"""
This module provides a `BitMask` class for efficient manipulation and representation of binary data as a fixed-length
sequence of bits.

It allows initializing a bitmask with a specified length and an optional starting value, provides methods for common
bitwise operations such as setting, resetting, and flipping individual or all bits.
Includes other useful functionalities for various properties of the bitmask.

The BitMask class is useful for bit manipulation, flag management, or compact binary representations of data.
"""

# Author: Adam Thieringer
# Date: 2025-05-27
# Version: 1.1.0
# Bit hacks used can be found at https://graphics.stanford.edu/~seander/bithacks.html


from __future__ import annotations
import warnings


class BitMask:
    def __init__(self, length: int, value: int = 0):
        """
        Initialize a BitMask with a specified length and an optional initial integer value.

        :param length: The maximum number of bits the BitMask can hold.
        :type length: int
        :param value: An integer value to initialize the BitMask. Defaults to 0.
        :type value: int
        """
        # length data validation
        if not isinstance(length, int):
            raise TypeError(f"Expected type int, got type {type(length)}")

        if length <= 0:
            raise ValueError(f"Length {length} must be greater than 0")

        self.__max_length = length

        # value data validation
        if value != 0:
            if isinstance(value, int):
                if value < 0:
                    raise ValueError(f"Num {value} must be positive")
                elif value >= (1 << self.__max_length):
                    raise ValueError(f"Num {value} must be less than {1 << self.__max_length}")
                self.__value = value
            else:
                raise TypeError(f"Expected type int, got type {type(value)}")
        else:
            self.__value = value

    @property
    def max_length(self) -> int:
        return self.__max_length

    @property
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, new_value: int) -> None:
        """
        Set the value of the whole BitMask.

        :param new_value: The new value of the BitMask.
        :type new_value: int
        """
        # new_value data validation
        if isinstance(new_value, int):
            if new_value < 0:
                raise ValueError(f"Value {new_value} must be positive")
            elif new_value >= (1 << self.__max_length):
                raise ValueError(f"Value {new_value} must be less than {1 << self.__max_length}")
            self.__value = new_value
        else:
            raise TypeError(f"Expected type int, got type {type(new_value)}")

    def set_bit(self, pos: int) -> None:
        """
        Set the bit at the specified position to 1.

        :param pos: The position of the bit to set (0-indexed).
        :type pos: int
        """
        # pos data validation
        if not isinstance(pos, int):
            raise TypeError(f"Expected type int, got type {type(pos)}")

        if pos >= self.__max_length:
            raise IndexError(f"Index {pos} is out of range")

        self.__value |= 1 << pos

    def set_all(self) -> None:
        """Set all bits in the BitMask to 1."""
        self.__value |= (1 << self.__max_length) - 1

    def flip_bit(self, pos: int) -> None:
        """
        Flip the bit at the specified position.

        :param pos: The position of the bit to flip (0-indexed).
        :type pos: int
        """
        # pos data validation
        if not isinstance(pos, int):
            raise TypeError(f"Expected type int, got type {type(pos)}")

        if pos >= self.__max_length:
            raise IndexError(f"Index {pos} is out of range")

        self.__value ^= 1 << pos

    def flip_all(self) -> None:
        """Flip all bits in the BitMask."""
        self.__value ^= (1 << self.__max_length) - 1

    def reset_bit(self, pos: int) -> None:
        """
        Reset the bit at the specified position to 0.

        :param pos: The position of the bit to reset (0-indexed).
        :type pos: int
        """
        # pos data validation
        if not isinstance(pos, int):
            raise TypeError(f"Expected type int, got type {type(pos)}")

        if pos >= self.__max_length:
            raise IndexError(f"Index {pos} is out of range")

        self.__value &= ~(1 << pos)

    def reset_all(self) -> None:
        """Reset all bits in the BitMask to 0."""
        self.__value = 0

    def reverse_bit_order(self) -> None:
        """Reverses the bit order of the BitMask"""
        reversed_bits = 0
        for _ in range(self.__max_length):
            reversed_bits <<= 1
            reversed_bits |= (self.__value & 1)
            self.__value >>= 1

        self.__value = reversed_bits

    def reverse_bits(self) -> None:
        """Reverses the bit order of the BitMask"""
        warnings.warn("reverse_bits() will be deprecated in a future version. Use reverse_bit_order() instead",
                      DeprecationWarning, stacklevel=1)

        reversed_bits = 0
        for _ in range(self.__max_length):
            reversed_bits <<= 1
            reversed_bits |= (self.__value & 1)
            self.__value >>= 1

        self.__value = reversed_bits

    def get_bit(self, pos: int) -> int:
        """
        Get the value of the bit at the specified position.

        :param pos: The position of the bit to retrieve (0-indexed).
        :type pos: int
        :return: The value of the bit (0 or 1).
        :rtype: int
        """
        # pos data validation
        if not isinstance(pos, int):
            raise TypeError(f"Expected type int, got type {type(pos)}")

        if pos >= self.__max_length:
            raise IndexError(f"Index {pos} is out of range")

        return (self.__value >> pos) & 1

    def get_count(self) -> int:
        """
        Count the number of set bits (1s) in the BitMask.

        :return: The count of set bits.
        :rtype: int
        """
        temp_value = self.__value
        count = 0
        while temp_value:
            temp_value &= temp_value - 1
            count += 1

        return count

    def get_non_zero(self) -> tuple[int, ...]:
        """
        Get the indices of all set bits (1s).

        :return: A list of indices where bits are set to 1.
        :rtype: tuple[int, ...]
        """
        return tuple(index for index in range(self.__max_length) if (self.__value >> index) & 1)

    def get_zero(self) -> tuple[int, ...]:
        """
        Get the indices of all unset bits (0s).

        :return: A list of indices where bits are set to 0.
        :rtype: tuple[int, ...]
        """
        return tuple(index for index in range(self.__max_length) if not (self.__value >> index) & 1)

    def get_lsb(self) -> int:
        """
        Get the index of the least significant set bit (LSB).

        :return: The index of the least significant bit that is set to 1, or -1 if no bits are set.
        :rtype: int
        """
        return (self.__value & -self.__value).bit_length() - 1

    def set_binary(self, new_value: str) -> None:
        """
        Set the BitMask value using a binary string.

        :param new_value: A binary string representation of the value.
        :type new_value: str
        """
        # num data validation
        if not isinstance(new_value, str):
            raise TypeError(f"Expected type str, got type {type(new_value)}")

        try:
            new_value = int(new_value, 2)
        except ValueError:
            raise ValueError(f"{new_value} is not a valid binary string")
        except Exception:
            raise Exception

        if new_value >= (1 << self.__max_length):
            raise ValueError(f"Value {new_value} must be less than {bin(1 << self.__max_length)}")
        elif new_value < 0:
            raise ValueError(f"Value {new_value} must be positive")
        else:
            self.__value = new_value

    def set_hexadecimal(self, new_value: str) -> None:
        """
        Set the BitMask value using a hexadecimal string.

        :param new_value: A hexadecimal string representation of the value.
        :type new_value: str
        """
        # num data validation
        if not isinstance(new_value, str):
            raise TypeError(f"Expected type str, got type {type(new_value)}")

        try:
            new_value = int(new_value, 16)
        except ValueError:
            raise ValueError(f"{new_value} is not a valid hexadecimal string")
        except Exception:
            raise Exception

        if new_value >= (1 << self.__max_length):
            raise ValueError(f"Value {new_value} must be less than {hex(1 << self.__max_length)}")
        elif new_value < 0:
            raise ValueError(f"Value {new_value} must be positive")
        else:
            self.__value = new_value

    def set_decimal(self, new_value: int) -> None:
        """
        Set the BitMask value using an integer.

        :param new_value: The value to set.
        :type: num
        """
        # num data validation
        if not isinstance(new_value, int):
            raise TypeError(f"Expected type int, got type {type(new_value)}")

        if new_value >= (1 << self.__max_length):
            raise ValueError(f"Value {new_value} must be less than {1 << self.__max_length}")
        elif new_value < 0:
            raise ValueError(f"Value {new_value} must be positive")

        self.__value = new_value

    def to_binary(self) -> str:
        """Return a binary string representation of the BitMask."""
        binary_string = bin(self.__value)
        return binary_string[:2] + binary_string[2:].zfill(self.__max_length)

    def to_hexadecimal(self) -> str:
        """Return a hexadecimal string representation of the BitMask."""
        hexadecimal_string = hex(self.__value)
        return hexadecimal_string[:2] + hexadecimal_string[2:].zfill((self.__max_length + 3) >> 2)

    def to_decimal(self) -> int:
        """Return the decimal value of the BitMask."""
        return self.__value

    # Returns all bits separated by a space
    def __str__(self) -> str:
        return ' '.join([str(bit) for bit in self])[::-1]

    def __getitem__(self, item: int | slice) -> int | BitMask:
        # When sliced, returns a BitMask object with new max_length and value
        if isinstance(item, slice):
            start, stop, step = item.indices(self.__max_length)
            new_value = 0
            new_length = abs(start - stop)

            # Create the value for the new BitMask one bit at a time
            if step > 0:
                for i, pos in enumerate(range(start, stop, step)):
                    new_value |= ((self.__value >> pos) & 1) << i
            else:
                for i, pos in enumerate(range(start, stop, step)):
                    new_value |= ((self.__value >> pos) & 1) << (new_length - 1 - i)

            return BitMask(new_length, new_value)

        # For an index, return the value of the bit at the index
        elif isinstance(item, int):
            if item < 0:
                # Handle negative indices
                if abs(item) > self.__max_length:
                    raise IndexError(f"Index {item} is out of range")
                else:
                    item += self.__max_length

            return self.get_bit(item)
        else:
            raise TypeError(f"BitMask indices must be integers ot slices, not {type(item)}")

    # Sets the bit at position 'key' to 'value'
    def __setitem__(self, key: int, value: int) -> None:
        if not isinstance(key, int):
            if isinstance(key, slice):
                raise TypeError(f"BitMask object does not support slicing assignments")
            else:
                raise TypeError(f"BitMask indices must be integers, not {type(key)}")

        # Handle negative indices
        if key < 0:
            if abs(key) > self.__max_length:
                raise IndexError(f"Index {key} is out of range")
            else:
                key += self.__max_length

        if key >= self.__max_length:
            raise IndexError(f"Index {key} is out of range")

        if value not in [0, 1]:
            raise ValueError(f"Cannot assign {value} to position {key} because {value} is not 0 or 1")

        if value:
            self.set_bit(key)
        else:
            self.reset_bit(key)

    # Uses max length for __len__
    def __len__(self) -> int:
        return self.__max_length

    # Comparisons for BitMasks of different lengths are not supported
    # Comparisons for string representations of integers are not supported
    # Compares using the value of the BitMask, not amount of bits set
    def __eq__(self, other: int | BitMask) -> bool | NotImplemented:
        if isinstance(other, int):
            return self.__value == other
        elif isinstance(other, BitMask):
            if self.__max_length != other.max_length:
                return NotImplemented
            else:
                return self.__value == other.value
        elif not isinstance(other, BitMask):
            return NotImplemented

    def __ne__(self, other: int | BitMask) -> bool | NotImplemented:
        equality = self.__eq__(other=other)
        if equality == NotImplemented:
            return NotImplemented
        else:
            return not equality

    def __lt__(self, other: int | BitMask) -> bool | NotImplemented:
        if isinstance(other, int):
            return self.__value < other
        elif isinstance(other, BitMask):
            if self.__max_length != other.max_length:
                raise TypeError(f"'<' not supported between instances of BitMask with different lengths")
            else:
                return self.__value < other.value
        else:
            return NotImplemented

    def __le__(self, other: int | BitMask) -> bool | NotImplemented:
        if isinstance(other, int):
            return self.__value <= other
        elif isinstance(other, BitMask):
            if self.__max_length != other.max_length:
                raise TypeError(f"'<=' not supported between instances of BitMask with different lengths")
            else:
                return self.__value <= other.value
        else:
            return NotImplemented

    def __gt__(self, other: int | BitMask) -> bool | NotImplemented:
        if isinstance(other, int):
            return self.__value > other
        elif isinstance(other, BitMask):
            if self.__max_length != other.max_length:
                raise TypeError(f"'>' not supported between instances of BitMask with different lengths")
            else:
                return self.__value > other.value
        else:
            return NotImplemented

    def __ge__(self, other: int | BitMask) -> bool | NotImplemented:
        if isinstance(other, int):
            return self.__value >= other
        elif isinstance(other, BitMask):
            if self.__max_length != other.max_length:
                raise TypeError(f"'>=' not supported between instances of BitMask with different lengths")
            else:
                return self.__value >= other.value
        else:
            return NotImplemented

    # Yields each bit from LSB to MSB
    def __iter__(self) -> int:
        current = 0
        while current < self.__max_length:
            yield (self.__value >> current) & 1
            current += 1

    def __invert__(self) -> int:
        return self.__value ^ (1 << self.__max_length) - 1

    def __hash__(self) -> None:
        return None
