Instalacja i uruchomienie
=========================

Dokument ten opisuje sposób instalacji i konfiguracji aplikacji BIP w systemie Linux. Podane poniżej polecenia odpowiadają tym w Debianie 10 i Ubuntu. Dla systemów bazujących na RPM (Fedora, Centos) trzeba będzie je odpowiednio zmodyfikować.

Zalecane systemy operacyjne
---------------------------

Aplikacja BIP może działać w każdym systemie operacyjnym, w którym jest dostępny Python 3.7 lub nowszy, jednak została ona przetestowana wyłącznie w systemie Linux, do tego systemu również odnosi się ta instrukcja. Instrukcja została przygotowana w oparciu o systemy Debian 10 i Ubuntu 18.04, ponieważ są dla nich dostępne pakiety Pythona 3.7 (w Debianie 10 jest on dostępny w systemie, dla Ubuntu 18.04 możliwe jest zainstalowanie go używając PPA ``deadsnakes``). Z pewnością jest możliwe uruchomienie aplikacji na innych dystrybucjach Linuksa, jednak nie zostało to przetestowane przez autora.

Minimalne wymagania sprzętowe
-----------------------------

W nawiasie podane są wartości *zadowalające*. Wartości minimalne dotyczą serwisów o niewielkim ruchu, nie przekraczającym 100 odsłon na godzinę i obsługiwanych przez jednego redaktora jednocześnie. Proszę pamiętać, że przy używaniu serwera bazy danych wymagane zasoby wzrosną co najmniej o 1 core, a ilość RAM do co najmniej 2 GB.

* CPU: 1 core (2 core)
* RAM: 1 GB (2 GB)
* wolna przestrzeń dyskowa: 2 GB

Instalacja aplikacji
--------------------

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

Instalacja aplikacji krok po kroku
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Zalecam, by instalację przeprowadzić na zwykłym (nie administracyjnym) koncie użytkownika. Można do tego celu utworzyć nowe konto, ale zazwyczaj nie ma takiej potrzeby. Aplikacja zainstalowana w sposób opisany w tej instrukcji będzie działała używając uprawnień *zwykłego* użytkownika, a do działania w ogóle nie potrzebuje uprawnień administracyjnych.

Zainstaluj wszystkie niezbędne narzędzia programistyczne oraz wymagane dodatkowe pakiety związane z Pythonem.

.. code-block:: shell-session

    $ sudo apt install build-essential libffi-dev python3-venv python3-dev

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

Innym rodzajem zawartości serwisu są pliki udostępnione do pobrania. Aplikacja umieszcza je we wskazanym miejscu i je również dobrze będzie trzymać tam gdzie i całą resztę. Ścieżka do tego katalogu jest później przekazana w zmiennej środowiskowej.

.. code-block:: shell-session

    $ mkdir -p instance/attachments

Utwórz również katalog na statyczne dane konfiguracji serwisu i skopiuj do niego przykładowy plik konfiguracją serwisu.

.. code-block:: shell-session

    $ mkdir conf
    $ wget -O conf/site.json https://raw.githubusercontent.com/zgoda/bip/master/conf/site.json.example

W ten sposób zainstalowana aplikacja jest gotowa do uruchmonienia pod kontrolą serwera aplikacji WSGI.

Instalacja, konfiguracja i uruchomienie serwera aplikacji WSGI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Najpopularniejszymi serwerami aplikacji WSGI są uWSGI i Gunicorn. Każdy z nich dostarcza różnych możliwości uruchomienia aplikacji:

* uWSGI: jako samodzielny proces i zintegrowany z serwerem WWW Nginx
* Gunicorn jako samodzielny proces

Uruchomienie jako samodzielny proces daje możliwość wykorzystania dowolnego serwera WWW jako *reverse proxy*, natomiast ścisła integracja z Nginx ułatwia konfigurację.

W ramach przykładu pokazane zostanie uruchomienie aplikacji pod kontrolą uWSGI działającego w integracji z serwerem WWW Nginx oraz pod kontrolą Gunicorn z serwerem Nginx działającym jako *reverse proxy*. Przykładowe pliki konfiguracyjne można pobrać ze `źródłowego repozytorium Git projektu <https://github.com/zgoda/bip/tree/master/conf>`_.

uWSGI + Nginx
~~~~~~~~~~~~~

Na początek należy zainstalować wymagane oprogramowanie. Dla uproszczenia wszystkie polecenia wykonywane będą z katalogu domowego aplikacji jak to jest opisane wcześniej, oraz przy aktywnym środowisku wirtualnym Pythona - jeżeli nie jest aktywne to należy je zawczasu aktywować.

.. code-block:: shell-session

    $ sudo apt install nginx
    $ pip install -U uwsgi

W tym momencie powinno być już możliwe uruchomienie uWSGI jako samodzielnego kontenera aplikacji WSGI.

.. code-block:: shell-session

    $ export ENV="production"
    $ uwsgi --socket 0.0.0.0:5000 --protocol=http -w bip.wsgi:application

