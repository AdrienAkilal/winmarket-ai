# Guide de résolution — Situations difficiles dans les appels d'offres

Ce document recense les situations complexes fréquemment rencontrées lors de l'analyse ou de la réponse à un appel d'offres, avec la posture et les arguments recommandés.

---

## 1. Le client demande une technologie que l'on ne maîtrise pas

**Situation :** L'AO exige une compétence technique absente du référentiel de l'entreprise (framework spécifique, progiciel éditeur, langage peu courant).

**Posture recommandée :**
Être transparent sur l'état actuel des compétences tout en proposant une mitigation crédible. Ne jamais affirmer une maîtrise inexistante : les audits préalables ou le démarrage du projet révèlent rapidement les lacunes.

**Arguments à construire :**
- Identifier une compétence adjacente maîtrisée (Python si l'AO demande un framework Python spécifique, React si l'AO demande Vue.js, etc.)
- Proposer un plan de montée en compétence réaliste : formation interne sur les 2 premières semaines, pair programming avec un expert externe si nécessaire, autonomie d'équipe visée au deuxième mois
- Proposer optionnellement un renfort freelance spécialisé budgété dans l'offre (+10 % environ)

**Seuil de faisabilité :** Si plus de deux technologies critiques sont absentes, le risque de dérive qualité est élevé. Envisager un GO sous réserve ou un NO-GO selon la pondération de ces technologies dans l'AO.

---

## 2. Une certification obligatoire est absente

**Situation :** L'AO exige une certification que l'entreprise ne détient pas (ISO 27001, SecNumCloud, HDS, etc.).

**Analyse préalable :** Distinguer "obligatoire avec attestation exigée" de "souhaitée" ou "alignée". Lire attentivement la formulation dans le CCTP et le règlement de consultation.

**Si la certification est souhaitée mais non obligatoire :**
Valoriser les pratiques équivalentes en place (politique de sécurité interne, PAQ, alignement sur les exigences de la norme sans certification formelle). Fournir ces documents dans l'offre.

**Si la certification est obligatoire :**
- ISO 27001 : critère bloquant. Ne pas répondre.
- SecNumCloud : critère bloquant sauf si un partenaire hébergeur qualifié peut être impliqué et que le client l'accepte. À vérifier avant de répondre.
- Qualiopi : NovaSoft est certifiée. Pas de problème.
- HDS : critère bloquant si le titulaire doit être hébergeur HDS en propre.

Se référer aux fiches certification dédiées pour le détail de chaque cas.

---

## 3. Le budget client est trop faible pour le périmètre demandé

**Situation :** Le budget annoncé ne couvre pas l'ensemble des fonctionnalités demandées dans l'AO.

**Approche recommandée — décomposition en phases :**
Proposer un périmètre MVP pour la phase 1 dans l'enveloppe disponible, avec une roadmap claire pour les fonctionnalités complémentaires en phase 2, chiffrées séparément en option. Cette approche démontre le pragmatisme de l'entreprise sans promettre une livraison irréaliste.

**Seuils de vigilance :**
- Plateforme web métier complète avec intégration SI : difficile sous 120 000 €
- RAG documentaire industrialisé avec interface et gouvernance : difficile sous 80 000 €
- Dashboard BI multi-sources livré et formé : faisable entre 40 000 et 90 000 €
- Application mobile terrain avec mode offline : difficile sous 100 000 €

**À éviter :** Réduire les délais ou les effectifs pour entrer dans le budget. La qualité de livraison s'en ressent et l'entreprise se retrouve en déficit d'heures sur un projet vendu trop bas.

---

## 4. La deadline de réponse à l'AO est très courte (moins de 2 semaines)

**Situation :** Le délai entre la publication de l'AO et la date limite de remise des offres est inférieur à 15 jours.

