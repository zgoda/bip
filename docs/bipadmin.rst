Administracja serwisem BIP
==========================

Administracja serwisem BIP odbywa się na dwóch poziomach, na poziomie redaktora i na poziomie administratora. Jedyna różnica polega na tym, że administrator posiada uprawnienia do zarządzania kontami użytkowników (redaktorów i innych administratorów), natomiast redaktorzy mogą jedynie zarządzać swoimi własnymi danymi. W pozostałym zakresie zasady zarządzania danymi serwisu się nie różnią.

Ten dokument opisuje tylko zasady zarządzania kontami użytkowników. Pozostałe kwestie związane z administracją zawartością BIP są omówione w :doc:`podręczniku użytkownika <userguide>`.

Zakładanie konta pierwszego administratora
------------------------------------------

W aplikacjach z zarządzeniem kontami użytkowników występuje problem zbliżony do paradoksu *jajka i kury* - do zakładania kont użytkowników potrzebne jest konto użytkownika administracyjnego, które jakoś musi zostać założone, pomimo braku jakiegokolwiek konta w systemie. W aplikacji BIP jest to rozwiązane tak, że konto pierwszego administratora jest zakładane przy użyciu wiersza poleceń aplikacji.

Aby założyć konto użytkownika należy zalogować się do powłoki (*shell*) serwera na którym jest zainstalowana aplikacja, a następnie po aktywowaniu wirtualnego środowiska uruchomieniowego Pythona uruchomić program bip:

.. code-block:: shell-session

    $ cd bip
    $ source venv/bin/activate
    $ bip user --help
    Usage: bip user [OPTIONS] COMMAND [ARGS]...

      Zarządzanie kontami użytkowników

    Options:
      --help  Show this message and exit.

    Commands:
      change  Zmiana danych konta użytkownika
      create  Zakładanie nowego konta użytkownika
      info    Informacje o zalogowanym użytkowniku
      list    Wyświetl listę użytkowników
      login   Zaloguj użytkownika i zachowaj dane logowania

Z podanych poleceń interesujące będzie polecenie ``create``, które tworzy nowe konto użytkownika.

.. code-block:: shell-session

    $ bip user create --help
    Usage: bip user create [OPTIONS]

      Zakładanie nowego konta użytkownika

    Options:
      -n, --name TEXT        Nazwa konta użytkownika  [required]
      -p, --password TEXT    Hasło użytkownika  [required]
      -e, --email TEXT       Email użytkownika
      --active / --inactive  Czy konto ma być od razu aktywne (domyślnie: NIE)
      --admin / --regular    Czy konto ma mieć uprawnienia administracyjne
                             (domyślnie: NIE)

      -u, --user TEXT        Nazwa użytkownika wykonującego czynność
      --help                 Show this message and exit.

Z powyższego opisu polecenia wynika, że do utworzenia konta konieczne jest podanie nazwy/loginu użytkownika (parametr ``--name``), hasła (parametr ``--password``) oraz ustawienie by konto było od razu aktywne (parametr ``--active``) oraz by było kontem administracyjnym (parametr ``--admin``). Dwa ostatnie parametry są flagami i nie wymagają podawania wartości, tak że ostatecznie linia poleceń wygląda następująco:

.. code-block:: shell-session

    $ bip user create --name nazwakonta --password haslo --active --admin

Parametry ``name`` i ``password`` mają również formę skróconą:

.. code-block:: shell-session

    $ bip user create -n nazwakonta -p haslo --active --admin

Gdyby konto miało być zakładane przez administratora systemu, to hasło po pierwszym logowaniu należy zmienić korzystając z funkcji zmiany hasła na stronie profilu użytkownika.
