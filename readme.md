# aplikaceOS

Jednoduchá Flask aplikace s více-stránkovým formulářem (2+ stránek), kontejnerizovaná pomocí Dockeru a připravená pro Kubernetes.

Struktura:
- `src/`  aplikace
- `src/templates/`  HTML šablony
- `Dockerfile`, `requirements.txt`
- `k8s/deployment.yaml`
- `claudie.yaml`  (existující manifest v repu)

Lokální build & run:
docker build -t aplikaceos .
docker run -e FLASK_SECRET="muj-tajny-klic" -p 8080:8080 aplikaceos
Otevřít: http://localhost:8080/page1

Kubernetes:
Upravte `k8s/deployment.yaml` s obrazem v registru a použijte:
kubectl apply -f k8s/deployment.yaml

Bezpečnost: místo pevného `FLASK_SECRET` v manifestu použijte K8s Secret.
