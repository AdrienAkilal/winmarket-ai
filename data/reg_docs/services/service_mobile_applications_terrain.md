# Service - Applications mobiles et outils terrain

## Positionnement
NovaSoft Conseil développe des applications mobiles Android/iOS et des Progressive Web Apps destinées aux équipes terrain : techniciens, commerciaux, inspecteurs, agents de contrôle, livreurs ou partenaires. Ces applications sont conçues pour fonctionner en situation de mobilité, avec ou sans connexion réseau stable.

## Périmètre fonctionnel couvert
Consultation et saisie de données terrain, formulaires structurés, prise de photo et annotation, signature client, géolocalisation, mode hors connexion avec synchronisation différée, gestion de tournées, planification d'interventions, notifications push et accès sécurisé aux données d'entreprise. Les applications sont systématiquement couplées à une plateforme web d'administration pour les managers et superviseurs.

## Technologies maîtrisées
React Native (iOS et Android depuis une base commune), Flutter selon contexte, Progressive Web App (PWA) pour les besoins légers. Côté back-end : API REST FastAPI ou Node.js, PostgreSQL, stockage local chiffré, Firebase pour les notifications, authentification SSO (OpenID Connect, SAML). Gestion de l'offline avec synchronisation contrôlée et gestion des conflits.

## Méthode de déploiement
Publication sur App Store et Google Play, déploiement MDM pour les appareils gérés par l'entreprise, mises à jour OTA (Over-the-Air) pour les correctifs urgents. Les certificats de signature et les configurations de distribution sont livrés et documentés.

## Équipe mobilisable
Un projet mobile standard mobilise 1 chef de projet, 1 développeur React Native senior, 1 développeur back-end, 1 UX/UI designer spécialisé mobile et 1 QA. Sur les projets plus complexes (mode offline avancé, intégration matérielle), un architecte solution peut intervenir en renfort.

## Conditions de réussite
Le projet est favorable lorsque le périmètre fonctionnel est clairement priorisé, que les devices cibles sont connus (marque, OS, version), que les règles de synchronisation offline sont explicites et que le client accepte une phase pilote terrain avant déploiement généralisé. Un budget inférieur à 100 000 € est insuffisant pour une application terrain complète avec mode offline et back-office.

## Limites et red flags
Intégration de matériels spécifiques non documentés (scanners, imprimantes Bluetooth, capteurs IoT), synchronisation complexe sur des réseaux très dégradés sans règles de conflit définies, remplacement d'un outil critique en production dans un délai inférieur à 3 mois, exigence de certification HDS sans hébergeur partenaire identifié.
