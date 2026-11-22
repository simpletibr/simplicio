<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="Logo Simplicio" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>Ten sam agent, ten sam model, to samo zadanie: 121&nbsp;s&nbsp;→&nbsp;25&nbsp;s, a koszt $0.0226&nbsp;→&nbsp;$0.0076.</b></p>

<p>Bez Simplicio → z Simplicio 3.15.0. Mediana z 3 przebiegów jednego małego zadania programistycznego w Claude Code z modelem Claude Haiku 5.5.</p>

<p>Simplicio działa na twoim komputerze i dodaje narzędzia do agenta kodującego, którego już używasz.</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="Najnowsze wydanie"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="Dokumentacja"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Gwiazdki"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="Licencja: zastrzeżona">
</p>

<p>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português (Brasil)</a> ·
  <a href="README.es-ES.md">Español</a> ·
  <a href="README.fr-FR.md">Français</a> ·
  <a href="README.it-IT.md">Italiano</a> ·
  Polski ·
  <a href="README.ru-RU.md">Русский</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja-JP.md">日本語</a> ·
  <a href="README.ko-KR.md">한국어</a> ·
  <a href="README.hi-IN.md">हिन्दी</a> ·
  <a href="README.ar-SA.md">العربية</a>&lrm; ·
  <a href="README.he-IL.md">עברית</a>&lrm; ·
  <a href="README.id-ID.md">Bahasa Indonesia</a> ·
  <a href="README.ms-MY.md">Bahasa Melayu</a>
</p>

<p align="center"><sub>Ten plik jest tłumaczeniem <a href="../README.md">angielskiego README</a>. Jeśli te dwie wersje się różnią, odniesieniem jest angielska strona. Liczby i wykresy są w języku angielskim.</sub></p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-dark.svg">
    <img src="../assets/benchmark-2026-11-22-light.svg" width="840" alt="Wykres słupkowy porównujący konfigurację bez Simplicio, Simplicio 3.14.0 i Simplicio 3.15.0 w trzech miarach, mediana z trzech sesji dla każdej konfiguracji. Czas całego zadania: 121 s bez Simplicio, 104 s z Simplicio 3.14.0 i 25 s z Simplicio 3.15.0. Koszt: $0.0226, $0.0220 i $0.0076. Tokeny wyjściowe: 18,162, 19,722 i 3,211.">
  </picture>
</p>

<p align="center">
  <sub>Mediana z 3 sesji dla każdej konfiguracji (bez Simplicio, Simplicio 3.14.0 i Simplicio 3.15.0). Claude Haiku 5.5 w Claude Code 2.1.330, 2026-11-22. Każda konfiguracja dostarczyła 9 z 9 kroków. Cienka linia na każdym słupku biegnie od najniższej do najwyższej sesji.<br>
  <a href="../benchmarks/2026-11-22-standard-benchmark.md">Metoda, dane i ograniczenia</a></sub>
</p>

<p align="center">
  <sub>Czytając to, miej na uwadze: jedno małe zadanie, trzy sesje na konfigurację, jeden model. Sprawdzenia z zewnątrz obejmują mniej, niż wymagają prompty. Szczytowe zużycie pamięci było wyższe: 375 MB wobec 270 MB. Kompilacje Simplicio zbudowano z commitów wydań, z wyłączonym logowaniem.</sub>
</p>

<p align="center">Sposób, w jaki Simplicio uzyskuje ten wynik, nie jest publikowany. Pomiary są publikowane, także te, w których Simplicio przegrywa.</p>

<p align="center">
  <b>Wypróbuj:</b> <a href="#install">Instalacja</a> · <a href="#first-run">Pierwsze uruchomienie</a><br>
  <a href="#what-simplicio-is">Czym jest</a> ·
  <a href="#the-measurement">Pomiar</a> ·
  <a href="#works-with-the-agent-you-already-use">Agenci</a> ·
  <a href="#command-line">Polecenia</a> ·
  <a href="#safety-and-privacy">Prywatność</a> ·
  <a href="#questions-people-ask">Pytania</a> ·
  <a href="#documentation-and-community">Dokumentacja</a>
</p>

<a id="what-simplicio-is"></a>

## Czym jest Simplicio

