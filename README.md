# COFRAP MSPR - Architecture Serverless Kubernetes

## Présentation

Ce projet a été réalisé dans le cadre de la MSPR TPRE921 de l'EPSI.

L'objectif est de proposer une solution sécurisée de gestion des accès utilisateurs pour la COFRAP en s'appuyant sur une architecture Serverless déployée sur Kubernetes.

La solution permet :

* la génération automatique de mots de passe complexes ;
* la mise en place obligatoire d'une authentification multifacteur (MFA/TOTP) ;
* le stockage sécurisé des informations sensibles ;
* l'authentification des utilisateurs ;
* la gestion de l'expiration automatique des identifiants.

---

## Architecture technique

### Infrastructure

* Kubernetes K3S
* OpenFaaS Community Edition
* PostgreSQL
* Docker
* Helm

### Développement

* Python 3
* OpenFaaS Python HTTP Template
* Cryptography (Fernet)
* PyOTP
* QRCode

### Frontend

* VueJS
* TypeScript
* Vite

---

## Structure du dépôt

```text
openfaas/
├── stack.yaml
├── cofrap-generate-password/
├── cofrap-generate-2fa/
└── cofrap-authenticate-user/

kubernetes/
├── postgres-table.sql
├── secrets.example.yaml
└── commands.md

docs/
├── architecture.md
└── screenshots/
```

---

## Fonctions OpenFaaS

### cofrap-generate-password

Génère un mot de passe complexe de 24 caractères.

Fonctionnalités :

* génération aléatoire sécurisée ;
* chiffrement Fernet ;
* enregistrement en base PostgreSQL ;
* génération d'un QR Code transmis au frontend.

---

### cofrap-generate-2fa

Génère un secret MFA compatible TOTP.

Fonctionnalités :

* génération du secret MFA ;
* création de l'URI TOTP ;
* génération du QR Code ;
* chiffrement Fernet ;
* stockage PostgreSQL.

---

### cofrap-authenticate-user

Authentifie un utilisateur.

Contrôles réalisés :

* vérification du login ;
* vérification du mot de passe ;
* vérification du code TOTP ;
* contrôle de l'expiration des identifiants.

---

## Base de données

La solution utilise PostgreSQL.

Table principale :

```sql
users
```

Colonnes :

| Champ    | Description             |
| -------- | ----------------------- |
| id       | Identifiant utilisateur |
| username | Nom d'utilisateur       |
| password | Mot de passe chiffré    |
| mfa      | Secret MFA chiffré      |
| gendate  | Date de génération      |
| expired  | Statut d'expiration     |

---

## Sécurité

Les mécanismes de sécurité mis en œuvre sont :

* chiffrement des mots de passe avec Fernet ;
* chiffrement des secrets MFA ;
* stockage sécurisé des paramètres via Kubernetes Secrets ;
* authentification multifacteur ;
* rotation périodique des identifiants ;
* isolation des fonctions via OpenFaaS.

---

## Déploiement

### Construction des images

```bash
faas-cli build -f stack.yaml
```

### Publication Docker Hub

```bash
faas-cli push -f stack.yaml
```

### Déploiement OpenFaaS

```bash
faas-cli deploy -f stack.yaml --gateway http://127.0.0.1:31112
```

---

## Tests

### Génération de mot de passe

```bash
curl -X POST http://127.0.0.1:31112/function/cofrap-generate-password \
-H "Content-Type: application/json" \
-d '{"username":"test"}'
```

### Génération MFA

```bash
curl -X POST http://127.0.0.1:31112/function/cofrap-generate-2fa \
-H "Content-Type: application/json" \
-d '{"username":"test"}'
```

### Authentification

```bash
curl -X POST http://127.0.0.1:31112/function/cofrap-authenticate-user \
-H "Content-Type: application/json" \
-d '{"username":"test","password":"PASSWORD","totp":"123456"}'
```

---

## Auteur

Tom Saintenoy - Heniart Loan - Hilaricus Stephane - Boursault Benjamin

MSPR TPRE921 - EPSI

Projet COFRAP - Architecture Serverless Kubernetes/OpenFaaS
