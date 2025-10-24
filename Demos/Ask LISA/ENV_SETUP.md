# Using .env file with Ask LISA (Python)

## Step 1: Install python-dotenv

The Python version needs the `python-dotenv` package to load `.env` files:

```bash
pip install python-dotenv
```

## Step 2: Update app.py to load .env

Add these lines at the **top** of `app.py`:

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
```

## Step 3: Configure your .env file

1. Open the `.env` file I created
2. Replace `sk-your-openai-api-key-here` with your actual OpenAI API key
3. Save the file

Your `.env` file should look like:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Step 4: Run the application

```bash
python app.py
```

The application will automatically load the API key from the `.env` file.

## Alternative: Use environment variables without .env file

If you don't want to use a `.env` file, you can set the environment variable directly:

### PowerShell:
```powershell
$env:OPENAI_API_KEY = "sk-your-api-key-here"
python app.py
```

### Command Prompt:
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
python app.py
```

### Linux/Mac:
```bash
export OPENAI_API_KEY=sk-your-api-key-here
python app.py
```

## Security Notes

- ✅ The `.env` file is now in `.gitignore` to prevent accidental commits
- ✅ Never commit API keys to version control
- ✅ Use `.env.template` as a reference (without actual keys)
- ✅ Share `.env.template` with your team, not `.env`

## For the Blazor version

The Blazor version uses a different approach:
- Configuration is in `appsettings.Development.json`
- Already set up and ready to use
- Just edit the file and add your API key
