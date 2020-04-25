Instalacja i uruchomienie
=========================

Aplikacja BIP może zostać uruchomiona zarówno samodzielnie, jak i w postaci kontenerów. Ten dokument opisuje oba te sposoby, kładąc jednak nacisk na instalację samodzielną, ponieważ jej zasady dotyczą również instalacji w postaci kontenerów, a sposób ten daje najwięcej możliwości dostosowania instalacji do dostępnych warunków.

Zalecane systemy operacyjne
---------------------------

Aplikacja BIP może działać w każdym systemie operacyjnym, w którym jest dostępny Python 3.7, jednak została ona przetestowana wyłącznie w systemie Linux, do tego systemu również odnosi się ta instrukcja. Instrukcja została przygotowana w oparciu o systemy Debian 10 i Ubuntu 18.04, ponieważ są dla nich dostępne pakiety Pythona 3.7 (w Debianie 10 jest on dostępny w systemie, dla Ubuntu możliwe jest zainstalowanie go używając PPA ``deadsnakes``). Z pewnością jest możliwe uruchomienie aplikacji na innych dystrybucjach Linuksa, jednak nie zostało to przetestowane przez autora.

Minimalne wymagania sprzętowe
-----------------------------

W nawiasie podane są wartości *zadowalające*. Wartości minimalne dotyczą serwisów o niewielkim ruchu, nie przekraczającym 100 odsłon na godzinę i obsługiwanych przez jednego redaktora jednocześnie. Proszę pamiętać, że przy używaniu serwera bazy danych wymagane zasoby wzrosną co najmniej o 1 core, a ilość RAM do co najmniej 2 GB.

* CPU: 1 core (2 core)
* RAM: 1 GB (2 GB)
* wolna przestrzeń dyskowa: 2 GB

Uruchmienie instalacji w kontenerze będzie wymagało nieznacznie więcej zasobów.

Instalacja samodzielna
----------------------

Do uruchomienia serwisu w wersji samodzielnej wymagany jest dostęp do powłoki serwera, na którym będzie zainstalowana aplikacja (tzw. *shell*). Dla pełnej instalacji wymagane są również uprawnienia administracyjne w systemie operacyjnym.

Wymagane oprogramowanie
^^^^^^^^^^^^^^^^^^^^^^^

* Python 3.7 lub nowszy
* narzędzia do budowania kodu
* biblioteka ``ffi``
* serwer HTTP (np. Nginx, Apache, Lighttpd)
* serwer aplikacji WSGI (np. uWSGI, Gunicorn)

Oprogramowanie opcjonalne
^^^^^^^^^^^^^^^^^^^^^^^^^

* serwer bazy danych (PostgreSQL lub MySQL)

Instalacja samodzielna krok po kroku
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Zalecam, by instalację przeprowadzić na zwykłym (nie administracyjnym) koncie użytkownika. Można do tego celu utworzyć nowe konto, ale zazwyczaj nie ma takiej potrzeby. Aplikacja zainstalowana w sposób opisany w tej instrukcji będzie działała używając uprawnień *zwykłego* użytkownika, a do działania w ogóle nie potrzebuje uprawnień administracyjnych.

Zainstaluj wszystkie niezbędne narzędzia programistyczne.

.. code-block:: shell-session

    $ sudo apt install build-essential libffi-dev

Utwórz katalog na instalację aplikacji.

.. code-block:: shell-session

    $ mkdir bip
    $ cd bip

Od tej pory wszystkie polecenia wydaje się w katalogu aplikacji.

Utwórz wirtualne środowisko uruchomieniowe Pythona i aktywuj je. Wspierane są wersje 3.7 i nowsze.

.. code-block:: shell-session

    $ /usr/bin/python3.7 -m venv venv
    $ source venv/bin/activate

Zaktualizuj podstawowe pakiety służące do instalacji.

.. code-block:: shell-session

    $ pip install -U pip wheel

Zainstaluj aplikację. Najprościej jest to zrobić używając pakietu instalacyjnego z PyPI.

.. code-block:: shell-session

    $ pip install -U biuletyn-bip

Po zakończeniu instalacji utwórz w katalogu aplikacji łącze symboliczne do katalogu zawierającego statyczną zawartość serwisu.

.. code-block:: shell-session

    $ ln -s venv/lib/python3.7/site-packages/bip/static static

Utwórz również katalog na statyczne dane konfiguracji serwisu i skopiuj do niego przykładowy plik konfiguracją serwisu.

.. code-block:: shell-session

    $ mkdir conf
    $ wget -O conf/site.json https://raw.githubusercontent.com/zgoda/bip/master/conf/site.json.example
