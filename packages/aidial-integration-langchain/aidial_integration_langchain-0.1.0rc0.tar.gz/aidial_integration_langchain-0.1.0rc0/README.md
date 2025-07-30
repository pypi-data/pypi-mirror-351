# Overview

The package provides useful integration of DIAL API with Langchain library.

## Passing DIAL-specific extra fields in Langchain requests/responses

`langchain_openai` [doesn't allow](https://github.com/langchain-ai/langchain/issues/26617) to pass extra request/response parameters to/from the upstream model.

The minimal example highlighting the issue could be found in the [example folder](./example/):

```sh
> cd example
> python -m venv .venv
> source .venv/bin/activate
> pip install -q -r requirements.txt
> python -m app
Received extra fields in:
(1) ☐ Request - in the `messages` list
(2) ☑ Request - on the top-level
(3) ☐ Response - in the `message` field
(4) ☐ Response - on the top-level
```

`langchain_openai` ignores certain extra fields, meaning that the upstream endpoint won't receive (1) and the client won't receive (3) and (4) if they were sent by the upstream.

Note that **top-level request extra fields** do actually reach the upstream.

### Solution

One way to *fix* the issue, is to modify the Langchain methods that ignore these extra fields so that they are taken into account.

This is achieved via monkey-patching certain private methods in `langchain_openai` that do the conversion from the Langchain datatypes to dictionaries and vice versa.

### Usage

Import `aidial_integration_langchain` before importing any Langchain module to apply the patches:

```python
import aidial_integration_langchain.patch # isort:skip  # noqa: F401 # type: ignore

from langchain_openai import AzureChatOpenAI
...
```

The same example as above, but with the patch applied:

```sh
> cd example
> python -m venv .venv
> source .venv/bin/activate
> pip install -q -r requirements.txt
> cp -r ../src/aidial_integration_langchain .
> python -m app
Received extra fields in:
(1) ☑ Request - in the `messages` list
(2) ☑ Request - on the top-level
(3) ☑ Response - in the `message` field
(4) ☑ Response - on the top-level
```

### Supported Langchain versions

The following `langchain_openai` versions have been tested for Python 3.9, 3.10, 3.11, 3.12, and 3.13:

|Version|Request per-message|Response per-message|Response top-level|
|---|---|---|---|
|>=0.1.1,<=0.1.22|🟢|🟢|🔴|
|>=0.1.23,<=0.1.25|🟢|🟢|🟢|
|>=0.2.0,<=0.2.14|🟢|🟢|🟢|
|>=0.3.0,<=0.3.16|🟢|🟢|🟢|

> [!NOTE]
> The patch for `langchain_openai<=0.1.22` doesn't support response top-level extra fields, since the structure of the code back then was not very amicable for monkey-patching in this particular respect.

### Configuration

The list of extra fields that are allowed to pass-through is controlled by the following environment variables.

|Name|Default|Description|
|---|---|---|
|LC_EXTRA_REQUEST_MESSAGE_FIELDS|custom_content|A comma-separated list of extra message fields allowed to pass-through in chat completion requests.|
|LC_EXTRA_RESPONSE_MESSAGE_FIELDS|custom_content|A comma-separated list of extra message fields allowed to pass-through in chat completion responses.|
|LC_EXTRA_RESPONSE_FIELDS|statistics|A comma-separated list of extra fields allowed to pass-through on the top-level of the chat completion responses.|
