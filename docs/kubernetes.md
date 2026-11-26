# Kubernetes deployment (Minikube)

This deployment is intended for local Kubernetes development and evaluation. It
uses Kubernetes Secrets, persistent volume claims, probes, resource requests and
limits, restrictive pod security contexts, NetworkPolicies, and an ingress. It
is not a highly available production cluster: MongoDB, Kafka, Mosquitto, the
backend, and WebSocket service each run as a single instance. In particular,
backend and WebSocket must remain at one replica because desk state and active
WebSocket connections are process-local.

## Prerequisites

- Docker
- Minikube
- `kubectl`
- OpenSSL
- A terminal with `minikube`, `kubectl`, and `openssl` on `PATH`

The NetworkPolicies require a CNI that enforces them. Start Minikube with
Calico, and enable the ingress controller and metrics server:

```powershell
minikube start --cni=calico
minikube addons enable ingress
minikube addons enable metrics-server
kubectl config use-context minikube
```

If you already created a Minikube cluster with another CNI, recreate it with
Calico before applying these manifests.

## Build application images

From the repository root, build the images into Minikube's image store:

```powershell
minikube image build -t dus-backend:local -f infra/k8s/Dockerfile.backend .
minikube image build -t dus-frontend:local -f infra/k8s/Dockerfile.frontend .
```

The manifests use these local image tags with `imagePullPolicy: IfNotPresent`.
Rebuild the images and restart the corresponding Deployment after changing
application code.

## Create credentials and MQTT certificates

Create the namespace before its Secrets. Generate unique values locally; the
following PowerShell example uses OpenSSL-generated hex strings and does not
store them in the repository:

```powershell
kubectl create namespace dus --dry-run=client -o yaml | kubectl apply -f -
$mongoUser = "dus"
$mongoPassword = (openssl rand -hex 24).Trim()
$jwtSecret = (openssl rand -hex 32).Trim()
kubectl create secret generic dus-secrets --namespace dus `
  --from-literal=mongo-root-username=$mongoUser `
  --from-literal=mongo-root-password=$mongoPassword `
  --from-literal=jwt-secret=$jwtSecret
```

Mosquitto requires a CA and a server certificate, supplied as the `mqtt-tls`
Secret. Create a local CA and a server certificate with DNS names matching the
in-cluster service:

```powershell
openssl genrsa -out ca.key 3072
openssl req -x509 -new -key ca.key -sha256 -days 3650 `
  -subj "/CN=dus-mqtt-ca" `
  -addext "basicConstraints=critical,CA:TRUE" `
  -addext "keyUsage=critical,keyCertSign,cRLSign" -out ca.crt
openssl genrsa -out tls.key 2048
openssl req -new -key tls.key -subj "/CN=mqtt.dus.svc.cluster.local" -out mqtt.csr
@"
subjectAltName=DNS:mqtt,DNS:mqtt.dus,DNS:mqtt.dus.svc,DNS:mqtt.dus.svc.cluster.local
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
"@ | Set-Content -Encoding ascii mqtt-server.ext
openssl x509 -req -in mqtt.csr -CA ca.crt -CAkey ca.key -CAcreateserial `
  -out tls.crt -days 825 -sha256 -extfile mqtt-server.ext
kubectl create secret generic mqtt-tls --namespace dus `
  --from-file=ca.crt=ca.crt --from-file=tls.crt=tls.crt --from-file=tls.key=tls.key
```

The broker requires client-certificate authentication. For a test client,
generate a separate certificate signed by the same CA; its common name becomes
the MQTT username used by the configured topic ACL:

```powershell
openssl genrsa -out client.key 2048
openssl req -new -key client.key -subj "/CN=pico-001" -out client.csr
@"
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=clientAuth
"@ | Set-Content -Encoding ascii mqtt-client.ext
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial `
  -out client.crt -days 825 -sha256 -extfile mqtt-client.ext
```

Do not commit the generated private keys or certificate files. Kubernetes
Secrets are namespace-scoped and should be treated as sensitive; for a
production cluster, use a managed secret store, encryption at rest, and a
certificate issuance/rotation process. These self-signed certificates are for
local evaluation only.

## Deploy

Apply the Kustomize package:

```powershell
kubectl apply -k infra/k8s
kubectl -n dus get pods,pvc,services,ingress
kubectl -n dus rollout status statefulset/mongodb
kubectl -n dus rollout status statefulset/kafka
kubectl -n dus rollout status statefulset/mqtt
kubectl -n dus rollout status deployment/backend
kubectl -n dus rollout status deployment/websocket
kubectl -n dus rollout status deployment/frontend
```

The backend waits for MongoDB and the WebSocket service creates its Kafka topics
before starting. If a workload does not become ready, inspect it with
`kubectl -n dus describe pod <pod-name>` and `kubectl -n dus logs <pod-name>`.
MongoDB, Kafka, and Mosquitto each use a persistent volume claim. Do not delete
those claims unless you intend to delete the stored data.

Set `dus.local` to the Minikube IP in the Windows hosts file
(`C:\Windows\System32\drivers\etc\hosts`), for example:

```text
<minikube-ip> dus.local
```

Get the address with `minikube ip`. The Ingress is HTTP-only by default and is
for local use. For HTTPS, configure an Ingress TLS Secret and update the
frontend Deployment's `ORIGIN` to the external `https://` origin; the current
`ORIGIN` value is `http://dus.local`.

## Manual smoke tests

1. Open `http://dus.local/` and confirm the frontend loads.
2. Open `http://dus.local/api/docs` and confirm the backend OpenAPI page loads.
   The backend readiness endpoint is `http://dus.local/api/healthz/ready`.
3. Use the tracking API in OpenAPI to create or update desk state. Restart the
   backend with `kubectl -n dus rollout restart deployment/backend`, wait for
   rollout completion, and verify the state remains available. The snapshots
   and measurement history are stored in MongoDB.
4. Open the WebSocket test page in the frontend and send a message between two
   browser sessions. WebSocket connections are not shared across replicas, so
   keep the WebSocket Deployment at one replica.
5. To verify the MQTT TLS listener, port-forward the service in one terminal:

   ```powershell
   kubectl -n dus port-forward service/mqtt 8883:8883
   ```

   In another terminal, with a Mosquitto client installed, publish using the
   generated CA and client certificate:

   ```powershell
   mosquitto_pub -h localhost -p 8883 --cafile ca.crt `
     --cert client.crt --key client.key `
     -t pico/pico-001/test -m smoke-test
   ```

   The project does not yet include a backend MQTT ingestion subscriber, so
   this verifies broker TLS and authorization only, not Pico-to-database
   ingestion.
6. Confirm the frontend HPA reports metrics with
   `kubectl -n dus get hpa frontend`. Metrics may take a few minutes to appear.

The frontend is autoscaled from one to three replicas when metrics are
available. Backend and WebSocket scaling is intentionally disabled until their
state is moved to shared storage or coordinated between replicas. Kafka is a
single combined KRaft broker/controller with cluster-internal plaintext
traffic, suitable only for this local cluster.

## Remove the deployment

Remove the deployment:

```powershell
kubectl delete -k infra/k8s
```

This deletes the namespace and its PVCs, which may delete the MongoDB, Kafka,
and MQTT data depending on the storage provisioner's reclaim policy. Back up
data first if it must be retained.
