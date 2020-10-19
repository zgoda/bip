Dokumentacja administratora
===========================

Jako "administratora systemu" rozumiem osobę odpowiedzialną za instalację, uruchomienie i utrzymanie serwisu Biuletynu w stanie sprawnym i działającym. Zakładam że instalacja i uruchmienie aplikacji zostaną wykonane w systemie Linux. Dla mniej wprawnych użytkowników proponuję wykonanie próbnej instalacji na maszynie wirtualnej Debiana 10 uruchomionej pod Virtualbox albo VMWare. Ogólnie instalacja **nie wymaga** niczego poza instalowaniem pakietów systemowych, instalowaniem pakietów bibliotek Pythona w środowisku wirtualnym oraz edytowania plików tekstowych z konfiguracją serwisów takich jak serwer aplikacji czy WWW.

Instalacja aplikacji została szczegółowo opisana w :doc:`podręczniku instalacji <install>`.

Aktualizacja aplikacji
----------------------

Aby zaktualizować zainstalowaną aplikację należy aktywować środowisko wirtualne Pythona w którym jest ona zainstalowana oraz uruchomić aktualizację z PyPI. Po zakończeniu instalacji należy ponownie uruchomić usługę.

.. code-block:: shell-session

    $ pip install -U biuletyn-bip
    $ sudo systemctl restart bip

Gdyby doszło do jakiejś katastrofy i program się nie uruchomił poprawnie to w łatwy sposób można kod przywrócić do wcześniejszej wersji instalując aktualizację ze wskazaniem konkretnego numeru wersji.

.. code-block:: shell-session

    $ pip install -U "biuletyn-bip==1.0.1"

Proszę zwrócić uwagę na konieczność użycia cudzysłowów w linii tego polecenia.

Śledzenie błędów wykonania
--------------------------

Aby śledzić nieobsłużone błędy wykonania aplikacji w najprostszym przypadku można polegać na logach serwera aplikacji (uWSGI lub Gunicorn) - przykładowa konfiguracja logowania błędów jest umieszczona w podręczniku instalacji. Lepszym rozwiązaniem jest skorzystanie z usługi agregacji błędów jaką daje np opisane poniżej Sentry. W przypadku `zgłaszania błędów <https://github.com/zgoda/bip/issues>`_ wskazane jest dołączanie fragmentów logów, ponieważ w inny sposób trudno będzie mi prześledzić co się tak naprawdę wydarzyło.

Logi błędów odkładane są do jednego pliku, dlatego wskazanym jest skonfigurowanie zewnętrznego narzędzia do rotacji logów, np ``logrotate``.

Usługi dodatkowe
----------------

Integracja z usługą zdalnego logowania Sentry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Aplikacja BIP może być opcjonalnie zintegrowana z usługą zdalnego logowania błędów `Sentry <https://sentry.io/welcome/>`_. Do zintegrowania aplikacji z Sentry konieczne jest dostarczenie poprzez zmienną środowiskową parametrów połączenia do serwera Sentry. Poniższy przykład pokazuje jak to zrobić przy użyciu pliku ze zmiennymi środowiskowymi używanego przez ``systemd`` w definicji usługi aplikacji (plik ten jest wskazywany przez ``EnvironmentFile`` w pliku konfiguracji usługi dla ``systemd``). W pliku tym należy umieścić poniższą linię, zastępując ``klucz``, ``konto`` i ``projekt`` odpowiednimi wartościami z panelu administracji projektu w Sentry.

.. code-block:: shell

    SENTRY_DSN=https://klucz@konto.ingest.sentry.io/projekt

Zawartość tej zmiennej można znaleźć w ustawieniach projektu na stronie administracji w Sentry.

.. image:: /_static/sentry_config.png

Usługa Sentry przesyła na bieżąco informacje o napotkanych nieprawidłowościach w działaniu aplikacji, które nie zostały obsłużone w jej kodzie.

Integracja działa zarówno z darmową, jak i płatną wersją usługi Sentry.

Jeżeli aplikacja jest uruchomiona za pośrednictwem uWSGI, wtedy by bezproblemowo korzystać z Sentry należy również włączyć w ustawieniach serwera uWSGI obsługę wielowątkowości. W pliku, który podczas instalacji sugerowałem zapisać jako ``bip.ini`` należy dodać poniższą linię.

.. code-block:: ini

    enable-threads = true

W przeciwnym wypadku aplikacja będzie się zatrzymywać podczas wysyłania każdego raportu do serwera Sentry.

Po tej zmianie należy ponownie uruchomić usługę.
