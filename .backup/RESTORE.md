# Как откатить профиль

Копия исходного README лежит в `.backup/README.original.md`
(снято с коммита `266370e`, последнего коммита `main` до редизайна).

Откат одной командой:

    git checkout 266370e -- README.md && git rm -r --cached assets .github 2>/dev/null; git commit -m "Revert profile redesign"

Или просто скопируй `.backup/README.original.md` в `README.md`.
Удалять `.github/workflows/snake.yml` не обязательно, но без README змейка нигде не показывается.
