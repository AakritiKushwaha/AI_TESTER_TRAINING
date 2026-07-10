# API Contract Validator - Langflow UI

A lightweight React+Vite application for validating API contracts against JSON schemas. The app sends requests to a Langflow endpoint to perform intelligent API contract validation using LLMs.

## Features

- **Curl or URL Input**: Share a request curl command or simple API URL
- **JSON Schema Validation**: Provide the expected JSON schema for your API response
- **Langflow Integration**: Automatically calls your Langflow instance to validate the contract
- **Light Theme UI**: Clean, minimal interface with soft colors and good readability
- **Session Support**: Optional session ID for conversation continuity
- **API Key Support**: Optional API key authentication for Langflow

## Prerequisites

- Node.js (v14+)
- npm or yarn
- Langflow running locally on port 7862
- Langflow flow ID: `6f5358c8-cab1-4f75-95cf-8940426178b8`

## Installation

```bash
cd UI
npm install
```

## Running the App

Start the development server:

```bash
npm run dev
```

The app will be available at **http://localhost:3000**

## How to Use

1. **Enter Request Curl or API URL**:
   - You can paste a full curl command: `curl "https://api.example.com/users"`
   - Or just the URL: `https://api.example.com/users`

2. **Provide JSON Schema**:
   - Enter your expected JSON schema in the text area
   - The app will validate the live API response against this schema

3. **Optional: Add API Key**:
   - If your Langflow instance requires authentication, enter the API key
   - This will be sent as `x-api-key` header

4. **Optional: Add Session ID**:
   - For conversation continuity, you can provide a session ID
   - Langflow will use this to maintain context

5. **Click "Validate Contract"**:
   - The app extracts the API URL from your curl command
   - Sends the request to Langflow for validation
   - Displays the validation results

## Response Structure

The app sends the following payload to Langflow:

```json
{
  "output_type": "chat",
  "input_type": "chat",
  "input_value": "Please perform API Contract validation for following:\ncurl \"<API_URL>\"\n\nJSON Schema\n<YOUR_SCHEMA>",
  "session_id": "<optional>"
}
```

## Configuration

The Langflow endpoint is hardcoded as:
```
http://localhost:7862/api/v1/run/6f5358c8-cab1-4f75-95cf-8940426178b8?stream=false
```

To change the endpoint or flow ID, edit [src/App.jsx](src/App.jsx) and update the `langflowUrl` variable.

## Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
UI/
├── src/
│   ├── App.jsx         # Main application component
│   ├── main.jsx        # React entry point
│   └── index.css       # Light theme styles
├── public/             # Static assets
├── index.html          # HTML entry point
├── package.json        # Dependencies
├── vite.config.js      # Vite configuration
└── README.md           # This file
```

## Technologies

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Ajv**: JSON Schema validation library
- **CSS3**: Light theme styling

## Notes

- The app extracts API URLs from curl commands using regex
- All API calls are made from the browser to Langflow
- Validation results from Langflow are parsed and displayed in a readable format
- The light color theme ensures comfortable viewing in any environment
