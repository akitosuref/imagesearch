
NUM_CLIENTS=${1:-3}

stress_client() {
  for ((j=1;j<=25;j++)); do
    img="images/train/basset/n02088238_1203.JPEG"
    echo "[$(date +"%T")] Client $$ gửi ảnh: $img"
    curl --max-time 5 -F "file=@$img" http://host.docker.internal/search
    echo ""
  done
}

for ((i=1;i<=NUM_CLIENTS;i++)); do
  stress_client &
done

wait
