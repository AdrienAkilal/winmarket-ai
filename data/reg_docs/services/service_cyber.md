# Service Cybersécurité applicative — NovaSoft Conseil

## Positionnement

NovaSoft Conseil n'est pas une ESN spécialisée en cybersécurité offensive ou en opérations de sécurité (SOC, SIEM, forensic). En revanche, l'entreprise intègre systématiquement des pratiques de sécurité applicative dans ses projets de développement et d'exploitation, et peut proposer un accompagnement ciblé sur la sécurisation des applications et des infrastructures cloud.

## Ce que l'on fait

**Sécurité applicative (SAST/DAST)**
- Analyse statique du code source (SonarQube, Semgrep) intégrée dans les pipelines CI/CD
- Analyse dynamique des applications web (OWASP ZAP, tests de vulnérabilité courants)
- Revue manuelle de sécurité sur les composants critiques (authentification, gestion des sessions, contrôle d'accès)
- Correction des vulnérabilités identifiées (injections SQL, XSS, CSRF, IDOR, exposition de secrets)

**Gestion des identités et des accès (IAM)**
- Mise en œuvre de l'authentification SSO (SAML 2.0, OpenID Connect, OAuth2)
- Intégration Azure Active Directory, Keycloak
- Principe du moindre privilège : RBAC (contrôle d'accès par rôle) appliqué sur toutes les applications
- Gestion des tokens et des sessions (expiration, révocation, rotation)

**Gestion des secrets**
- Stockage des secrets dans des coffres sécurisés (Azure Key Vault, HashiCorp Vault)
- Interdiction de stocker des secrets en dur dans le code source (détection via hooks pre-commit)
- Rotation automatique des clés et des certificats selon politique client

**Durcissement des infrastructures cloud**
- Configuration sécurisée des services cloud (Azure Security Center, politiques IAM AWS)
- Segmentation réseau, groupes de sécurité, règles de pare-feu
- Chiffrement au repos et en transit sur l'ensemble des composants
- Activation des journaux d'audit (Azure Monitor, CloudTrail)

**Conformité et accompagnement**
- Accompagnement à la conformité RGPD (voir fiche RGPD)
- Assistance à la mise en place de pratiques alignées ISO 27001 (voir fiche ISO 27001)
- Préparation aux audits de sécurité demandés par les clients
- Sensibilisation sécurité des équipes projet (bonnes pratiques développement sécurisé)

## Ce que l'on ne fait pas

- Tests d'intrusion (pentests) avancés réalisés par des équipes Red Team spécialisées
- Opérations de sécurité en continu (SOC as a service, SIEM)
- Réponse à incident (forensic, investigation numérique)
- Certification SecNumCloud ou PASSI (Prestataire d'Audit de la Sécurité des Systèmes d'Information)
- Qualification ISO 27001 certifiée (pratiques alignées uniquement — voir fiche dédiée)

## Quand valoriser ce service dans une candidature

- L'AO mentionne des exigences de sécurité applicative (OWASP, tests de vulnérabilité)
- L'AO demande une gestion des accès et des habilitations (SSO, RBAC)
- L'AO demande un audit de sécurité au moment de la livraison
- L'AO traite des données sensibles (données personnelles, données financières, données contractuelles)

## Limites à mentionner si pertinent

Si l'AO exige un pentest réalisé par un prestataire certifié PASSI, NovaSoft peut coordonner le recours à un prestataire tiers spécialisé, mais ne peut pas porter ce service en propre. Ce point doit être clarifié dans la réponse.
