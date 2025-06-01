
NUM_CLIENTS=${1:-3}

stress_client() {
  while true; do
    img=$(find images/ -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | shuf -n 1)
    echo "[$(date +"%T")] Client $$ gửi ảnh: $img"
    curl --max-time 5 -F "file=@$img" http://127.0.0.1:8000/search
    echo ""
  done
}

for ((i=1;i<=NUM_CLIENTS;i++)); do
  stress_client &
done

wait
