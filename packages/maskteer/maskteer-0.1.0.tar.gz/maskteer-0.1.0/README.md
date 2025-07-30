# Maskteer

Automatically mask sensitive information from logs or outputs for Django, Flask, and FastAPI applications.


## Installation

```bash
pip install maskteer
```

## Usage

### Django

In `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'maskteer': {
            'level': 'DEBUG',
            'class': 'maskteer.handler.MaskteerHandler',
        },
    },
    "loggers" : {
        "root": {
            "handlers": ["maskteer"], 
            "level": "DEBUG",
            "propagate": True
        }
    },
}
```


### Flask


```python
from flask import Flask
from maskteer.handler import MaskteerHandler

app = Flask(__name__)

handler = MaskteerHandler(config_file='path/to/your/config.yml')
app.logger.addHandler(handler)
```


### FastAPI

```python
from fastapi import FastAPI
from maskteer.handler import MaskteerHandler

app = FastAPI()

handler = MaskteerHandler(config_file='path/to/your/config.yml')
app.logger.addHandler(handler)
```

## Configuration

You can configure via YAML file or environment variables:
```yaml
patterns:
  - "\\b[\\w.-]+@[\\w.-]+\\.\\w+\\b"
  - "(?i)password=[^\\s]+"
mask: "[REDACTED]"
```

Environment Variables:
```bash
export MASKTEER_PATTERNS="token=[^\\s]+,api_key=[^\\s]+"
export MASKTEER_MASK="[HIDDEN]"
```

## License

MIT License
