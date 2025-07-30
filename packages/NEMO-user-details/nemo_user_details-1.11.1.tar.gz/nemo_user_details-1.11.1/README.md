[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/NEMO-user-details?label=python)](https://www.python.org/downloads/release/python-3110/)
[![PyPI](https://img.shields.io/pypi/v/nemo-user-details?label=pypi%20version)](https://pypi.org/project/NEMO-User-Details/)

# NEMO User Details

This plugin for NEMO adds extra fields to users.

The following fields can be enabled in `Customization -> User details`:
* employee id
* ORCID
* Scopus ID
* Researcher ID (Web of Science)
* Google scholar ID
* phone number
* emergency contact
* groups (from django authentication groups)
* gender
* race
* ethnicity
* education level

If `groups` are enabled, there will also be a new option in `email broadcast` to email based on the groups they belong to.

# Installation

`pip install NEMO-user-details`

`django-admin migrate NEMO_user_details`

# Add NEMO User Details

in `settings.py` add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    '...',
    'NEMO_user_details',
    '...'
]
```

to track changes to details with auditlog, in `settings.py` add to `AUDITLOG_INCLUDE_TRACKING_MODELS`:
```python
AUDITLOG_INCLUDE_TRACKING_MODELS = (
    '...',
    "NEMO_user_details.UserDetails",
    '...',
)
```

# Usage
Go to `Detailed administration` to add choices for each field if needed (groups, gender, ethnicity, race, education level).

Then go to `Customization -> User details` and select which fields you want to enable and require.

Then simply navigate to the `User` page in the `Administration` menu and the new fields will be available.

### NEMO Compatibility

NEMO >= 5.5.0 & NEMO-CE >= 2.4.0 ----> NEMO-user-details >= 1.9.0

NEMO >= 4.7.0 & NEMO-CE >= 1.7.0 ----> NEMO-user-details >= 1.7.0

NEMO >= 4.5.0 & NEMO-CE >= 1.2.0 ----> NEMO-user-details >= 1.6.0
