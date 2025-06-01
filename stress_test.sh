#!/bin/bash
for i in {1..100}; do
  echo "Request $i:"
  curl --max-time 5 -F "file=@1.jpg" http://127.0.0.1:8000/search
  echo ""
done