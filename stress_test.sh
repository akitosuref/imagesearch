for i in {1..100}; do
  curl -F "file=@n02088094_4261.JPEG" http://0.0.0.0:8000/search &
done