# ChatGPT Custom GPT Setup Guide

This guide will help you create a ChatGPT custom GPT that can invoke your Pinterest Home Feed API with API key authentication.

## Step 1: API Key Authentication Setup

Your Pinterest Feed API now requires API key authentication for the `api/home_feed/` endpoint.

### Creating an API Key

1. **Access Django Admin**:
   ```bash
   python3 manage.py createsuperuser  # If you haven't created one yet
   python3 manage.py runserver
   ```
   
2. **Navigate to**: `http://localhost:8000/admin/`

3. **Go to**: Home_feed → API Keys → Add API Key

4. **Create a new API Key**:
   - **Name**: "ChatGPT Custom GPT"
   - **Is Active**: ✓ Checked
   - Click "Save"

5. **Copy the generated API key** (it will look like: `abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx1234yz5678901234567890`)

## Step 2: Custom GPT Configuration

### Basic Information
- **Name**: Pinterest Home Feed Assistant
- **Description**: Get random Pinterest-style images for inspiration and creative projects

### Instructions
```
You are a Pinterest Home Feed Assistant that helps users get random Pinterest-style images. You can fetch image feeds using the home_feed API.

When users ask for images, use the home_feed API to get random images. You can specify how many images to return (1-10).

The API returns image data including:
- Image source URL (src)
- Alt text description
- Origin URL
- Fallback URLs if needed

Always present the images in a user-friendly way and provide the alt text descriptions.
```

### Conversation Starters
- "Show me some random images for inspiration"
- "Get me 5 random Pinterest-style images"
- "I need some creative visual inspiration"
- "Fetch some random images for my project"

## Step 3: Actions Configuration

### Authentication
- **Authentication Type**: API Key
- **API Key**: `YOUR_GENERATED_API_KEY_HERE`
- **Auth Type**: Custom
- **Custom Header Name**: `Authorization`
- **Custom Header Value**: `Api-Key YOUR_GENERATED_API_KEY_HERE`

### Schema (OpenAPI 3.0.1)
```json
{
  "openapi": "3.0.1",
  "info": {
    "title": "Pinterest Home Feed API",
    "description": "API for fetching random Pinterest-style images",
    "version": "v1.0.0"
  },
  "servers": [
    {
      "url": "https://your-domain.com"
    }
  ],
  "paths": {
    "/api/home_feed/": {
      "get": {
        "description": "Get random images from the home feed",
        "operationId": "getHomeFeed",
        "parameters": [
          {
            "name": "count",
            "in": "query",
            "description": "Number of images to return (1-10)",
            "required": false,
            "schema": {
              "type": "integer",
              "minimum": 1,
              "maximum": 10,
              "default": 1
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "message": {
                      "type": "string"
                    },
                    "total_available": {
                      "type": "integer"
                    },
                    "count": {
                      "type": "integer"
                    },
                    "images": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "src": {
                            "type": "string",
                            "format": "uri"
                          },
                          "alt": {
                            "type": "string"
                          },
                          "origin": {
                            "type": "string",
                            "format": "uri"
                          },
                          "fallback_urls": {
                            "type": "array",
                            "items": {
                              "type": "string",
                              "format": "uri"
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "401": {
            "description": "Authentication failed"
          },
          "400": {
            "description": "Bad request"
          }
        },
        "security": [
          {
            "ApiKeyAuth": []
          }
        ]
      }
    }
  },
  "components": {
    "securitySchemes": {
      "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
      }
    }
  }
}
```

## Step 4: Testing the API

### Manual Test with curl
```bash
curl -X GET "https://your-domain.com/api/home_feed/?count=3" \
  -H "Authorization: Api-Key YOUR_GENERATED_API_KEY_HERE" \
  -H "Content-Type: application/json"
```

### Expected Response
```json
{
  "message": "Images retrieved successfully",
  "total_available": 45,
  "count": 3,
  "images": [
    {
      "src": "https://example.com/image1.jpg",
      "alt": "Beautiful landscape",
      "origin": "https://pinterest.com/pin/123456789",
      "fallback_urls": []
    },
    {
      "src": "https://example.com/image2.jpg",
      "alt": "Creative design",
      "origin": "https://pinterest.com/pin/987654321",
      "fallback_urls": []
    },
    {
      "src": "https://example.com/image3.jpg",
      "alt": "Inspiring artwork",
      "origin": "https://pinterest.com/pin/456789123",
      "fallback_urls": []
    }
  ]
}
```

## Step 5: Deploy Your API

Make sure your API is deployed and accessible from the internet. Update the server URL in the OpenAPI schema to match your deployed domain.

### Common Deployment Options:
- AWS (using your existing deployment plan)
- Heroku
- Digital Ocean
- Railway
- Render

## Step 6: Privacy and Usage

### Privacy Settings
- **Data Usage**: Only use data for improving the GPT's responses
- **Share Conversations**: Disable if you want to keep conversations private

### Rate Limiting
Consider implementing rate limiting on your API to prevent abuse.

## Troubleshooting

### Common Issues:

1. **Authentication Failed (401)**
   - Check that your API key is correct
   - Ensure the header format is: `Authorization: Api-Key YOUR_KEY`
   - Verify the API key is active in Django admin

2. **No Images Available**
   - Run the scraping task to populate images: `python3 manage.py scrape_images`
   - Check that images exist in the database via Django admin

3. **Connection Errors**
   - Verify your API is deployed and accessible
   - Check the server URL in the OpenAPI schema
   - Ensure CORS is properly configured if needed

## Security Notes

- Keep your API key secure and don't share it publicly
- Consider implementing request logging for monitoring
- Set up alerts for unusual API usage patterns
- Rotate API keys periodically

## Next Steps

After setting up your custom GPT:
1. Test it with various queries
2. Monitor API usage through Django admin
3. Consider adding more features like image filtering or categories
4. Set up proper logging and monitoring for production use