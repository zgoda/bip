Instalacja i uruchomienie
=========================

Aplikacja BIP może zostać uruchomiona zarówno samodzielnie, jak i w postaci kontenerów. Ten dokument opisuje oba te sposoby, kładąc jednak nacisk na instalację samodzielną, ponieważ jej zasady dotyczą również instalacji w postaci kontenerów, a sposób ten daje najwięcej możliwości dostosowania instalacji do dostępnych warunków.

Instalacja samodzielna
----------------------

Do uruchomienia serwisu w wersji samodzielnej wymagany jest dostęp do powłoki serwera, na którym będzie zainstalowana aplikacja (tzw. *shell*). Dla pełnej instalacji wymagane są również uprawnienia administracyjne w systemie operacyjnym.

Minimalne wymagania sprzętowe
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

W nawiasie podane są wartości *zadowalające*. Wartości minimalne dotyczą serwisów o niewielkim ruchu, nie przekraczającym 100 odsłon na godzinę i obsługiwanych przez jednego redaktora jednocześnie. Proszę pamiętać, że przy używaniu serwera bazy danych wymagane zasoby wzrosną co najmniej o 1 core, a ilość RAM do co najmniej 2 GB.

* CPU: 1 core (2 core)
* RAM: 1 GB (2 GB)
* wolna przestrzeń dyskowa: 2 GB

Wymagane oprogramowanie
^^^^^^^^^^^^^^^^^^^^^^^

* Python 3.7 lub nowszy
* serwer HTTP (np. Nginx, Apache, Lighttpd)
* serwer aplikacji WSGI (np. uWSGI, Gunicorn)

Oprogramowanie opcjonalne
^^^^^^^^^^^^^^^^^^^^^^^^^

* serwer bazy danych (PostgreSQL lub MySQL)

Instalacja samodzielna krok po kroku
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
