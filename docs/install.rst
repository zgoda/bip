Instalacja i uruchomienie
=========================

Dokument ten opisuje sposób instalacji i konfiguracji aplikacji BIP w systemie Linux. Podane poniżej polecenia odpowiadają tym w Debianie 10 i Ubuntu. Dla systemów bazujących na RPM (Fedora, Centos) trzeba będzie je odpowiednio zmodyfikować.

Zalecane systemy operacyjne
---------------------------

Aplikacja BIP może działać w każdej dystrybucji Linuksa, w której jest dostępny Python 3.7 lub nowszy, jednak została ona przetestowana wyłącznie w systemach opartych na Debianie, do takich systemów również odnosi się ta instrukcja. Instrukcja została przygotowana w oparciu o systemy Debian 10 i Ubuntu 20.04, ponieważ są dla nich dostępne pakiety Pythona 3.7 (Debian 10) lub 3.8 (Ubuntu 20.04). Dla Ubuntu 18.04 możliwe jest pobranie wymaganych wersji Pythona z repozytorium PPA `Deadsnakes <https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa?field.series_filter=bionic>`_.

Z pewnością jest możliwe uruchomienie aplikacji na innych dystrybucjach Linuksa, jednak nie zostało to przeze mnie przetestowane. Instalacja w systemie Windows, jakkolwiek teoretycznie możliwa, raczej nie wchodzi w grę z powodu użycia kilku bibliotek, które wymagają kompilacji rozszerzenia w C lub C++.

Minimalne wymagania sprzętowe
-----------------------------

W nawiasie podane są wartości *zadowalające*. Wartości minimalne dotyczą serwisów o niewielkim ruchu, nie przekraczającym 100 odsłon na godzinę i obsługiwanych przez jednego redaktora jednocześnie. Proszę pamiętać, że przy używaniu serwera bazy danych wymagane zasoby wzrosną co najmniej o 1 rdzeń, a ilość RAM do co najmniej 2 GB.

* CPU: 1 core (2 core)
* RAM: 1 GB (2 GB)
* wolna przestrzeń dyskowa: 2 GB

Włączenie HTTPS/SSL
-------------------

Ze względów bezpieczeństwa oraz wizerunkowych polecam zabezpiecznie dostępu do aplikacji poprzez skierowanie całej komunikacji z serwerem WWW przez kanał bezpieczny. Konkretna konfiguracja powinna zostać przeprowadzona zgodnie z instrukcją dla wybranego serwera WWW otrzymaną od dostawcy certyfikatu. W przypadku nie posiadania dedykowanego certyfikatu najlepszym wyjściem będzie użycie darmowego (co bynajmniej nie oznacza gorszego) certyfikatu od `Let's Encrypt <https://letsencrypt.org/>`_. Instalacja certyfikatu i konfiguracja serwera WWW są przeprowadzane przy użyciu `programu Certbot <https://certbot.eff.org/>`_, którego dokumentacja przeprowadzi przez proces krok po kroku.

.. image:: /_static/certbot_nginx_debian10.png

Certbot dostarcza zautomatyzowane procedury instalacji i odnowienia certyfikatu SSL dla serwerów WWW Apache i Nginx uruchomionych na wielu popularnych dystrybucjach Linuksa, w tym również dla Debiana i Ubuntu.

Instalacja aplikacji
--------------------

Do uruchomienia serwisu w wersji samodzielnej wymagany jest dostęp do powłoki serwera, na którym będzie zainstalowana aplikacja (tzw. *shell*). Dla pełnej instalacji wymagane są również uprawnienia administracyjne w systemie operacyjnym.

Wymagane oprogramowanie
^^^^^^^^^^^^^^^^^^^^^^^

* Python 3.7 lub nowszy
* narzędzia do budowania kodu
* biblioteka ``ffi`` (pakiet binarny i nagłówkowy)
* biblioteka ``icu`` (pakiet binarny i nagłówkowy)
* biblioteka ``magic`` (pakiet binarny i nagłówkowy)
* serwer HTTP (np. Nginx, Apache, Lighttpd)
* serwer aplikacji WSGI (np. uWSGI, Gunicorn)

Oprogramowanie opcjonalne
^^^^^^^^^^^^^^^^^^^^^^^^^

* serwer bazy danych (PostgreSQL lub MySQL)

