# API Configuration

This project uses environment variables to securely store API credentials.

## Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Add your Live Score API credentials to the `.env` file:
   ```
   LIVESCORE_API_KEY=your_actual_api_key
   LIVESCORE_API_SECRET=your_actual_api_secret
   ```

3. The `.env` file is automatically ignored by git to keep your credentials secure.

## Important Security Notes

- Never commit the `.env` file to version control
- Never hardcode API keys in your source code
- The `.env.example` file shows the required environment variables without exposing secrets