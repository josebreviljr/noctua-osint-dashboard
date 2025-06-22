from dashboard import app
from flask import Request, Response
import json

def onRequest(context):
    """
    Cloudflare Pages serverless function handler.
    This function forwards all requests to the Flask app.
    """
    # Create a Flask request object from the Cloudflare context
    request = Request.from_values(
        path=context.request.url,
        method=context.request.method,
        headers=dict(context.request.headers),
        data=context.request.body if hasattr(context.request, 'body') else None
    )
    
    # Let the Flask app handle the request
    with app.request_context(request.environ):
        response = app.full_dispatch_request()
        
        # Convert Flask response to Cloudflare format
        return {
            'status': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        } 