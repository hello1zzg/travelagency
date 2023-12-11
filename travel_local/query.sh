#！/bin/bash
oid=$(cat ./data/oid.txt)
curl 10.77.70.173:8999/grafana/getResByOid/${oid}
