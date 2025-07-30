# HybridMethod: A Python Hybrid Method Decorator Class

The HybridMethod library provides a Python method decorator that allows methods defined
in a class to be used as both a class method and an instance method..

The `@hybridmethod` decorator provided by the library wraps methods defined in classes
using the usual `@decorator` syntax. Methods defined in classes that are decorated with
the `@hybridmethod` decorator can then be accessed as both class methods and as instance
methods, with the first argument passed to the method being a reference to either the
class when the method is called as a class method or to the instance when the method is
called as an instance method.

If a class-level property is defined and then an instance-level property is created with
the same name that shadows the class-level property, the hybrid method can be used to
interact with both the class-level property and the instance-level property simply based
on whether the hybrid method was called directly on the class or on an a class instance.

If desired, a simple check of the value of the first variable passed to a hybrid method
using `isinstance(<variable>, <class>)` allows one to determine if the call was made on
an instance of the class in which case `isinstance()` evaluates to `True` or if the call
was made on the class itself, in which case `isinstance()` evaluates to `False`.

The variable passed as the first argument to the method may have any name, including as
is common in Python, `self`, although the use of `self` as the name of this argument on
an instance method is just customary and the name has no significance.

If using the `isinstance(<variable>, <class>)` check as described above is used simply
substitute in the name of the first variable of a hybrid method for `<variable>` and the
name of the class for `<class>`.

### Requirements

The HybridMethod library has been tested with Python 3.10, 3.11, 3.12 and 3.13. The library is not compatible with Python 3.9 or earlier.

### Installation

The HybridMethod library is available from PyPI, so may be added to a project's dependencies via its `requirements.txt` file or similar by referencing the HybridMethod library's name, `hybridmethod`, or the library may be installed directly into your local runtime environment using `pip` via the `pip install` command by entering the following into your shell:

	$ pip install hybridmethod

### Usage

To use the HybridMethod library decorator import the decorator of the same name from the
library and use it to decorate the class methods you wish to use as both class methods
and instance methods:

```python
from hybridmethod import hybridmethod

class MyClass(object):
	items: list[str] = []
	
	def __init__(self):
		# Create an 'items' instance variable; note that this shadows the class variable
		# of the same name which can still be accessed directly via self.__class__.items
		self.items: list[object] = []

	@hybridmethod
	def add_item(self, item: object):
		# We can use the following line to differentiate between the call being made on
		# an instance or directly on the class; isinstance(self, <class>) returns True
		# if the method was called on an instance of the class, or False if the method
		# was called on the class directly; the 'self' variable will reference either
		# the instance or the class; although 'self' is traditionally used in Python as
		# reference to the instance
		if isinstance(self, MyClass):
			self.items.append(item)
		else:
			self.items.append(item)

	def get_class_items(self) -> list[object]:
		return self.__class__.items

	def get_instance_items(self) -> list[object]:
		return self.items

	def get_combined_items(self) -> list[object]:
		return self.__class__.items + self.items

MyClass.add_item("ABC")  # Add an item to the class-level items list

myclass = MyClass()

myclass.add_item("XYZ")  # Add an item to the instance-level items list

assert myclass.get_class_items() == ["ABC"]

assert myclass.get_instance_items() == ["XYZ"]

assert myclass.get_combined_items() == ["ABC", "XYZ"]
```

### Unit Tests

The HybridMethod library includes a suite of comprehensive unit tests which ensure that
the library functionality operates as expected. The unit tests were developed with and
are run via `pytest`.

To ensure that the unit tests are run within a predictable runtime environment where all of the necessary dependencies are available, a [Docker](https://www.docker.com) image is created within which the tests are run. To run the unit tests, ensure Docker and Docker Compose is [installed](https://docs.docker.com/engine/install/), and perform the following commands, which will build the Docker image via `docker compose build` and then run the tests via `docker compose run` – the output of running the tests will be displayed:

```shell
$ docker compose build
$ docker compose run tests
```

To run the unit tests with optional command line arguments being passed to `pytest`, append the relevant arguments to the `docker compose run tests` command, as follows, for example passing `-vv` to enable verbose output:

```shell
$ docker compose run tests -vv
```

See the documentation for [PyTest](https://docs.pytest.org/en/latest/) regarding available optional command line arguments.

### Copyright & License Information

Copyright © 2025 Daniel Sissman; licensed under the MIT License.