<p align="center">
  <img src="https://github.com/veb-bet/vebfs/raw/ff362f8f30d1a9debc566ff5ed54a5bcca221b43/docs/bat_image.png" alt="vebfs logo" width="150"/>
</p>

# vebmimesisify

**vebmimesisify** — это библиотека для генерации случайных сценариев, диалогов и событийных логов с использованием [vebmimesisify](https://github.com/lk-geimfari/vebmimesisify). Отлично подходит для генерации тестовых данных, случайных описаний и повествований.

## Установка

```bash
pip install vebmimesisify
```

## Использование

```python
from vebmimesisify import generate_scenario, generate_dialogue, generate_event_log

print(generate_scenario())
print(generate_dialogue())
print(generate_event_log(3))
```
