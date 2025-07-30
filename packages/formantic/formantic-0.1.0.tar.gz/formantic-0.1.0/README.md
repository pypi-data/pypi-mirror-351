# ![FormAntic](resources/logo.svg)

[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![ruff](https://github.com/wnowicki/formantic/workflows/Ruff/badge.svg)](https://github.com/wnowicki/formantic/actions?query=branch%3Amain)
[![pytest](https://github.com/wnowicki/formantic/workflows/Pytest/badge.svg)](https://github.com/wnowicki/formantic/actions?query=branch%3Amain)
[![markdown](https://github.com/wnowicki/formantic/workflows/Markdown%20Lint/badge.svg)](https://github.com/wnowicki/formantic/actions?query=branch%3Amain)
[![License: GPLv3](https://img.shields.io/badge/License-MIT-blue.svg)](https://license.md/licenses/mit-license/)

## Overview

**Form Generator**  
It is designed to work with [Pydantic](https://docs.pydantic.dev/latest/) and [WTForms](https://wtforms.readthedocs.io/en/). Especially useful with [SQL Admin](https://aminalaee.github.io/sqladmin/)

## Usage

Simple way:

```python
from pydantic import BaseModel, Field
from formantic import Former

class User(BaseModel):
    id: int = Field(..., description="The unique identifier for the user")
    name: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email address of the user")

# WTForm based on Pydantic model
form = Former(User).gen_form()

form.process()
```

or with some additional modifications:

```python
from pydantic import BaseModel, Field
from wtforms import StringField
from wtforms.form import BaseForm
from formantic import Former

class User(BaseModel):
    id: int = Field(..., description="The unique identifier for the user")
    name: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email address of the user")

# Form schema for BAseModel based on Pydantic model
form_schema = Former(User).gen_form_schema()

# Some additional field
form_schema["extra_field"] = StringField(
    "extra_field",
    description="An additional field not in the Pydantic model",
    default="Default Value"
)

form = BaseForm(form_schema)

form.process()
```

Then work with the form as with normal WTForms

## Test

```shell
uv run pytest
```

## Security

If you discover any security-related issues, please email [email](mailto:wnowicki@me.com) instead of using the issue tracker.

---
Copyright (c) 2025 Wojciech Nowicki
