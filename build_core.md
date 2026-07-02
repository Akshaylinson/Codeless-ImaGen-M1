# Project Specification: CPU-Optimized AI Image Editing Platform

# Project Name

CodelessAI Smart Image Editor

---

# Project Vision

Build a production-ready, browser-based AI image editing platform capable of performing instruction-driven image editing entirely on CPU-only infrastructure.

The platform must run on commodity servers (4 vCPU, 16 GB RAM) without requiring GPUs.

Users should be able to upload an image, provide natural language editing instructions, and receive an edited image generated through a multi-stage AI pipeline.

Examples:

* "Remove the sunglasses."
* "Replace the apple with a golden trophy."
* "Remove the car from the background."
* "Change the shirt color to blue."
* "Replace the tree with a palm tree."
* "Remove the text from this image."

The system must intelligently understand the user's intent, identify the target object, precisely segment the object, and perform localized AI inpainting.

---

# Core Design Philosophy

The system must use a Stateful Micro-Execution Architecture.

Only one major AI model should remain in memory at a time.

Models are loaded from NVMe storage, executed, and immediately unloaded to minimize RAM consumption.

The architecture is optimized for CPU inference.

---

# High-Level Architecture

Frontend (HTML + Tailwind + Vanilla JS)

↓

FastAPI REST Backend

↓

Task Orchestrator

↓

Stage 1: Intent Extraction (LLM)

↓

Stage 2: Object Grounding (Vision Model)

↓

Stage 3: Segmentation (Mask Generation)

↓

Stage 4: AI Inpainting

↓

Image Post-Processing

↓

Final Result Storage

↓

Frontend Delivery

---

# Technology Stack

## Frontend

Plain HTML5

Tailwind CSS CDN

Vanilla JavaScript (ES Modules)

No React

No Vue

No build step

No npm dependencies

Use modular JavaScript architecture.

Recommended structure:

frontend/

index.html

assets/

css/

js/

components/

pages/

services/

utils/

---

## Backend

Python 3.12+

FastAPI

Uvicorn

Pydantic V2

Async architecture

---

## AI Runtime

### LLM Runtime

llama-cpp-python

GGUF model execution

CPU optimized

---

### Vision Runtime

ONNX Runtime

Optional OpenVINO acceleration

---

## Image Processing

Pillow

OpenCV

NumPy

---

## Background Tasks

FastAPI BackgroundTasks

Optional Celery support

---

## Storage

SQLite for development

PostgreSQL for production

Filesystem-based image storage

---

# Detailed AI Pipeline

# STAGE 1: Intent Extraction

Purpose:

Convert free-form user instructions into structured machine-readable JSON.

Example input:

"Replace the red apple with a blue diamond."

Expected output:

{
"action": "replace",
"target_object": "red apple",
"replacement_object": "blue diamond"
}

Supported actions:

remove

replace

add

change_color

enhance

blur

clean

restore

erase_text

Supported JSON schema:

{
"action": "",
"target_object": "",
"replacement_object": "",
"attributes": {
"color": "",
"style": ""
}
}

Use grammar-constrained JSON generation.

Model:

Qwen2.5-3B-Instruct GGUF

Inference library:

llama-cpp-python

Responsibilities:

Understand instruction.

Extract action.

Extract target object.

Extract replacement object.

Validate JSON.

Return structured response.

Unload model immediately after inference.

---

# STAGE 2: Object Localization

Purpose:

Locate the exact object requested by the user.

Input:

Original image

Target object string

Example:

"red apple"

Model:

Florence-2 Large ONNX

Task:

Caption-to-Phrase Grounding

Expected output:

{
"x1": 100,
"y1": 80,
"x2": 250,
"y2": 300
}

Requirements:

Support multiple object detection.

Support confidence score.

Return best matching object.

If multiple matches exist:

Ask user for clarification.

OR

Select highest confidence.

Unload model after completion.

---

# STAGE 3: Segmentation

Purpose:

Generate pixel-perfect object masks.

Input:

Original image

Bounding box

Model:

MobileSAM ONNX

Output:

Binary mask PNG.

White pixels:

Editable region.

Black pixels:

Protected region.

Requirements:

Support:

Single object.

Multiple objects.

Complex shapes.

Fine edges.

Hair.

Transparent regions.

Export:

mask.png

mask_preview.png

Unload model after execution.

---

# STAGE 4: AI Inpainting

Purpose:

Modify only selected regions.

Input:

Original image

Binary mask

Instruction

Replacement prompt

Model:

