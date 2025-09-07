# API Contracts

## POST `/api/ingest`
Request body:
```json
{
  "niches": ["tech"],
  "top_percentile": 0.05
}
```
Response body:
```json
{
  "message": "ingestion_complete",
  "items": [{
    "niche": "tech",
    "title": "Video title",
    "url": "https://...",
    "transcript": "...",
    "analysis": {"pacing": "1s", "style": "lo-fi", "on_screen_text": []}
  }]
}
```

## POST `/api/strategy`
Request body:
```json
{ "niches": ["tech"] }
```
Response body:
```json
{ "patterns": ["Use fast cuts", "Hook with a question"] }
```

## POST `/api/generate`
Request body:
```json
{ "prompt": "My AI SaaS", "niche": "tech" }
```
Response body:
```json
{
  "script": "...",
  "storyboard": ["https://image1", "https://image2"],
  "notes": ["Use upbeat music"],
  "variations": {"tiktok": "...", "instagram": "..."}
}
```
