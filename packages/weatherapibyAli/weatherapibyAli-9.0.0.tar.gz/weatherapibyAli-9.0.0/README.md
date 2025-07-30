# Wether App
## Install IT:
`pip install weatherapibyAli`

## Get an API Key:
[Click here to get your API Key](https://openweathermap.org/)
Register on the page, then click your username at the top. Select "My API keys" and copy the default API key.

## Example Code:
```python
from weatherapibyAli import WeatherApp
WeatherApp.run("Your Api Key")
```

## Py to EXE Tutorial

You can convert your Python script to a Windows executable using the `auto-py-to-exe` package. Here’s how:

1. **Install auto-py-to-exe:**
    ```
    pip install auto-py-to-exe
    ```

2. **Launch auto-py-to-exe:**
    ```
    auto-py-to-exe
    ```

3. **Configure your build:**
    - In the GUI, select your Python script.
    - Choose "One File" to bundle everything into a single executable.
    - Adjust other settings as needed.

4. **Start the build:**
    - Click the "Convert .py to .exe" button.
    - After the process completes, you’ll find the executable in the `output` folder.

For more details, check the [auto-py-to-exe documentation](https://github.com/brentvollebregt/auto-py-to-exe).