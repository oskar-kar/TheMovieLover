# TheMovieLover

## Aplikacja internetowa wykorzystująca system rekomendacyjny do proponowania użytkownikowi filmów do obejrzenia.

Na aplikację składają się:
  - Baza danych przechowująca informacje na temat filmów, osób biorących udział w ich produkcji, użytkownikach aplikacji oraz wystawionych przez nich ocenach.
    - Wykorzystuje zbiór danych dostępny w Internecie, który został odpowiednio przeredagowany i obcięty na potrzeby aplikacji.
  - System rekomendacyjny opierający się na filtrowaniu kolaboratywnym oraz filtrowaniu w oparciu o zawartość.
  - REST API (Serwer aplikacji, Back-end) służące jako pośrednik między Front-endem, a systemem rekomendacyjnym oraz bazą danych.
  - Strona internetowa (Front-end) zajmująca się interakcją z użytkownikiem oraz prezentowaniem mu treści.

Do stworzenia aplikacji internetowej wykorzystano poniższe technologie:
  - Microsoft SQL Server - do stworzenia bazy danych.
  - Język Python, framework Django oraz biblioteki m. in. scikit-learn, numpy, pandas - do stworzenia REST API oraz systemu rekomendacyjnego.
  - Język HTML, CSS, JavaScript oraz biblioteki JQuery - do stworzenia strony internetowej.
  - Komunikacja między Front-endem a Back-endem opiera się na przesyłaniu danych w formacie JSON.

Aplikacja pozwala:
  - Zarejestrować konto użytkownika.
  - Zalogować się na konto (oraz wylogować).
  - Wyszukać film podając pełny jego tytuł lub część w języku polskim lub angielskim.
  - Przejrzeć pełną listę filmów znajdujących się w bazie.
  - Filtrować listę filmów podając odpowiedni gatunek, rok produkcji lub średnią ocen.
  - Wystawić ocenę w skali 1-10 wybranemu filmowi.
  - Przejrzeć listę filmów, które użytkownik ocenił.
  - Poprosić o rekomendację 8 filmów przez system rekomendacyjny.

Mechanizmy bezpieczeństwa w aplikacji:
  - Dostęp do bazy danych (odczytu,, zapisu, edycji oraz usuwania) posiadają dwa konta: Konto administratora systemu Windows, na którym znajduje się baza danych oraz konto użytkownika wykorzystywane przez REST API.
  - Wykorzystanie funkcji skrótu SHA256 w celu zapewnienia prywatności haseł użytkowników. W bazie danych przechowywane są wyniki funkcji skrótu przeprowadzonej na hasłach, a nie same hasła.
  - Wykorzystanie tokenów JWT (Access oraz Refresh token) w celu autoryzacji operacji wykonywanych przez użytkownika.
  - Ochrona przed SQLInjection poprzez użycie frameworka Django oraz wyrażen regularnych w polach tekstowych Front-endu.

## Web application that uses recommendation system to suggest users movies to watch.

Application consists of:
  - Database that stores information about movies, people involved in their production, application users and their movie ratings.
    - Uses available online data set, that was appropriately edited and cut down in size according to application requirements.
  - Reccomendation system based on collaborative filtering and content based filtering.
  - REST API (Back-end, Server) which main purpose is to be a go-between Front-end, recommendation system and database.
  - Website (Front-end) which interacts with user and presents them information visually.

Following technologies were use to create web application:
  - Microsoft SQL Server - for the creation of database.
  - Python, Django framework and libraries such as scikit-learn, numpy, pandas - for the creation of REST API and recommendation system.
  - HTML, CSS, JavaScript and JQuery libraries - for the creation of website.
  - Back-end - Front-end communication based on passing information in JSON format.

Application allows user to:
  - Register new account.
  - Log into account (as well as logout).
  - Search movie by entering full (or part of a) movie title in Polish or English language.
  - Browse through full movie list from database.
  - Filter movie list by entering genre, year of production or average rating.
  - Rate a movie from 1 to 10.
  - Browse through the list of movies rated by user.
  - Ask for a recommendation of 8 movies by recommendation system.

Security measures included in the application:
  - Database access (read, write, update and delete) only for two accounts: Windows admin account on which the database is stored and user account created for REST API.
  - SHA256 hash function used to ensure privacy of accounts's passwords. No password is stored in database, only hashes.
  - JWT tokens (Access and Refresh tokens) used for authorization of user's operations.
  - Protection from SQLInjection thanks to Django framework and usage of regular expressions in website's text fields.