Jeszcze słówko na temat przechowywania danych przez aplikację. Decyzję o tym, czy używać bazy serwerowej jak PostgreSQL czy MySQL proszę podjąć po dokonaniu oceny zarówno docelowej wielkości serwisu, jak i tego jak będzie on obsługiwany od strony edytorskiej. W sytuacji gdy serwis będzie miał jednego lub dwóch edytorów, którzy dodatkowo rzadko będą prowadzić edycję zawartości jednocześnie, a ilość stron nie przekroczy 1000, serwerowa baza danych będzie wytaczaniem armaty na muchy. W tej sytuacji zupełnie dobrze poradzi sobie wbudowana baza SQLite, która ma ten wielki plus, że jest całkowicie bezobsługowa. Właściwie jedynym przypadkiem kiedy **konieczne** będzie użycie bazy serwerowej będzie przypadek uruchamiania aplikacji w kilku instancjach działających na oddzielnych maszynach (fizycznych lub wirtualnych).

Instalacja aplikacji krok po kroku
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Zalecam, by instalację przeprowadzić na zwykłym (nie administracyjnym) koncie użytkownika. Można do tego celu utworzyć nowe konto, ale zazwyczaj nie ma takiej potrzeby. Aplikacja zainstalowana w sposób opisany w tej instrukcji będzie działała używając uprawnień *zwykłego* użytkownika, a do działania w ogóle nie potrzebuje uprawnień administracyjnych. Do instalacji będą potrzebne uprawnienia administracyjne dostarczane przez program ``sudo``.

Zainstaluj wszystkie niezbędne narzędzia programistyczne oraz wymagane dodatkowe pakiety związane z Pythonem.

.. code-block:: shell-session

    $ sudo apt install build-essential libffi-dev libicu-dev libmagic-dev python3-venv python3-dev wget

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

Innym rodzajem zawartości serwisu są pliki udostępnione do pobrania. Aplikacja umieszcza je we wskazanym miejscu i je również dobrze będzie trzymać tam gdzie i całą resztę. Ścieżka do tego katalogu jest później przekazana w zmiennej środowiskowej.

.. code-block:: shell-session

    $ mkdir -p instance/attachments

Utwórz również katalog na statyczne dane konfiguracji serwisu i skopiuj do niego przykładowy plik konfiguracją serwisu.

.. code-block:: shell-session

    $ mkdir conf
    $ wget -O conf/site.json https://raw.githubusercontent.com/zgoda/bip/master/conf/site.json.example

W ten sposób zainstalowana aplikacja jest gotowa do uruchmonienia pod kontrolą serwera aplikacji WSGI.

Instalacja, konfiguracja i uruchomienie serwera aplikacji WSGI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Najpopularniejszymi serwerami aplikacji WSGI są uWSGI i Gunicorn (ale oczywiście nie jedynymi). Każdy z nich dostarcza różnych możliwości uruchomienia aplikacji:

* uWSGI: jako samodzielny proces lub zintegrowany z serwerem WWW Nginx
* Gunicorn jako samodzielny proces

Od strony praktycznej używając poniżej omówionych sposobów nie ma większych różnic w jaki sposób serwer aplikacji będzie się komunikował z serwerem WWW.

W ramach przykładu pokazane zostanie uruchomienie aplikacji pod kontrolą uWSGI działającego w integracji z serwerem WWW Nginx oraz pod kontrolą Gunicorn z serwerem Nginx działającym jako *reverse proxy*. Przykładowe pliki konfiguracyjne można pobrać ze `źródłowego repozytorium Git projektu <https://github.com/zgoda/bip/tree/master/conf>`_.

Ze względu na prostszą konfigurację osobom nieobeznanym proponuję użycie Gunicorn jako serwera WSGI i Nginx jako serwera WWW.

Każdy z poniższych przykładów ładuje część ustawień ze zmiennych środowiskowych, które procesom aplikacji są dostarczane przez zarządcę, w naszym przypadku ``systemd``. Zmienne te są ładowane z pliku, którego zawartość powinna wyglądać tak jak poniżej (``mojekonto`` należy w nim zamienić na rzeczywistą nazwę konta użytkownika, na którym będzie uruchomiona aplikacja):

.. code-block:: shell

    FLASK_DEBUG="0"
    FLASK_TESTING="0"
    INSTANCE_PATH="/home/mojekonto/bip/instance"
    SITE_JSON="/home/mojekonto/bip/conf/site.json"
    DB_NAME="/home/mojekonto/bip/db.sqlite3"
    DB_DRIVER="sqlite"