Stable Diffusion 1.5 Inpainting

LCM accelerated.

Runtime:

ONNX Runtime.

Capabilities:

Remove object.

Replace object.

Modify object.

Fill background naturally.

Preserve image identity.

Preserve lighting.

Preserve perspective.

Generation settings:

4-8 LCM steps.

CFG scale configurable.

Seed configurable.

Output:

edited_image.png

Unload model after generation.

---

# Image Processing Layer

Responsible for:

Image loading.

Resize.

Normalization.

Mask resizing.

Format conversion.

Thumbnail generation.

Metadata extraction.

Watermarking.

Compression.

Supported formats:

PNG

JPEG

WEBP

Maximum upload:

20 MB

Maximum resolution:

2048x2048

Automatically resize larger images.

---

# Backend Architecture

backend/

app/

api/

core/

services/

models/

schemas/

database/

workers/

ai/

storage/

utils/

middleware/

config/

main.py

---

# API Endpoints

## Authentication

POST /api/auth/login

POST /api/auth/logout

GET /api/auth/me

---

## Image Upload

POST /api/images/upload

Response:

{
"image_id": ""
}

---

## Start Editing

POST /api/edit/start

Request:

{
"image_id": "",
"instruction": ""
}

Response:

{
"job_id": ""
}

---

## Job Status

GET /api/jobs/{job_id}

Response:

{
"status": "queued",
"progress": 60
}

Statuses:

queued

processing

completed

failed

---

## Download Result

GET /api/jobs/{job_id}/result

---

## History

GET /api/history

---

## Delete Job

DELETE /api/jobs/{job_id}

---

# Background Execution Flow

User submits request.

Create Job record.

Set status = queued.

Worker begins processing.

Status updates:

10%

30%

50%

70%

100%

Final image stored.

Job marked completed.

Frontend notified.

---

# Database Design

Tables:

users

images

jobs

edit_requests

generated_images

activity_logs

---

# Job Table

id

user_id

image_id

instruction

status

progress

created_at

updated_at

error_message

output_path

processing_time

---

# File Storage Structure

storage/

uploads/

generated/

masks/

thumbnails/

temp/

logs/

---

# Frontend Features

# Landing Page

Project overview.

Features.

Upload CTA.

---

# Dashboard

Recent jobs.

Upload image.

View history.

Statistics.

---

# Editor Page

Image upload.

Instruction textbox.

Preview image.

Generate button.

Job progress indicator.

Before/After comparison slider.

Download button.

Retry button.

---

# Gallery Page

Display all generated images.

Search history.

Delete images.

Favorites.

---

# Admin Panel

View jobs.

Monitor queue.

Monitor failures.

System statistics.

Storage usage.

CPU usage.

RAM usage.

Logs.

---

# Frontend Components

Navbar

Sidebar

UploadZone

ImagePreview

PromptInput

JobProgress

ComparisonSlider

HistoryGrid

ToastNotification

Modal

Loader

EmptyState

Pagination

---

# Security Requirements

Validate uploads.

Limit file size.

Rate limiting.

CORS protection.

Secure headers.

Sanitize filenames.

Prevent path traversal.

JWT authentication.

Image MIME validation.

Reject unsupported files.

---

# Logging Requirements

Every stage must log:

Model loaded.

Model unloaded.

Execution time.

RAM usage.

Errors.

Inference duration.

Store logs in:

logs/system.log

logs/inference.log

logs/error.log

---

# Monitoring

Expose:

/health

/metrics

CPU usage.

RAM usage.

Disk usage.

Queue size.

Active jobs.

---

# Performance Requirements

Target server:

4 vCPU

16 GB RAM

SSD/NVMe storage

Maximum concurrent jobs:

2

Average processing time:

20-60 seconds.

Peak RAM:

Less than 8 GB.

---

# AI Service Layer Design

Create independent service classes.

IntentService

GroundingService

SegmentationService

InpaintingService

StorageService

JobService

Each service must:

load_model()

predict()

cleanup()

unload_model()

This architecture ensures memory is always released.

Example:

with IntentService() as service:

result = service.predict()

The service should automatically unload itself after completion.

---

# Final Processing Pipeline

1. Receive image.

2. Save image.

3. Create job.

4. Parse instruction.

5. Ground object.

6. Generate mask.

7. Run inpainting.

8. Post-process image.

9. Save result.

10. Update job.

11. Return final image.

The entire system must be modular, production-ready, extensible, and optimized for CPU-only execution without requiring any GPU resources.
