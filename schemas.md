# Schemas
Make id a composite id: town_council_1234_2026

## Assignments
id|meeting_id|body|published_date|materials|status
---|---|---|---|---|---
town_council_1234_2026|"1234"|"Town Council"|DATE|url|"pending"

### Assignments JSON
```json
  {
    "town_council_1234_2025": 
      {
      "meeting_id": "1234",
      "body": "Town Council",
      "published_date": "2026-03-06",
      "materials": "/link/to/html",
      "status": "pending"
      }
  }
```
get_rss() needs to return this format without "status", which is added later by assign()

## Source Materials
id|meeting_id|document_link|document_type|transcription
---|---|---|---|---
1|town_council_1234_2026|url|"minutes"|TEXT
2|town_council_1234_2026|url|"agenda"|TEXT
3|town_council_1234_2026|url|"votes"|TEXT
4|town_council_1234_2026|NULL|"zoom_recording"|TEXT

## Articles
id|meeting_id|meeting_date|summary_type|summary
---|---|---|---|---
1|town_council_1234_2025|DATE|"minutes"|TEXT/HTML
2|town_council_1234_2025|DATE|"agenda"|TEXT/HTML

