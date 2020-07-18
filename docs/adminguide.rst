Dokumentacja administratora
===========================

Jako "administratora systemu" rozumiemy osobę odpowiedzialną za instalację, uruchomienie i utrzymanie serwisu Biuletynu w stanie sprawnym i działającym. Zakładamy że instalacja i uruchmienie aplikacji zostaną wykonane w systemie Linux. Dla mniej wprawnych użytkowników proponujemy wykonanie próbnej instalacji na maszynie wirtualnej Debiana 10 uruchomionej pod Virtualbox albo VMWare. Ogólnie instalacja **nie wymaga** niczego poza instalowaniem pakietów systemowych, instalowaniem pakietów bibliotek Pythona w środowisku wirtualnym oraz edytowania plików tekstowych z konfiguracją serwisów takich jak serwer aplikacji czy WWW.

Usługi dodatkowe
----------------

Integracja z usługą zdalnego logowania Sentry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Aplikacja BIP może być opcjonalnie zintegrowana z usługą zdalnego logowania błędów Sentry. Do zintegrowania aplikacji z Sentry konieczne jest dostarczenie poprzez zmienną środowiskową parametrów połączenia do serwera Sentry. Poniższy przykład pokazuje jak to zrobić przy użyciu pliku ze zmiennymi środowiskowymi używanego przez ``systemd`` w definicji usługi aplikacji.

.. code-block:: shell

    SENTRY_DSN=https://klucz@konto.ingest.sentry.io/projekt

Zawartość tej zmiennej można znaleźć w ustawieniach projektu na stronie administracji w Sentry.

.. image:: /_static/sentry_config.png
