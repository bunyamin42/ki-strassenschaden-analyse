{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [6.4355, 51.1941] 
      },
      "properties": {
        "image_id": "mapillary_abc123",
        "image_url": "https://scontent.mapillary.com/.../image.jpg",
        "timestamp": "2025-08-14T10:30:00Z",
        "overall_severity": "Hoch",
        "detections": [
          {
            "damage_class": "Schlagloch",
            "confidence": 0.94,
            "bounding_box": {
              "x_min": 120,
              "y_min": 340,
              "x_max": 250,
              "y_max": 480
            }
          },
          {
            "damage_class": "Netzrisse",
            "confidence": 0.82,
            "bounding_box": {
              "x_min": 400,
              "y_min": 500,
              "x_max": 600,
              "y_max": 700
            }
          }
        ]
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [6.4358, 51.1943]
      },
      "properties": {
        "image_id": "mapillary_xyz789",
        "image_url": "https://scontent.mapillary.com/.../image2.jpg",
        "timestamp": "2025-08-14T10:30:05Z",
        "overall_severity": "Niedrig",
        "detections": []
      }
    }
  ]
}
