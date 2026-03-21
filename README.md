# Spark Test Project

E2E test repo for Aira AI agent flows.

## Greeting Utility

The `greet` module provides a simple utility for generating personalized greeting strings.

### Usage

```python
from greet import greet

message = greet("Alice")
print(message)  # Hello, Alice!
```

### Running the Tests

Make sure you have [pytest](https://pytest.org) installed:

```bash
pip install pytest
```

Then run the test suite:

```bash
pytest test_greet.py
```

Or run all tests in the project:

```bash
pytest
```

### Example Output

```
$ python -c "from greet import greet; print(greet('World'))"
Hello, World!
```
