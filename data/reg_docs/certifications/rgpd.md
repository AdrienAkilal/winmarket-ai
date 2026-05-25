# RGPD — Conformité et démarche de NovaSoft Conseil

## Positionnement

NovaSoft Conseil intègre la conformité RGPD by design dans tous ses projets impliquant des données personnelles. L'entreprise intervient systématiquement en qualité de sous-traitant au sens de l'article 28 du RGPD, traitant des données pour le compte et sur instruction de ses clients (responsables de traitement).

## Ce que l'on met en œuvre dans chaque projet

**Analyse préalable**
- Identification des catégories de données personnelles traitées par la solution
- Qualification du rôle de chaque acteur (responsable de traitement, sous-traitant, co-responsable)
- Assistance à la réalisation d'une Analyse d'Impact relative à la Protection des Données (AIPD) si le traitement est à risque élevé

**Architecture et développement**
- Minimisation des données : collecte strictement limitée aux données nécessaires à la finalité
- Durées de conservation configurables par catégorie de donnée
- Chiffrement des données sensibles en transit (TLS 1.3) et au repos (AES-256)
- Pseudonymisation ou anonymisation lorsque le cas d'usage le permet
- Gestion technique des droits des personnes : accès, rectification, effacement, portabilité
- Journalisation des accès et des traitements (audit trail)

**Documentation et contractualisation**
- Rédaction du DPA (Data Processing Agreement / accord de sous-traitance) conforme article 28
- Contribution au registre des traitements du client pour les traitements mis en œuvre
- Clause de sous-traitance ultérieure documentée (hébergeurs, API LLM, services tiers)

**Hébergement**
- Hébergement des données exclusivement en Union Européenne (Azure France Central, OVHcloud, Scaleway selon projet)
- Aucun transfert de données personnelles hors UE sans encadrement juridique préalable (clauses contractuelles types)

## Ce que l'on peut fournir dans une candidature

- Modèle de DPA complété et signable
- Note sur l'architecture RGPD du projet (flux de données, mesures de protection, durées de conservation)
- Engagement écrit sur la localisation des données (UE uniquement)
- Procédure de notification en cas de violation de données (délai ≤ 72h au client)
- Politique de confidentialité interne de NovaSoft disponible sur demande

## Cas particuliers

**Données de santé :** NovaSoft n'est pas hébergeur agréé HDS. Les projets impliquant des données de santé nominatives nécessitent un hébergeur HDS partenaire et une analyse juridique spécifique. Ce point doit être évalué au cas par cas.

**Modèles LLM externes :** Lorsque des données personnelles sont transmises à une API LLM tierce (Claude, GPT-4, etc.), un DPA avec l'éditeur du modèle est requis, assorti d'une clause interdisant l'utilisation des données pour l'entraînement des modèles. Ce point est systématiquement documenté et soumis à validation du client.
