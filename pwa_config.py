
import streamlit as st
import base64
from pathlib import Path

def inject_pwa_config():
    """
    Injects the necessary HTML meta tags and manifest link to make the
    Streamlit app a Progressive Web App (PWA).
    """
    
    # Path to the manifest file
    manifest_path = "assets/manifest.json"
    icon_path = "assets/icon-192x192.png" # A default icon

    # Create a dummy icon if it doesn't exist to prevent 404 errors
    if not Path(icon_path).exists():
        Path(icon_path).parent.mkdir(exist_ok=True)
        # A simple 1x1 transparent png
        png_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")
        with open(icon_path, "wb") as f:
            f.write(png_data)

    pwa_tags = f"""
    <head>
        <!-- PWA Meta Tags -->
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="theme-color" content="#4A90E2">
        
        <!-- Link to Manifest -->
        <link rel="manifest" href="/app/{manifest_path}">
        
        <!-- iOS App Icons -->
        <link rel="apple-touch-icon" href="/app/{icon_path}">
    </head>
    """
    st.markdown(pwa_tags, unsafe_allow_html=True)