W ten sposób uruchomiony serwer powinien być dostępny z zewnątrz na porcie 5000. Po weryfikacji że tak rzeczywiście się dzieje można go wyłączyć kombinacją klawiszy Ctrl+C i przystąpić do konfiguracji aplikacji w kontenerze WSGI.

.. code-block:: shell-session

    $ vim bip.ini

W pliku należy umieścić poniższą zawartość (linie zaczynające się od ``#`` są komentarzem i mogą zostać pominięte).

.. code-block:: ini

    [uwsgi]
    # lokalizacja obiektu aplikacji
    module = bip.wsgi:application

    # uruchom proces zarządzający i 2 procesy robocze
    master = true
    processes = 2

    # komunikacja z Nginx będzie się odbywać poprzez wspólne gniazdo
    socket = /tmp/bip.sock
    chmod-socket = 660
    vacuum = true

    # obsługa sygnału zakończenia
    die-on-term = true

Za nadzór nad uruchomieniem całości będzie odpowiadał ``systemd``, dla którego potrzebny będzie również plik sterujący, tzw. *unit*.

.. code-block:: shell-session

    $ sudo vim /etc/systemd/system/bip.service

W pliku tym należy umieścić poniższą zawartość. Proszę zwrócić uwagę, że ``systemd`` wszędzie w konfiguracji wymaga ścieżek absolutnych. W poniższym przykładzie należy zmienić ``mojekonto`` na rzeczywistą nazwę konta, na jakim została zainstalowana aplikacja.

.. code-block:: ini

    [Unit]
    Description=uruchomienie BIP jako aplikacji WSGI (uWSGI)
    # uruchom serwis po pełnej konfiguracji sieci
    After=network.target

    [Service]
    # użytkownik który uruchomi proces usługi
    User=mojekonto
    # grupa www-data jest również używana przez Nginx
    Group=www-data
    # ustawienie zmiennej ścieżki wyszukiwania programów
    Environment="PATH=/home/mojekonto/bip/venv/bin"
    # ustawienie zmiennej rodzaju instancji
    Environment="ENV=production"
    # ustawienie zmiennej z katalogiem plików do pobrania
    Environment="INSTANCE_PATH=/home/mojekonto/bip/instance"
    # komenda uruchamiająca usługę
    ExecStart=/home/mojekonto/bip/venv/bin/uwsgi --ini /home/mojekonto/bip/bip.ini

    [Install]
    # w którym momencie włączyć usługę, multi-user to ostatni krok
    WantedBy=multi-user.target

Po zapisaniu tego pliku będzie możliwe uruchomienie usługi pod kontrolą zarządcy ``systemd``.

.. code-block:: shell-session

    $ sudo systemctl start bip
    $ sudo systemctl enable bip
    $ sudo systemctl status bip

Ostatnie polecenie powinno dać skutek jak na poniższym obrazku.

.. image:: /_static/install_uwsgi_debian10.png

Tak skonfigurowana usługa będzie się uruchamiała automatycznie po każdym restarcie systemu.

Ostatnim krokiem jest konfiguracja serwera WWW Nginx aby komunikował się z aplikacją.

.. code-block:: shell-session

    $ sudo vim /etc/nginx/sites-available/bip

W pliku tym należy umieścić poniższą zawartość. ``bip.domena.pl`` oraz ``mojekonto`` należy zastąpić rzeczywistymi wartościami, tj. nazwą domenową serwera oraz prawdziwą nazwą konta użytkownika, na którym została zainstalowana aplikacja.

.. code-block:: nginx

    server {
        listen 80;
        server_name bip.domena.pl;

        location / {
            # zmiana początku ścieżki do plików do pobrania
            rewrite ^/files/(.*)$ /attachments/$1 last;
            # włączenie obsługi uWSGI
            include uwsgi_params;
            uwsgi_pass unix:/tmp/bip.sock;
            uwsgi_param UWSGI_SCHEME $scheme;
            uwsgi_param SERVER_SOFTWARE nginx/$nginx_version;
        }

        # reguła dla zasobów statycznych
        location /static {
            root /home/mojekonto/bip;
            sendfile on;
            sendfile_max_chunk 1m;
        }

        # reguła dla plików do pobrania
        location /attachments {
            root /home/mojekonto/instance;
            sendfile on;
            sendfile_max_chunk 1m;
            # pliki mają zawsze być pobierane, a nie wyświetlane
            if ($arg_f) {
                add_header Content-Disposition "attachment; filename=$arg_f";
            }
        }
    }

Plik ten należy ostatecznie zlinkować do katalogu z konfiguracjami włączonych aplikacji.

.. code-block:: shell-session

    $ sudo ln -s /etc/nginx/sites-available/bip /etc/nginx/sites-enabled
    $ sudo systemctl reload nginx

Po przeładowaniu konfiguracji Nginxa aplikacja powinna być już dostępna pod adresem domenowym podanym w powyższym przykładzie.

Gunicorn + Nginx
~~~~~~~~~~~~~~~~

Na początek należy zainstalować wymagane oprogramowanie. Dla uproszczenia wszystkie polecenia wykonywane będą z katalogu domowego aplikacji jak to jest opisane wcześniej, oraz przy aktywnym środowisku wirtualnym Pythona - jeżeli nie jest aktywne to należy je zawczasu aktywować.

.. code-block:: shell-session

    $ sudo apt install nginx
    $ pip install -U gunicorn

W tym momencie powinno być już możliwe uruchomienie Gunicorn jako samodzielnego kontenera aplikacji WSGI.

.. code-block:: shell-session

    $ export ENV="production"
    $ gunicorn --bind 0.0.0.0:5000 bip.wsgi:application

W ten sposób uruchomiony serwer powinien być dostępny z zewnątrz na porcie 5000. Po weryfikacji że tak rzeczywiście się dzieje można go wyłączyć kombinacją klawiszy Ctrl+C i przystąpić do konfiguracji uruchamiania kontenera WSGI przez ``systemd``. W tym celu należy utworzyć plik kontrolny dla ``systemd``, tzw *unit*.

.. code-block:: shell-session

    $ sudo vim /etc/systemd/system/bip.service

Zawartość tego pliku bedzie podobna jak w przypadku uWSGI we wcześniejszym przykładzie, inne bedzie tylko polecenie uruchamiające usługę. Podobnie jak w przypadku ustawień dla uWSGI trzeba zamienić ``mojekonto`` na rzeczywistą nazwę konta, na którym została zainstalowana aplikacja.

.. code-block:: ini

    [Unit]
    Description=uruchomienie BIP jako aplikacji WSGI (Gunicorn)
    # uruchom serwis po pełnej konfiguracji sieci
    After=network.target

    [Service]
    # użytkownik który uruchomi proces usługi
    User=mojekonto
    # grupa www-data jest również używana przez Nginx
    Group=www-data
    # ustawienie zmiennej ścieżki wyszukiwania programów
    Environment="PATH=/home/mojekonto/bip/venv/bin"
    # ustawienie zmiennej rodzaju instancji
    Environment="ENV=production"
    # ustawienie zmiennej z katalogiem plików do pobrania
    Environment="INSTANCE_PATH=/home/mojekonto/bip/instance"
    # komenda uruchamiająca usługę
    ExecStart=/home/mojekonto/bip/venv/bin/gunicorn --workers 2 --bind unix:/tmp/bip.sock -m 007 bip.wsgi:application

    [Install]
    # w którym momencie włączyć usługę, multi-user to ostatni krok
    WantedBy=multi-user.target

Po zapisaniu tego pliku będzie możliwe uruchomienie usługi pod kontrolą zarządcy ``systemd``.

.. code-block:: shell-session

    $ sudo systemctl start bip
    $ sudo systemctl enable bip
    $ sudo systemctl status bip

Ostatnie polecenie powinno dać skutek jak na poniższym obrazku.

.. image:: /_static/install_gunicorn_debian10.png

Tak skonfigurowana usługa będzie się uruchamiała automatycznie po każdym restarcie systemu.

Ostatnim krokiem jest konfiguracja serwera WWW Nginx aby komunikował się z aplikacją.

.. code-block:: shell-session

    $ sudo vim /etc/nginx/sites-available/bip

W pliku tym należy umieścić poniższą zawartość. ``bip.domena.pl`` oraz ``mojekonto`` należy zastąpić rzeczywistymi wartościami, tj. nazwą domenową serwera oraz prawdziwą nazwą konta użytkownika, na którym została zainstalowana aplikacja.

.. code-block:: nginx

    server {
        listen 80;
        server_name bip.domena.pl;

        location / {
            # zmiana początku ścieżki do plików do pobrania
            rewrite ^/files/(.*)$ /attachments/$1 last;
            # włączenie proxy
            include proxy_params;
            proxy_pass http://unix:/tmp/bip.sock;
        }

        # reguła dla zasobów statycznych
        location /static {
            root /home/mojekonto/bip;
            sendfile on;
            sendfile_max_chunk 1m;
        }

        # reguła dla plików do pobrania
        location /attachments {
            root /home/mojekonto/instance;
            sendfile on;
            sendfile_max_chunk 1m;
            # pliki mają zawsze być pobierane, a nie wyświetlane
            if ($arg_f) {
                add_header Content-Disposition "attachment; filename=$arg_f";
            }
        }

    }

Plik ten należy ostatecznie zlinkować do katalogu z konfiguracjami włączonych aplikacji.

.. code-block:: shell-session

    $ sudo ln -s /etc/nginx/sites-available/bip /etc/nginx/sites-enabled
    $ sudo systemctl reload nginx

Po przeładowaniu konfiguracji Nginxa aplikacja powinna być już dostępna pod adresem domenowym podanym w powyższym przykładzie.
