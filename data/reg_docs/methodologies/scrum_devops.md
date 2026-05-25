# Méthodologie projet — Scrum et pratiques DevOps chez NovaSoft Conseil

## Approche générale

NovaSoft Conseil applique une méthode agile pragmatique adaptée au contexte de chaque client. L'objectif est de livrer de la valeur de façon incrémentale, de maintenir une visibilité constante sur l'avancement et d'intégrer les retours utilisateurs tout au long du projet. La méthode est adaptée (mais non rigide) : pour les clients disposant de processus plus formalisés ou soumis à des exigences réglementaires, un cycle hybride agile / jalons formels peut être proposé.

## Cadre Scrum

**Rôles**
- Product Owner (proxy) : assuré par le chef de projet NovaSoft en coordination avec le référent métier client. Il porte la vision produit, priorise le backlog et valide les user stories.
- Scrum Master : rôle tenu par le chef de projet, garant du bon déroulement des cérémonies et de la levée des obstacles.
- Équipe de développement : pluridisciplinaire (développeurs, QA, UX selon projet), auto-organisée dans les sprints.

**Cérémonies**
- Sprint planning (début de sprint, 2h) : sélection des user stories du backlog, découpage en tâches techniques, estimation en points ou en jours
- Daily standup (quotidien, 15 min) : avancement, blocages, synchronisation — en visioconférence pour les équipes distribuées
- Sprint review (fin de sprint, 1h) : démonstration au client des fonctionnalités livrées, collecte des retours
- Rétrospective (fin de sprint, 45 min) : amélioration continue des pratiques d'équipe (interne NovaSoft)

**Sprints**
- Durée standard : 2 semaines
- Chaque sprint produit un incrément potentiellement livrable et testé
- Un sprint de cadrage initial (2 à 3 semaines) précède le premier sprint de développement : il sert à finaliser l'architecture, produire les maquettes UX et rédiger le backlog initial

**Backlog**
- Structuré en épics → user stories → tâches techniques
- Priorisé par valeur métier en collaboration avec le client
- Estimé et mis à jour à chaque sprint
- Accessible au client sur l'outil de gestion de projet convenu (Jira, Linear, Notion selon préférence)

## Pratiques DevOps intégrées

**Intégration continue (CI)**
- Pipeline CI déclenché à chaque push sur la branche principale
- Étapes automatisées : compilation, tests unitaires, analyse de qualité de code (SonarQube), scan de vulnérabilités des dépendances
- Blocage automatique si les tests échouent ou si le seuil de couverture n'est pas atteint

**Déploiement continu (CD)**
- Déploiement automatisé sur l'environnement de développement à chaque merge
- Déploiement en recette déclenché manuellement après validation QA
- Déploiement en production après validation client et signature du procès-verbal de recette
- Outils : GitHub Actions ou GitLab CI selon préférence client

**Gestion des environnements**
- Trois environnements minimum : développement, recette, production
- Configuration as Code : variables d'environnement gérées via coffres de secrets (Azure Key Vault, GitHub Secrets)
- Parité maximale entre les environnements (mêmes images Docker, mêmes configurations)

**Qualité et tests**
- Tests unitaires : rédigés par les développeurs, intégrés au pipeline CI
- Tests d'intégration : validation des API et des interfaces entre composants
- Tests de non-régression automatisés sur les scénarios critiques (Cypress ou Playwright selon projet)
- Tests de performance (k6 ou JMeter) avant chaque mise en production majeure
- Recette métier progressive : les utilisateurs référents du client valident les fonctionnalités sprint par sprint

**Observabilité**
- Monitoring applicatif : Grafana + Prometheus ou Azure Application Insights selon infrastructure
- Alertes configurées sur les métriques critiques (disponibilité, temps de réponse, taux d'erreur)
- Centralisation des logs applicatifs (ELK ou Azure Log Analytics)

## Adaptation pour les projets réglementés

Certains clients (secteur public, mutuelles, organismes financiers) exigent des jalons formels, des dossiers de conception et des procès-verbaux de recette. Dans ce cas, la méthode est adaptée :
- Phases formalisées avec jalons contractuels (conception, développement, recette, production)
- Dossier d'architecture technique soumis à validation avant développement
- Plan de tests et cahier de recette signés
- Rapport de mise en production

Ces livrables complémentaires sont compatibles avec la démarche agile : le développement reste itératif, les jalons formels ponctuent les grandes étapes sans rigidifier les sprints internes.
