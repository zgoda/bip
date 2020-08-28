Dokumentacja administratora
===========================

Jako "administratora systemu" rozumiem osobę odpowiedzialną za instalację, uruchomienie i utrzymanie serwisu Biuletynu w stanie sprawnym i działającym. Zakładam że instalacja i uruchmienie aplikacji zostaną wykonane w systemie Linux. Dla mniej wprawnych użytkowników proponuję wykonanie próbnej instalacji na maszynie wirtualnej Debiana 10 uruchomionej pod Virtualbox albo VMWare. Ogólnie instalacja **nie wymaga** niczego poza instalowaniem pakietów systemowych, instalowaniem pakietów bibliotek Pythona w środowisku wirtualnym oraz edytowania plików tekstowych z konfiguracją serwisów takich jak serwer aplikacji czy WWW.

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
