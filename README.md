---
title: Football Team Performance Profiler
emoji: ⚽
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
---

# Football Team Performance Profiler

A FastAPI application that assigns football teams to one of five historical
archetypes using the saved SECOND-SCOPE K-Means model. This is team profile
assignment, not future match prediction.

The web application lives in `huggingface_app/`. FastAPI's interactive API
documentation is available at `/docs` while the application is running.
