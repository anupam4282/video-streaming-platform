# StreamBox — Video Streaming Platform

## Stack
Python, Flask, SQLite, FFmpeg/ffprobe, AWS S3 (optional), HTML5/CSS/JavaScript.

## Features
- Register/login with hashed passwords
- Upload and stream videos
- Dashboard for uploaded videos
- Search videos
- Edit title/description
- Delete own videos
- View counter
- FFmpeg metadata extraction
- Local storage by default
- Optional AWS S3 storage
- Responsive interface

## Run locally
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

FFmpeg is recommended. Without it, the app still works, but duration/resolution metadata may be 0.

## AWS S3
Copy `.env.example` to `.env` and set AWS_S3_BUCKET, AWS_REGION, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. If the bucket is empty, local `uploads/` storage is used.

For cloud deployment, S3 is recommended because many hosts have temporary local disks.

## Production
Use:
```bash
gunicorn app:app
```

Before production, add CSRF protection, rate limiting, upload scanning, HLS/transcoding queues, thumbnails, and stricter S3 IAM permissions.
