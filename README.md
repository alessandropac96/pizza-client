# pizza-client
Test llm client 

## Setup
to use the library, you need to install the dependencies. 
Please use a venv to avoid conflicts with other projects. 
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
To use the library, you need to import the client and create an instance of it. 
```python
from pizza_client import OpenAIClient   

config = LLMClientConfigInput(log_level=LogLevels.DEBUG)
client = OpenAIMockClient(config)
```

## Testing
To run the tests, after installing the dependencies, you can run the following command.  
```bash
python3 -m unittest pizza_client/tests/test_module.py
```
You can also run the tests using the docker image. 
```bash
docker compose up pizza-client
```