Simplicio to lokalny program, który daje agentowi kodującemu, którego już używasz, tryb ultraszybki, niezależnie od agenta i niezależnie od modelu. Liczby na tej stronie pochodzą od jednego agenta i jednego modelu; sekcja poniżej mówi dokładnie, co zmierzono.

- **Zostajesz przy swoim agencie i swoim modelu.** Simplicio nie zastępuje Claude Code, Codex, Cursor ani jakiegokolwiek modelu stojącego za nimi.
- **Instalujesz jeden podpisany natywny plik binarny.** Instalator weryfikuje podpis, a następnie rejestruje Simplicio w agentach, które znajdzie na twoim komputerze.
- **Działa na twoim komputerze.** Twój agent uruchamia Simplicio jako lokalny serwer MCP przez STDIO. MCP to Model Context Protocol, standardowy sposób, w jaki agent kodujący wywołuje zewnętrzne narzędzia. STDIO oznacza, że agent sam uruchamia program i rozmawia z nim przez jego standardowe wejście i wyjście.
- **Daje agentowi narzędzia.** Mapa repozytorium, ograniczony kontekst, ustrukturyzowane edycje i sprawdzenia. [Podstawowe narzędzia](#works-with-the-agent-you-already-use) są wymienione niżej.
- **Zmienia się sesja.** Ile czasu zajmuje i ile kosztuje. Następna sekcja pokazuje, o ile, i wskazuje, gdzie Simplicio nie pomaga.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="Schemat. Na twoim komputerze: ty, twój agent kodujący, Simplicio i twoje repozytorium. Agent rozmawia z Simplicio przez lokalne STDIO (MCP). Agent rozmawia z dostawcą modelu tak jak dotąd. Simplicio rozmawia z SimpleTI w sprawie logowania i sprawdzania planu oraz z GitHubem w sprawie sprawdzania wydania. W żadnej z tych rozmów nie ma treści repozytorium.">
  </picture>
</p>

<p align="center">
  <sub>Obraz pokazuje, co dzieje się domyślnie. Pełna lista, w tym funkcje łączące się z innymi usługami, znajduje się w sekcji <a href="#safety-and-privacy">Co Simplicio wysyła i do kogo</a> w części Bezpieczeństwo i prywatność.</sub>
</p>

<a id="the-measurement"></a>

## Pomiar

Jedno zadanie, uruchamiane w ten sam sposób z Simplicio i bez niego. Zadanie to jedna sesja agenta z trzema krokami w tej samej rozmowie:

1. Zbuduj listę użytkowników: API i stronę z tabelą, wyszukiwaniem i sortowaniem.
2. Zmień ją: usuń kolumnę, dodaj filtr według roli i kolumnę z datą.
3. Dodaj prostą rejestrację: endpoint `POST`, który sprawdza swoje dane wejściowe, oraz stronę z formularzem.

Po każdym kroku wynik jest sprawdzany z zewnątrz sesji. API jest wywoływane przez HTTP, a strony są ładowane w headless Chrome, czyli w Chrome bez okna. Każda konfiguracja używała tego samego agenta i tego samego modelu: Claude Code 2.1.330 z Claude Haiku 5.5. Punkt odniesienia to Claude Code 2.1.330 z własnymi narzędziami, bez serwera MCP i bez konfiguracji Simplicio. Sprawdzenia nie testują pola wyszukiwania, sortowania, przekierowania po zapisaniu, wyglądu strony ani jakości kodu.

Na wykresie widać każdą sesję, nie tylko mediany.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="Wykres punktowy wszystkich sesji: czas całego zadania na osi poziomej, a koszt zgłaszany przez agenta na osi pionowej. Simplicio 3.15.0, zielone romby: 23 do 27 s i $0.0071 do $0.0098. Simplicio 3.14.0, szare kwadraty: 90 do 106 s i $0.0214 do $0.0249. Bez Simplicio, puste kółka: 97 do 172 s i $0.0186 do $0.0280.">
  </picture>
</p>

Mediana z 3 sesji na konfigurację. Mała linia pod każdą wartością pokazuje najniższą i najwyższą sesję.

| Miara | Bez Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| Czas zadania | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| Zgłaszany koszt | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| Żądania do modelu | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| Wywołania narzędzi | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| Tokeny wyjściowe | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| Tokeny wejściowe | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| Czas CPU | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| Szczytowe zużycie pamięci | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| Dostarczone kroki | 9 z 9 | 9 z 9 | 9 z 9 |

Pogrubienie oznacza najlepszą wartość w wierszu, tylko tam, gdzie jej zakres nie nakłada się na pozostałe. Zakresy tokenów wejściowych nakładają się, więc ten przebieg nie stwierdza różnicy w tokenach wejściowych. „9 z 9” oznacza 3 kroki w każdej z 3 sesji, a każdy krok przeszedł wszystkie sprawdzenia z zewnątrz. Czas zadania to czas całego zadania. Żądanie do modelu to jedno wywołanie modelu, a wywołanie narzędzia to jedno użycie narzędzia przez agenta. Zgłaszany koszt to wartość podana przez agenta: liczba zużytych tokenów pomnożona przez opublikowaną cenę modelu. Liczy wyłącznie tokeny modelu. Nie jest to faktura.

Co zmieniło się w sesji, w liczbach: model wykonał mniej żądań, a agent wykonał mniej wywołań narzędzi.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="Wykres jednostkowy z jednym znacznikiem na każde żądanie do modelu lub wywołanie narzędzia, mediana z 3 sesji. Żądania do modelu: 25 bez Simplicio, 18 z Simplicio 3.14.0 i 10 z Simplicio 3.15.0. Wywołania narzędzi: 22, 15 i 7.">
  </picture>
</p>

Czas według kroku, na jednej wspólnej skali.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="Mediana czasu według kroku na jednej wspólnej skali. Krok 1, budowa: 57.3 s bez Simplicio, 53.7 s z Simplicio 3.14.0 i 5.8 s z Simplicio 3.15.0. Krok 2, zmiana: 17.3 s, 15.2 s i 8.9 s. Krok 3, rejestracja: 31.4 s, 27.5 s i 10.3 s.">
  </picture>
</p>

Każda mediana liczona jest osobno, więc kroki nie sumują się do mediany całego zadania.

<details>
<summary>Dokładne liczby dla każdego kroku</summary>

Każda komórka to mediana czasu i mediana kosztu kroku:

| Krok | Bez Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. Budowa | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. Zmiana | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. Rejestracja | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**Jak to czytać.** Ilorazy liczone są z niezaokrąglonych median. W porównaniu z tym samym agentem bez Simplicio całe zadanie wykonało się 4.9 raza szybciej i kosztowało około jednej trzeciej tego. W porównaniu z poprzednim wydaniem zadanie wykonało się 4.2 raza szybciej. W sesji model wykonał 10 żądań zamiast 25 i wygenerował 3,211 tokenów wyjściowych zamiast 18,162, a zadanie przeszło te same sprawdzenia z zewnątrz. Najgorszy przypadek: najszybsza sesja bez Simplicio (97.1 s) była mimo to 3.7 raza wolniejsza od najwolniejszej sesji z Simplicio 3.15.0 (26.6 s), a najtańsza sesja bez Simplicio ($0.0186) kosztowała mimo to 1.9 raza tyle, ile najdroższa sesja z nim ($0.0098). Punkt odniesienia to Claude Code 2.1.330 z własnymi narzędziami, bez serwera MCP i bez konfiguracji Simplicio. Koszt liczy wyłącznie tokeny modelu. Sesje uruchamiano po cztery naraz na jednej maszynie, więc czasy porównuj tylko w obrębie tej rundy.

<a id="where-simplicio-does-not-win"></a>

### Gdzie Simplicio nie wygrywa

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="Szczytowe zużycie pamięci, mediana z 3 sesji: 270 MB bez Simplicio, najniższe; 436 MB z Simplicio 3.14.0, o 61% więcej; 375 MB z Simplicio 3.15.0, o 39% więcej.">
  </picture>
</p>

- **Pamięć.** Szczytowe zużycie pamięci było o 39% wyższe niż przy zwykłym agencie: 375 MB wobec 270 MB.
- **Poprzednie wydanie nie dało zysku w tym zadaniu.** Simplicio 3.14.0 kosztowało tyle samo, co bez Simplicio, a jego różnica czasu mieści się w rozrzucie między przebiegami. Zysk na tej stronie pojawił się wraz z wersją 3.15.0.
- **Krótki jednorazowy skrypt w Pythonie.** We wcześniejszej rundzie Simplicio 3.10.8 było wolniejsze od zwykłego agenta dla każdego wypróbowanego modelu. Na Claude Sonnet 5.5 w Claude Code zajęło 19.6 s i $0.0548, wobec 11.4 s i $0.0283 bez niego. Tego zadania nie mierzono ponownie na 3.15.0.
- **To, co instalujesz, nie jest dokładnie tym, co zmierzono.** Kompilacje zbudowano z commitów wydań, z wyłączonym logowaniem i wyłączonym procesem w tle. Podpisane pliki do pobrania nie były mierzone.
- **Próba jest mała.** Trzy sesje na konfigurację, jeden model, jeden mały nowy projekt, jedna maszyna, cztery sesje naraz. Traktuj ilorazy jako pomiar tego zadania, a nie jako obietnicę dla twojej pracy. Żadna sesja z tych trzech konfiguracji nie została odrzucona ani powtórzona. Nie zmierzyliśmy, jaka część twojej pracy przypomina to zadanie.

### Sprawdź samodzielnie

[Raport](../benchmarks/2026-11-22-standard-benchmark.md) publikuje trzy prompty (po portugalsku, z tłumaczeniem), opis każdego sprawdzenia z zewnątrz i liczby dla każdej sesji; [plik z danymi](../benchmarks/2026-11-22-standard-benchmark.json) zawiera je w formacie JSON. Środowisko testowe nie jest publikowane. Uruchom te same trzy prompty w swoim agencie, z włączonym i wyłączonym Simplicio, w małym własnym projekcie, i porównaj własne czasy oraz własny rachunek.

<a id="install"></a>

## Instalacja

Zainstaluj podpisany natywny plik binarny. Wybierz jeden sposób.

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

Python (PyPI):

```bash
python3 -m pip install --upgrade simplicio-installer
simplicio install
```

W systemie Windows użyj `py -m pip install --upgrade simplicio-installer`, a następnie `simplicio install`. Jeśli katalog skryptów Pythona nie jest w `PATH`, najpierw go dodaj.

Instalator pobiera najnowsze podpisane wydanie dla twojej platformy i sprawdza jego SHA-256 oraz podpis Ed25519. Dopiero wtedy zastępuje zainstalowany plik binarny. Umieszcza go w `~/.simplicio/bin/` (w systemie Windows w `%USERPROFILE%\.simplicio\bin\`) i automatycznie rejestruje Simplicio w agentach, które znajdzie. Błąd rejestracji zatrzymuje instalator zamiast zgłaszać sukces. Uruchom ponownie każdego agenta, który jest już otwarty, aby wczytał swoją konfigurację.

**Logowanie.** Wymagane jest logowanie przez Google, także w becie. Uruchom `simplicio auth login`, potem `simplicio auth status --json` i kontynuuj, gdy status zgłosi `active: true`. Rejestracja nie wymaga logowania, więc agenci są skonfigurowani jeszcze przed logowaniem. Nigdy nie wklejaj hasła ani tokenu do konfiguracji agenta.

<details>
<summary>Sprawdzanie, aktualizacja, usuwanie</summary>

Aby zaktualizować, uruchom instalator ponownie. Którykolwiek z instalatorów możesz uruchomić ponownie w dowolnym momencie, a zawsze ustali najnowsze wydanie. `install.sh` i `install.ps1` znajdują się w katalogu głównym tego repozytorium.

```bash
# macOS / Linux
sh install.sh --doctor
sh install.sh --uninstall --keep-data
sh install.sh --uninstall --purge       # needs SIMPLICIO_CONFIRM_PURGE=1; preserves ~/.simplicio/.env
```

```powershell
# Windows
pwsh install.ps1 -Doctor
pwsh install.ps1 -Uninstall -KeepData
pwsh install.ps1 -Uninstall -Purge      # needs SIMPLICIO_CONFIRM_PURGE=1; preserves .env
```

- `--doctor` sprawdza instalację.
- `--uninstall --keep-data` usuwa zainstalowany plik binarny i zachowuje twoje dane. Dotyczy to także 30-dniowego stanu logowania przez Google w `~/.simplicio/login.json`.
- `--uninstall --purge` usuwa tylko stan zarządzany przez Simplicio, w tym stan logowania. Zachowuje `~/.simplicio/.env`, w którym mogą być dane uwierzytelniające dostawców. Czyszczenie wymaga `SIMPLICIO_CONFIRM_PURGE=1`.
- Odinstalowanie nie zmienia konfiguracji twoich agentów. Wpisy Simplicio pozostają w każdym agencie, aż usuniesz je w ustawieniach tego agenta.
- Dane w katalogu `.simplicio` projektu nie są usuwane przez `--keep-data`. Zanim wybierzesz `--purge`, sprawdź miejsce docelowe.

Pełne szczegóły: [INSTALL.md](../INSTALL.md).

</details>

<a id="first-run"></a>

## Pierwsze uruchomienie

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` potwierdza zainstalowany plik binarny. `simplicio onboard` przygotowuje projekt za pierwszym razem. Potem otwórz w tym projekcie swojego agenta i pracuj jak zwykle. Aby sprawdzić, czy Simplicio się wczytało, poszukaj `simplicio` na liście serwerów MCP agenta. W Claude Code `/mcp` wyświetla podłączone serwery. Wolisz najpierw przeczytać instalator? Jest nim [install.sh](../install.sh).

<a id="works-with-the-agent-you-already-use"></a>

## Działa z agentem, którego już używasz

Simplicio to lokalny serwer MCP działający przez STDIO, więc każdy agent, który potrafi uruchomić lokalny serwer MCP, może zostać skierowany na Simplicio.

Instalator przekazuje rejestrację własnemu rejestratorowi Simplicio. Wykrywa agentów na twoim komputerze i zapisuje wpis Simplicio dla tych, które potrafi skonfigurować, w tym dla Claude Code, Codex, Cursor, Visual Studio Code, OpenCode, Gemini CLI i Kiro. Dwa pliki w tym repozytorium opisują, jak daleko sięga każda integracja:

- Rejestr [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) wymienia 43 identyfikatory agentów i dla każdego określa, jak Simplicio do niego dociera: wpis MCP, który zapisuje Simplicio (23), natywną wtyczkę lub rozszerzenie (5), przenośny pakiet wtyczki (4), prowadzoną konfigurację, którą wykonujesz samodzielnie (9), albo inne narzędzie wiersza poleceń (2).
- Macierz zgodności [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) mówi, co zostało zweryfikowane. Spośród tych 43 oznacza 12 agentów jako obsługiwanych, a 29 jako `unverified`, i nie ma wiersza dla Codex ani Gemini CLI. W przypadkach, gdy rejestr mówi, że Simplicio zapisuje wpis, a macierz podaje `unverified`, traktuj tę integrację jako nieprzetestowaną.

23 agentów ma przewodnik w [`docs/hosts/`](../docs/hosts/). Dla agentów, do których dociera się przez wtyczkę, wtyczka jest stosowana w osobnym kroku, który pyta cię o zgodę. Opisuje to [INSTALL.md](../INSTALL.md).

<details>
<summary>Wszystkich 43 agentów według tego, jak Simplicio do nich dociera</summary>

| Jak Simplicio do nich dociera | Liczba | Agenci |
|---|---|---|
| Wpis MCP, który zapisuje Simplicio | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| Natywna wtyczka lub rozszerzenie | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| Przenośny pakiet wtyczki | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| Prowadzona konfiguracja, którą wykonujesz samodzielnie | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| Inne narzędzie wiersza poleceń | 2 | **OrcaDev / Orca ADE**, T3 Code |

Pogrubienie: macierz zgodności oznacza agenta jako obsługiwanego.

</details>

Aby powtórzyć rejestrację, uruchom `simplicio mcp register`. Polecenie serwera to `simplicio serve --mcp --stdio`. Oto podstawowe narzędzia, które otrzymuje twój agent:

| Narzędzie | Co daje |
|---|---|
| `simplicio_map` | Zwarta mapa repozytorium, dzięki której agent się w nim orientuje |
| `simplicio_context` | Kontekst potrzebny zadaniu, ograniczony, zamiast całych plików |
| `simplicio_edit` | Ustrukturyzowane edycje plików z przygotowanego planu |
| `simplicio_validate` | Sprawdzenia potoku, testów i dostarczenia |
| `simplicio_run` | Uruchomienie zadania pod kontrolą Simplicio |

Aktualna lista to ta, którą serwer zgłasza przy starcie. [MCP-CONNECT.md](../MCP-CONNECT.md) opisuje podstawowe narzędzia.

<details>
<summary>Konfiguracja ręczna</summary>

Jeśli twój agent nie został skonfigurowany automatycznie, dodaj ten wpis do jego konfiguracji MCP. Zamień ścieżkę na bezwzględną ścieżkę zainstalowanego pliku binarnego.

```json
{
  "mcpServers": {
    "simplicio": {
      "command": "/absolute/path/to/.simplicio/bin/simplicio",
      "args": ["serve", "--mcp", "--stdio"]
    }
  }
}
```

Codex czyta TOML. Agenci uruchamiają `command` bezpośrednio, więc nie używaj `~` i nie polegaj na rozwijaniu przez powłokę. W ścieżkach Windows używaj ukośników w przód i zamień przykładową nazwę użytkownika.

Windows:

```toml
[mcp_servers.simplicio]
command = "C:/Users/YourName/.simplicio/bin/simplicio.exe"
args = ["serve", "--mcp", "--stdio"]
```

macOS:

```toml
[mcp_servers.simplicio]
command = "/Users/your-name/.simplicio/bin/simplicio"
args = ["serve", "--mcp", "--stdio"]
```

Linux:

```toml
[mcp_servers.simplicio]
command = "/home/your-name/.simplicio/bin/simplicio"
args = ["serve", "--mcp", "--stdio"]
```

Gdzie każdy agent trzyma swój plik: [MCP-CONNECT.md](../MCP-CONNECT.md).

</details>

<a id="command-line"></a>

## Wiersz poleceń

| Polecenie | Co otrzymujesz |
|---|---|
| `simplicio map --repo . --for-llm markdown` | Zwarta mapa strukturalna repozytorium, zapisana tak, by model mógł ją czytać |
| `simplicio context --repo .` | Ograniczony kontekst dla zadania |
| `simplicio memory query "query" --json` | To, co projekt już wie, odczytane z jego zindeksowanej pamięci, w formacie JSON |
| `simplicio edit --plan plan.json --repo .` | Przygotowany zestaw ustrukturyzowanych edycji, zastosowany do plików |
| `simplicio run "task" --repo . --agents N` | Uruchomienie zadania z N agentami pod kontrolą Simplicio |
| `simplicio loop` | Praca prowadzona w rundach, aż się zbiegnie |

Nazwy, które zobaczysz w komunikatach Simplicio: Mapper obserwuje, Fast rzutuje lub pobiera, Dev CLI edytuje, Runtime zarządza i Loop zbiega się.

<a id="safety-and-privacy"></a>

## Bezpieczeństwo i prywatność

Ta sekcja opisuje wersję 3.15.0.

**Co Simplicio wysyła i do kogo**

- **Zostaje na twoim komputerze.** Mapowanie, kontekst, edycje i sprawdzenia działają wewnątrz pliku binarnego Simplicio. Przekazuje wyniki twojemu agentowi na tym samym komputerze. To, co agent wysyła do swojego dostawcy modelu, zależy od agenta, jak dotychczas.
- **Do SimpleTI (simpleti.com.br).** Wyłącznie logowanie i sprawdzanie planu. Przesyłają twój token logowania, wersję Simplicio i nazwę hosta twojego komputera. Opcjonalne sprawdzenie licencji przesyła też adres e-mail konta. Zwracają adres e-mail konta, nazwę i plan. Bez treści repozytorium: bez plików, ścieżek plików, promptów i edycji.
- **Do GitHub.** Sprawdzanie w tle, czy nie ma nowego wydania, najwyżej około raz na 12 godzin. Nie przesyła niczego o tobie ani o twoim kodzie. Aby je wyłączyć, ustaw `SIMPLICIO_DISABLE_AUTO_UPDATE=1`. Podczas aktualizacji nowy plik binarny jest pobierany z GitHuba, a jego SHA-256 i podpis są sprawdzane, zanim zastąpi stary.
- **Brak analityki.** Simplicio 3.15.0 oraz pliki, które instaluje w twoich agentach, zostały pod tym kątem sprawdzone: żaden nie wysyła analityki, raportów o awariach ani danych o użyciu. Zapisy zużycia i oszczędności są plikami lokalnymi. Haki, które instaluje, uruchamiają wyłącznie lokalne programy (plik binarny Simplicio oraz, dla opcjonalnych wtyczek, lokalne skrypty); żaden z nich nie łączy się z siecią.
- **Do usług, które skonfigurujesz.** Dostawca modelu, GitHub, Jira, powiadomienia w czacie lub wspólna pamięć podręczna zespołu otrzymują to, co wysyła dana funkcja, a może to obejmować prompty i kod. Żądania do dostawcy modelu niosą nagłówek, który wskazuje Simplicio jako klienta.
- **Dwie funkcje łączą się z ogólnodostępną usługą w internecie bez żadnej konfiguracji.** Wyszukiwanie w sieci, gdy działa, wysyła zapytanie do DuckDuckGo, chyba że skonfigurujesz inną usługę wyszukiwania. We własnym czacie Simplicio wiadomość, która wygląda jak pytanie o sieć, może stać się tym zapytaniem. Audyt bezpieczeństwa zależności, gdy go uruchomisz, wysyła nazwy i wersje twoich zależności do osv.dev. Żadna z tych funkcji nie wysyła zawartości plików.
- **Pobieranie.** Instalator i mechanizm aktualizacji pobierają z GitHuba. Niektóre opcjonalne skrypty pomocnicze pobierają własne narzędzia z PyPI lub npm, gdy je uruchomisz. Jeśli wtyczka agenta startuje i nie znajdzie pliku binarnego Simplicio, pobiera oficjalny instalator z GitHuba, przypięty do konkretnego commita i sprawdzony przez SHA-256.

**Podpisane wydania.** Każde wydanie publikuje swoje pliki binarne z sumami kontrolnymi SHA-256, podpisami Ed25519, SBOM (listą składników kompilacji) i pochodzeniem kompilacji (build provenance). Instalatory i mechanizm aktualizacji sprawdzają sumę kontrolną i podpis, zanim zastąpią zainstalowany plik binarny. W przypadku stabilnych wydań kontrakt sprawia, że brakujący lub nieprawidłowy podpis oraz niezgodność sumy kontrolnej są twardymi błędami. Kontrakt znajduje się w [docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md).

**Co instalator zmienia w agencie.** Dodaje wpis Simplicio do konfiguracji MCP agenta i zachowuje resztę konfiguracji. W Claude Code dodatkowo zezwala na `mcp__simplicio__*`, więc narzędzie Simplicio nie jest blokowane w trybie auto. W agentach, których interfejs haków instalator zweryfikował, instaluje tam także haki Simplicio. [INSTALL.md](../INSTALL.md) opisuje, co zapisuje instalator, a przewodnik każdego agenta w [`docs/hosts/`](../docs/hosts/) podaje szczegóły. Odinstalowanie nie cofa tych wpisów. Sekcja Instalacja mówi, jak je usunąć.

## Także w tym repozytorium

<details>
<summary>Aplikacja Desktop (podgląd dla macOS)</summary>

Podgląd aplikacji Desktop dla macOS (Apple Silicon) jest publikowany jako [Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg). Jego SHA-256 znajduje się w [DESKTOP-SHA256SUMS](../DESKTOP-SHA256SUMS), osobno od sum kontrolnych plików binarnych Simplicio. Obraz DMG nie ma pliku podpisu i zawiera plik binarny Simplicio 3.8.47.

- Windows Desktop nie jest publikowany. W systemie Windows użyj instalacji z wiersza poleceń powyżej.
- Podpisywanie Apple Developer ID i notaryzacja nie zostały wykonane. Pakiet jest podpisany ad hoc, czyli bez certyfikatu dewelopera Apple, a akceptacja przez Gatekeeper nie jest deklarowana, więc macOS może ostrzec cię przy otwarciu.
- Instalacja z wiersza poleceń powyżej jest obsługiwaną publiczną ścieżką instalacji, dopóki nie zostanie opublikowany podpisany pakiet Desktop.

Szczegóły: [docs/desktop/RELEASE.md](../docs/desktop/RELEASE.md).

</details>

<details>
<summary>Dla opiekunów: wygenerowany diagram przepływu</summary>

Polecenia i narzędzia opisane w README.md i MCP-CONNECT.md są narysowane jako jeden przepływ, [docs/flow/simplicio.svg](../docs/flow/simplicio.svg), wygenerowany z jednego pliku źródłowego, `docs/flow/simplicio.flow.json`. Wygeneruj go ponownie poleceniem `python3 scripts/generate_flow.py`, a poleceniem `python3 scripts/generate_flow.py --check` sprawdź, czy nie ma rozbieżności. Kontrakt, który utrzymuje go w zgodzie z tą stroną i z MCP-CONNECT.md, to `python3 -m pytest tests/test_flow_contract.py -q`. Sprawdzenie importu Langflow to `scripts/verify_flow_langflow.py`. Kończy się w trybie zamkniętym (exit 2, `status=blocked`), gdy żaden serwer nie działa. Dowody znajdują się w `docs/flow/evidence/` i `docs/flow/render/`, a [docs/flow/README.md](../docs/flow/README.md) zawiera wymagania i opis, jak to powtórzyć.

</details>

<a id="questions-people-ask"></a>

## Pytania, które ludzie zadają

**Czy porównanie jest uczciwe?**<br>
Ten sam agent, ten sam model, te same trzy prompty, ten sam początkowy projekt i te same sprawdzenia z zewnątrz, w jednej rundzie. Punkt odniesienia nie ma serwera MCP ani konfiguracji Simplicio. Zobacz [Gdzie Simplicio nie wygrywa](#where-simplicio-does-not-win) oraz [Ograniczenia](../benchmarks/2026-11-22-standard-benchmark.md#limits) w raporcie.

**Czy muszę zmienić agenta lub model?**<br>
Nie. Simplicio podłącza się do agenta, którego już używasz. W powyższym benchmarku każda konfiguracja używała tego samego agenta i tego samego modelu.

**Czy zawsze dostanę te liczby?**<br>
Nie. Mierzą jedno zadanie, z jednym modelem, na jednej maszynie, w trzech sesjach na konfigurację. Zobacz [Gdzie Simplicio nie wygrywa](#where-simplicio-does-not-win) i uruchom porównanie na własnej pracy.

**Czy to open source?**<br>
Nie. Simplicio jest oprogramowaniem zastrzeżonym. To podpisany plik binarny, publikowany jako załączniki wydań, a jego kod źródłowy nie jest publiczny. To repozytorium zawiera instalatory, pakiety dla agentów, kod źródłowy aplikacji Desktop, dokumentację i dane benchmarku.

**Jak to usunąć?**<br>
Uruchom `sh install.sh --uninstall --keep-data`, a w systemie Windows `pwsh install.ps1 -Uninstall -KeepData`. Usuwa to plik binarny i zachowuje twoje dane. Nie zmienia konfiguracji twoich agentów, więc usuń wpisy Simplicio w ustawieniach każdego agenta. [Instalacja](#install) zawiera szczegóły i opcję czyszczenia.

**Czy potrzebuję konta?**<br>
Tak. Wymagane jest logowanie przez Google, także w becie. Uruchom `simplicio auth login`.

**Czy mój kod opuszcza mój komputer?**<br>
Mapowanie, kontekst, edycje i sprawdzenia działają na twoim komputerze. Simplicio rozmawia z SimpleTI w sprawie logowania i sprawdzania planu oraz z GitHubem w poszukiwaniu aktualizacji. W obu przypadkach nie ma treści repozytorium. Funkcje, które konfigurujesz lub uruchamiasz, mogą docierać do innych usług. Pełna lista znajduje się w [Co Simplicio wysyła i do kogo](#safety-and-privacy).

<a id="documentation-and-community"></a>

## Dokumentacja i społeczność

- **Strona:** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **Dokumentacja:** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord:** [Dołącz do społeczności](https://discord.gg/wM6tr7xVb)
- **Zgłoszenia:** [tracker zgłoszeń GitHub](https://github.com/simpletibr/simplicio/issues)
- **W tym repozytorium:** [INSTALL.md](../INSTALL.md), [MCP-CONNECT.md](../MCP-CONNECT.md) i [docs/hosts/](../docs/hosts/)
- **Powiązane:** Simplicio Video (hypit). Aby je sklonować: `git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio jest zarejestrowanym oprogramowaniem zastrzeżonym. Wszelkie prawa zastrzeżone.</sub>
</p>
