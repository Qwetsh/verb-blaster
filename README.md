# 🚀 VERB BLASTER — Irregular Strike

Un shoot-them-up spatial **pédagogique** pour réviser les **verbes irréguliers anglais**,
dans un emballage rétro-arcade façon « saga galactique lointaine ».

▶️ **Jouer en ligne :** https://qwetsh.github.io/verb-blaster/

## 🎮 Principe

- On pilote un chasseur et on tire sur des astéroïdes portant des **verbes**.
- 💥 **Détruire un verbe IRRÉGULIER** → on gagne des points (+ combo).
- ✅ **Laisser passer un verbe RÉGULIER** → bonne décision, petit bonus.
- ❌ **Tirer sur un régulier** → erreur : pluie de missiles tout autour et perte de points.
- ☄️ **Percuter un astéroïde** (régulier ou irrégulier) → on perd 1 PV.

Par défaut, **aucun indice de couleur** : il faut vraiment reconnaître le verbe avant de tirer.
Un mode « indices couleur » (facile) est activable depuis le menu.

## 🕹️ Commandes

| Touche | Action |
|--------|--------|
| Flèches / Q-D-Z-S | Déplacer le vaisseau |
| Espace | Tirer |
| Échap | Retour au menu |

## ✨ Contenu

- Landing page arcade, crawl d'intro, Hall of Fame (scores en `localStorage`)
- **Écran de sélection de vaisseau** façon versus (8 chasseurs aux stats distinctes)
- Sprites de vaisseaux et de météorites détourés automatiquement

## 🛠️ Technique

100 % web, **zéro dépendance** : un seul `index.html` (Canvas 2D) + `sprites.js`
(sprites détourés encodés en base64). Jouable hors-ligne en double-cliquant le fichier.

Les sprites sont régénérés depuis les planches sources avec :

```bash
py build_sprites.py
```

---

Fait avec ❤️ par Charles ([@qwetsh](https://github.com/qwetsh)).
