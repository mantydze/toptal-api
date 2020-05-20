# toptal-api

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt

python run.py --config_path development-config.json
```

### Tests
```
coverage run --omit 'venv/*' tests.py --config_path testing-config.json && coverage html
```