# Platform independent interface for file dialogs

Installation:

```commandline
pip install --upgrade filedialogs
```

Test:

```python
from filedialogs import *

print(f'{STARTERID=}')

print(askfile())
print(askfiles())
print(asksave())
print(askdir())
```

CLI:

```commandline
askfile open|multi|save|dir
```
