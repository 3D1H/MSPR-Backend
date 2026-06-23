# COFRAP - Commandes principales

## Vérification du cluster

```bash
sudo kubectl get nodes
sudo kubectl get pods -A
sudo kubectl get svc -A
```

---

## Vérification OpenFaaS

```bash
faas-cli list --gateway http://127.0.0.1:31112

sudo kubectl get pods -n openfaas
sudo kubectl get pods -n openfaas-fn
```

---

## Vérification PostgreSQL

```bash
sudo kubectl get pods
sudo kubectl get svc
sudo kubectl get pvc
```

---

## Connexion à PostgreSQL

```bash
sudo kubectl exec -it postgres-postgresql-0 -- psql -U postgres
```

---

## Création des secrets OpenFaaS

```bash
echo -n "postgres" | faas-cli secret create db-user

echo -n "CHANGE_ME" | faas-cli secret create db-password

echo -n "postgres-postgresql" | faas-cli secret create db-host

echo -n "postgres" | faas-cli secret create db-name

echo -n "CHANGE_ME" | faas-cli secret create fernet-key
```

---

## Build des fonctions

```bash
cd ~/COFRAP

faas-cli build -f stack.yaml
```

---

## Push des images Docker Hub

```bash
faas-cli push -f stack.yaml
```

---

## Déploiement OpenFaaS

```bash
faas-cli deploy -f stack.yaml \
--gateway http://127.0.0.1:31112
```

---

## Liste des fonctions

```bash
faas-cli list \
--gateway http://127.0.0.1:31112
```

---

## Logs des fonctions

### Génération mot de passe

```bash
sudo kubectl logs -n openfaas-fn \
-l faas_function=cofrap-generate-password
```

### Génération MFA

```bash
sudo kubectl logs -n openfaas-fn \
-l faas_function=cofrap-generate-2fa
```

### Authentification

```bash
sudo kubectl logs -n openfaas-fn \
-l faas_function=cofrap-authenticate-user
```

---

## Test fonction génération mot de passe

```bash
curl -X POST http://127.0.0.1:31112/function/cofrap-generate-password \
-H "Content-Type: application/json" \
-d '{"username":"test"}'
```

---

## Test fonction génération MFA

```bash
curl -X POST http://127.0.0.1:31112/function/cofrap-generate-2fa \
-H "Content-Type: application/json" \
-d '{"username":"test"}'
```

---

## Test fonction authentification

```bash
curl -X POST http://127.0.0.1:31112/function/cofrap-authenticate-user \
-H "Content-Type: application/json" \
-d '{"username":"test","password":"PASSWORD","totp":"123456"}'
```

---

## Redémarrage du cluster K3S

```bash
sudo systemctl restart k3s
```

---

## Redémarrage de la Gateway OpenFaaS

```bash
sudo kubectl rollout restart deployment gateway -n openfaas
```

---

## Interface OpenFaaS

```
http://IP_SERVEUR:31112/ui/
```