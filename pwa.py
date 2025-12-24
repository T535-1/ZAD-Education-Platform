# -*- coding: utf-8 -*-
import streamlit as st
import base64

def setup_pwa():
    """
    Injects PWA meta tags and Service Worker registration.
    """
    # In a real deployment, these files should be served from the root or a static folder.
    # For this prototype, we'll assume they are accessible or inject the manifest directly if needed.
    
    # Inject Manifest Link
    st.markdown("""
    <link rel="manifest" href="assets/manifest.json">
    <meta name="theme-color" content="#4B0082">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    """, unsafe_allow_html=True)

    # Register Service Worker
    st.markdown("""
    <script>
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', function() {
        navigator.serviceWorker.register('assets/sw.js').then(function(registration) {
          console.log('ServiceWorker registration successful with scope: ', registration.scope);
        }, function(err) {
          console.log('ServiceWorker registration failed: ', err);
        });
      });
    }
    </script>
    """, unsafe_allow_html=True)
