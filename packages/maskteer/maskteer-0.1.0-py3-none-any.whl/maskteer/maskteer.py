import re
import yaml
import os

DEFAULT_CONFIG = {
    'patterns': [
        r'\b[\w.-]+@[\w.-]+\.\w+\b',    # email
        r'\b\d{3}-\d{3}-\d{4}\b',       # phone
        r'(?i)password=[^\s]+',         # password
        r'(?i)token=[^\s]+',            # token
        r'(?i)api_key=[^\s]+',          # api_key
        r'(?i)secret=[^\s]+',           # secret
    ],
    'mask': '[PRIVATE]',
}

class Maskteer:
    def __init__(self, config_file=None):
        if config_file:
            if not os.path.exists(config_file):
                raise FileNotFoundError(f"Config file not found: {config_file}")

            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = DEFAULT_CONFIG

        env_patterns = os.getenv('MASKTEER_PATTERNS')
        env_mask = os.getenv('MASKTEER_MASK')

        if env_patterns:
            additional_patterns = [pat.strip() for pat in env_patterns.split(',')]
            self.config['patterns'].extend(additional_patterns)

        if env_mask:
            self.config['mask'] = env_mask

    def mask_text(self, text):
        for pattern in self.config['patterns']:
            text = re.sub(pattern, self.config['mask'], text)
        return text
