# blankit: PII detection and removal in python

A lightweight package for detecting and removing Personally Identifiable Information (PII). 

blankit currently uses [GLiNER](https://github.com/urchade/GLiNER) as a backend to remove different types of PII

## PII types
Due to the versatility of GLiNER, blankit can essentially detect any PII type, though by default it supports the following:
- Name
- Location
- Ethnicity
- Gender
- Business Name
- Email address
- Phone number

However, you can specify your own PII types for more bespoke applications if needed.

## Getting started

### Installation
Install the package either from this repo or via your favourite package manager, such as `conda` or `uv`

`uv add blankit`

### Detecting PII

Detect and remove PII as follows:

```
from blankit.scanner import Scanner

text = "My name's gary and i live in fairfield with bruz and mugsy"

scanner = Scanner(pii_types=['Name', 'Location'])

# extract all the pii
entities = scanner.find_pii(text)

# remove pii from the text
text_redacted = scanner.redact(text)
```

