Przewodnik programisty
======================

Kod tego projektu jest przeznaczony dla środowiska uruchmieniowego języka Python w wersji 3.7 lub nowszej. Automatyczne testy są uruchamiane na każdym powszechnie dostępnym środowisku które spełnia to wymaganie (w chwili pisania tego dokumentu są to 3.7 i 3.8). Z powodu ograniczonej dostępności środowiska w wersji 3.8, zalecam do programowania lokalnie używać wersji 3.7, która jest dostępna zarówno w Debianie 10 (Buster) jak i Ubuntu 18.04. Dla innych wersji Ubuntu jest możliwość zainstalowania pozasystemowych wersji Pythona używając respozytorium `PPA Deadsnakes <https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa>`_. Niestety w Debianie wymaga to samodzielnej kompilacji odpowiedniej wersji z pakietu źródłowego.

Wszystko co trzeba na początek
------------------------------

Zacznij od zrobienia forka na Githubie i sklonuj go do lokalnej kopii.

.. code-block:: console

    $ git clone git@github.com:myname/bip.git
    $ cd bip

Od tej pory wszystkie polecenia są wykonywane w katalogu lokalnej kopii.

Połącz kod w swojej kopii z repozytorium macierzystym.

.. code-block:: console

    $ git remote add upstream https://github.com/zgoda/bip.git
    $ git fetch upstream

Utwórz środowisko wirtualne i zainstaluj podstawowe pakiety.

.. code-block:: console

    $ /usr/bin/python3.7 -m venv venv
    $ source venv/bin/activate
    $ pip install -U pip wheel

Od tej pory wszystkie polecenia są wykonywane z aktywowanym środowiskiem wirtualnym.

Zainstaluj zależności. Pakiet ma zdefiniowany tryb ``dev`` który instaluje wiele przydatnych narzędzi programistycznych, zorientowanych w szczególności na jakość kodu. Proponuję uruchamiać ``flake8 .`` przed każdym commitem, a najlepiej ustawić sobie *linting* w edytorze.

.. code-block:: console

    $ pip install -U -e .[dev]

W tym momencie kod powinien już być uruchamialny, ale wcześniej dobrze będzie utworzyć sobie plik z lokalnymi zmiennymi środowiskowymi ``.env`` jak poniżej.

.. code-block:: shell

    export FLASK_ENV="development"
    export SITE_JSON="${PWD}/conf/site.json"
    export DB_NAME="${PWD}/db.sqlite3"
    export SECRET_KEY="losowe znaki"

Zastąp ``losowe znaki`` czymś co jest naprawdę losowe, poniżej przykład.

.. code-block:: console

    $ python -c 'import os,hashlib; print(hashlib.sha256(os.urandom(64)).hexdigest())'

W tym momencie brakuje jeszcze tylko danych instytucji.

.. code-block:: console

    $ cp conf/site.json.example conf/site.json

Dane w przykładowym pliku powinny być wystarczające na początek.

**Gratulacje**, twoja kopia kodu źródłowego pakietu ``biuletyn-bip`` jest gotowa do pracy. Baw się dobrze!
