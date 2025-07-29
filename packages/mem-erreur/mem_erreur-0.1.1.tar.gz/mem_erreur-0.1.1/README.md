# mem_erreur

Package Python pour la gestion avancée des exceptions avec niveau de sévérité (`_fatal`) et enrichissement contextuel (`code`, `target`).

## 📦 Installation

```bash
pip install mem_erreur
```

## 🚀 Utilisation

```python
from mem_erreur import BaseException, BaseErreur, Erreur

# Erreur critique par défaut
raise BaseException("Erreur critique", code=1001, target="service-x")

# Erreur non bloquante
raise Erreur("Erreur mineure", code=42, target={"field": "email"})
```

## 🔧 Comportement automatique

- Toute exception non capturée ayant `_fatal=False` sera **ignorée silencieusement**.
- Les autres propageront le comportement standard (stacktrace + arrêt).

## 🧪 Tests

```bash
pytest
```

## 📤 Publication PyPI

```bash
python -m build
twine upload dist/*
```
