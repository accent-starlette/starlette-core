# Testing

Within the `starlette_core` package there is a set of helpers to aid testing your project.

## SQLAlchemy fields

Assuming you have the following SQLAlchemy model to test:

```python
import sqlalchemy as sa
from starlette_core.database import Base

class User(Base):
    email = sa.Column(sa.String(100), nullable=False, index=True, unique=True)
```

There is a function to test fields on a model:

```python
def assert_model_field(
    cls: typing.Type[Base],
    name: str,
    type: typing.Any,
    nullable: bool = True,
    index: bool = False,
    unique: bool = False,
    length: int = None,
):
    ...
```

This can be used like so to test each field:

```python
from starlette_core.testing import assert_model_field

def test_email():
    assert_model_field(User, "email", sa.String, False, True, True, 255)
```