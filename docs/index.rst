Dokumentacja aplikacji BIP
==========================

Aplikacja BIP implementuje Biuletyn Informacji Publicznej w języku Python przy użyciu ramówki aplikacyjnej Flask. Jest to aplikacja samodzielna, przeznaczona do uruchamiania w kontenerze lub do pełnej instalacji w systemie Linux. Do działania wymaga Pythona w wersji 3.7 lub nowszej oraz bazy danych. W szczególności całkiem dobrze działa z wbudowaną bazą SQLite i serwerowa baza danych jak PostgreSQL czy MySQL w najprostszych przypadkach nie jest wymagana.

Aplikacja jest przeznaczona dla serwisów małych i bardzo małych, zawierających do 1000 stron i obsługujących do 100 odsłon na minutę. Oczywiście, możliwe jest poziome przeskalowanie aplikacji tak, by mogła obsłużyć zarówno więcej dokumentów, jak i większy ruch, ale nie taki przyświecał cel podczas jej pisania.

Licencja
--------

Aplikacja jest rozwijana w modelu Open Source i jest dostępna nieodpłatnie na warunkach licencji GNU General Public License, wersja 3. Oznacza to, że nie ma żadnych ograniczeń w użytkowaniu tego oprogramowania (w tym za opłatą), ale w przypadku jego dystrybucji wymagane jest udostępnienie nabywcy pełnej wersji źródłowej programu ze wszystkimi zmianami, niezależnie od tego czy jest on udostępniany za darmo czy za opłatą. W szczególności oznacza to, że:

* można program zainstalować i użytkować bez opłat
* można w kodzie programu wprowadzać zmiany na własny użytek bez konieczności ich udostępniania
* można pobierać opłaty za zainstalowanie i utrzymanie serwisu
* będąc właścicielem usługi hostingu można oferować preinstalację programu dla użytkowników, zarówno bezpłatnie jak i za opłatą

Licencja dotyczy wyłącznie kodu aplikacji i nie obejmuje treści wprowadzonych przez jej użytkowników.

Dokumentacja użytkownika
------------------------

.. toctree::
    :maxdepth: 2

    userguide
    bipadmin

Instalacja i administracja
--------------------------

.. toctree::
    :maxdepth: 2

    install
    adminguide

Dokumentacja programistyczna
----------------------------

.. toctree::
    :maxdepth: 2

    devguide
    apidocs


Dokumenty ogólne
----------------

.. toctree::
    :maxdepth: 1

    roadmap
    coc
    contributing
    license
    thirdparty



Indeksy i tabele
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
