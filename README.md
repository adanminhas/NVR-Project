# Network Video Recorder (NVR) Project

A custom Network Video Recorder (NVR) system built to manage IP camera video streams using a FastAPI backend and a web-based frontend.

This project is designed to be used as part of a DIY home surveillance system.

## Features
- Manage and monitor multiple IP camera streams
- Live video streaming and recording using FFmpeg
- Automatic stream health checks and recovery
- HLS (HTTP Live Streaming) support
- Web-based frontend for live viewing and control

## Tech Stack
**Backend**
- Python
- FastAPI
- FFmpeg
- Linux

**Frontend**
- Vue.js
- HTML / CSS / JavaScript

## Architecture Overview
- FastAPI backend manages camera configuration and stream control
- FFmpeg handles video ingestion, transcoding, and HLS output
- Health check system monitors streams and automatically restarts failed processes
- Frontend communicates with backend via REST APIs to display live streams

## Motivation
This project was built to gain hands-on experience with backend systems, video streaming, and full-stack development.  
An additional motivation was to deploy the system as part of a personal DIY home surveillance setup, allowing direct practical use and real-world testing of reliability, performance, and fault tolerance.

## Status
Active development — planned improvements include authentication, recording management, and UI enhancements.

## Author
**Adan Minhas**  
Computer Science student at Queen Mary University of London  
GitHub: https://github.com/adanminhas