Plik ten należy umieścić w miejscu dostępnym dla zarządcy procesów, np w ``/home/mojekonto/bip``.

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

    # logowanie
    logto = /home/mojekonto/bip/uwsgi.log

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
    # załadowanie zmiennych środowiskowych z pliku
    EnvironmentFile="/home/mojekonto/bip/environment"
    # komenda uruchamiająca usługę
    ExecStart=/home/mojekonto/bip/venv/bin/uwsgi --ini /home/mojekonto/bip/bip.ini
    # warunek restartu usługi - zawsze
    Restart=always

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

W pliku tym należy umieścić poniższą zawartość. ``bip.domena.pl`` oraz ``mojekonto`` należy zastąpić rzeczywistymi wartościami, tj. nazwą domenową serwera skonfigurowaną w ustawieniach DNS oraz prawdziwą nazwą konta użytkownika, na którym została zainstalowana aplikacja. Poniższy plik konfiguracyjny Nginxa jest kompletny, tj. nie zawiera wszystko co potrzeba do uruchomienia aplikacji. W szczególnych przypadkach może być konieczne dostrojenie konfiguracji, ale to wykracza poza zakres podręcznika instalacji.

.. code-block:: nginx

    server {
        listen 80;
        listen [::]:80;
        server_name bip.domena.pl;
        access_log /var/log/nginx/bip.access.log;
        error_log /var/log/nginx/bip.error.log;

        location / {
            # włączenie obsługi uWSGI
            include uwsgi_params;
            uwsgi_pass unix:/tmp/bip.sock;
        }

        # reguła dla zasobów statycznych
        location /static {
            root /home/mojekonto/bip;
        }

        # reguła dla plików do pobrania
        location /attachment {
            root /home/mojekonto/instance;
            # pliki mają być pobierane, a nie wyświetlane
            if ($arg_save) {
                add_header Content-Disposition "attachment; filename=$arg_save";
            }
        }

        location /robots.txt {
            root /home/mojekonto/bip/static;
        }

        location /sitemap.xml {
            root /home/mojekonto/bip/static;
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
    # załadowanie zmiennych środowiskowych z pliku
    EnvironmentFile="/home/mojekonto/bip/environment"
    # komenda uruchamiająca usługę
    ExecStart=/home/mojekonto/bip/venv/bin/gunicorn --workers 2 --preload --bind unix:/tmp/bip.sock -m 007 --error-logfile /home/mojekonto/bip/gunicorn.error.log bip.wsgi:application
    # warunek restartu usługi - zawsze
    Restart=always

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

W pliku tym należy umieścić poniższą zawartość. ``bip.domena.pl`` oraz ``mojekonto`` należy zastąpić rzeczywistymi wartościami, tj. nazwą domenową serwera skonfigurowaną w ustawieniach DNS oraz prawdziwą nazwą konta użytkownika, na którym została zainstalowana aplikacja. Poniższy plik konfiguracyjny Nginxa jest kompletny, tj. nie zawiera wszystko co potrzeba do uruchomienia aplikacji. W szczególnych przypadkach może być konieczne dostrojenie konfiguracji, ale to wykracza poza zakres podręcznika instalacji.

.. code-block:: nginx

    server {
        listen 80;
        listen [::]:80;
        server_name bip.domena.pl;
        access_log /var/log/nginx/bip.access.log;
        error_log /var/log/nginx/bip.error.log;

        location / {
            # włączenie proxy
            include proxy_params;
            proxy_pass http://unix:/tmp/bip.sock:;
        }

        # reguła dla zasobów statycznych
        location /static {
            root /home/mojekonto/bip;
        }

        # reguła dla plików do pobrania
        location /attachment {
            root /home/mojekonto/instance;
            # pliki mają być pobierane, a nie wyświetlane
            if ($arg_save) {
                add_header Content-Disposition "attachment; filename=$arg_save";
            }
        }

        location /robots.txt {
            root /home/mojekonto/bip/static;
        }

        location /sitemap.xml {
            root /home/mojekonto/bip/static;
        }

    }

Plik ten należy ostatecznie zlinkować do katalogu z konfiguracjami włączonych aplikacji.

.. code-block:: shell-session

    $ sudo ln -s /etc/nginx/sites-available/bip /etc/nginx/sites-enabled
    $ sudo systemctl reload nginx

Po przeładowaniu konfiguracji Nginxa aplikacja powinna być już dostępna pod adresem domenowym podanym w powyższym przykładzie.