**Processus de triage recommandé :**
- Jours 1-2 : extraction automatique des éléments clés, scoring rapide (30 minutes), décision GO / NO-GO / à approfondir
- Si GO : concentration des efforts sur la note de compréhension du besoin (section la plus différenciante) et les réponses aux questions spécifiques du client. Les sections standardisées (présentation entreprise, méthodologie, références) sont adaptées depuis les templates existants.
- Si le délai est vraiment insuffisant : contacter le client pour demander un délai supplémentaire de 5 jours. Cette demande est souvent accordée, notamment dans les procédures adaptées.

**Règle interne :** Une réponse bâclée sous deadline courte nuit à l'image de l'entreprise et consomme des ressources sans valeur. Mieux vaut un NO-GO motivé qu'une offre incomplète.

---

## 5. Un concurrent connu est présent sur l'AO

**Situation :** L'entreprise sait ou suppose qu'un concurrent direct (ESN de taille comparable ou grande ESN nationale) répond au même AO.

**Positionnement recommandé :**
Ne jamais citer un concurrent par son nom dans la candidature. Valoriser les différenciateurs propres sans attaquer implicitement un autre acteur.

**Arguments différenciants selon le profil du concurrent :**

Contre une grande ESN nationale : souligner la dédicace de l'équipe (pas de matrice de ressources partagées), la continuité des intervenants (moins de turnover), la réactivité décisionnelle (le chef de projet a accès direct à la direction), et la spécialisation sur les technologies demandées.

Contre une ESN de taille comparable : mettre en avant les références les plus proches du besoin client, l'expertise sectorielle si elle est supérieure, la qualité des profils proposés (seniors identifiés nommément dans l'offre).

---

## 6. Les pénalités contractuelles sont disproportionnées

**Situation :** L'AO inclut des clauses de pénalités très élevées (supérieures à 1 % du montant par semaine de retard, ou dépassant 15 % en cumulé).

**Seuils d'alerte :**
- Pénalités supérieures à 0,5 % par semaine : vigilance renforcée
- Pénalités supérieures à 1 % par semaine : demande de négociation avant signature
- Pénalités supérieures à 2 % par semaine : critère de NO-GO si non négociables
- Obligation de résultat sur un SI tiers non maîtrisé : critère de NO-GO

**Stratégie de négociation :**
Proposer un plafonnement des pénalités à 10 % du montant contractuel, un déclenchement progressif (taux faible les 2 premières semaines, taux fort ensuite), et des exclusions pour les retards imputables au client (accès aux environnements, validation des livrables, accès aux API).

---

## 7. L'AO est très flou ou incomplet

**Situation :** Le périmètre, le budget ou les délais sont insuffisamment précisés pour produire une offre fiable.

**Recommandation :** Contacter le client avant la date limite pour clarifier les points bloquants via le mécanisme de questions prévu dans le dossier de consultation. Ces questions et leurs réponses sont en général publiées à l'ensemble des candidats.

**Scoring d'un AO flou :** Appliquer des hypothèses conservatrices sur tous les paramètres incertains. Un AO sans budget indiqué sera scoré comme si le budget était bas. Un périmètre vague sera scoré comme potentiellement large. Le score résultant reflète le risque réel de l'opération.

**Seuil :** Si plus de trois paramètres clés (budget, périmètre, délai, certifications) sont indéterminés après la phase de questions, le risque de dérive est trop élevé pour un GO direct. Préférer un GO sous réserve conditionnel à une réunion de cadrage préalable, ou un NO-GO.

---

## 8. Quand dire non à un AO a priori intéressant

**Critères de NO-GO même si le budget est attractif :**
- Équipe disponible inférieure à 5 % de capacité : risque de surcharge et de dégradation des projets en cours
- Client avec historique de litige, non-paiement ou mauvaise réputation marché
- Certification obligatoire impossible à obtenir dans le délai projet
- Périmètre fonctionnel ambigu que le client refuse de clarifier malgré les demandes
- Obligation de résultat sur un système tiers (ERP éditeur, SI legacy) sans accès à la documentation
- Technologie centrale que l'entreprise ne maîtrise pas et ne peut pas acquérir dans le délai imparti
