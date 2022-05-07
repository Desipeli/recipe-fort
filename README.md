# Recipe Fort

*Recipe Fort* on selaimella toimiva sovellus, missä kuka tahansa voi jakaa reseptejä sekä arvostella/kommentoida niitä. Sovellus on luotu Tietokantasovellus-kurssilla.

### Tämän hetken toiminnallisuudet ja ominaisuudet
- Käyttäjä pystyy luomaan käyttäjätunnuksen ja kirjautumaan sisään/ulos
- Voidaan hakea reseptejä useilla eri määrittelyillä
  - Reseptin nimi
  - Käyttäjän nimi
  - Valmistusaika
  - Vaikeustaso
  - Kategoria
  - Raaka-aineet
- Hakutuloksen voi järjestää
  - Aakkosjärjestykseen
  - Aikajärjestykseen
- Käyttäjä voi luoda uusia reseptejä, sekä muokata tai poistaa omia reseptejä
- Käyttäjä voi kommentoida reseptejä
- Käyttäjä voi poistaa itse kirjoittamansa kommentit
- Käyttäjä voi poistaa omasta reseptistään kenen tahansa kommentin
- Käyttäjä voi tykätä/vihata toisen käyttäjän tekemää reseptiä
- Käyttäjä voi vaihtaa salasanansa profiili-osiosta

- Sovelluksessa ei pitäisi olla mahdollisuutta SQL-injektioon, eikä csrf- tai XSS-haavoittuvuutta
- Sovelluksen ulkoasu on melko alkeellinen, mutta toimii myös siedettävästi puhelimella.

### Kehitysideoita

Seuraavaksi luetellut ominaisuudet oli tarkoitus toteuttaa, mutta aika loppui kesken.

- Admin-käyttäjä, joka voi poistaa kenen tahansa reseptin/kommentin, sekä laittaa käyttäjän jäähylle.
- Siistimpi ulkoasu
- Kommenttien arvostelu ja niihin vastaaminen
- Reseptien järjestäminen tykkäysten perusteella
- Käyttäjän poistaminen
- Jotain fiksua etusivulle, esim. viikon tykätyin resepti
- Suosikit-listaus omaan profiiliin, tai toisen käyttäjän seuraaminen

## Sovelluksen käyttö

Sovellusta voi käyttää herokussa: https://recipe-fort.herokuapp.com/

#### Käyttäjätunnus

- Alkuun kannattaa luoda uusi käyttäjätunnus ["register here"](https://recipe-fort.herokuapp.com/create_account) linkin kautta. Reseptien selaaminen on ainoa asia mitä voi tehdä kirjautumatta sisään.

#### Reseptin luominen

- Siirtymällä navigointipalkista "New recipe"-sivulle, käyttäjä voi luoda uuden reseptin. Kentissä on tietyt vaatimukset, ja virheviestit tulostetaan niiden perään.
  - Yhdellä käyttäjällä ei voi olla samannimisä reseptejä
  - Reseptin ja raaka-aineen nimen on oltava 1-60 kirjainta
  - Ajat ilmoitetaan kokonaislukuina minuutteina
  - Vaikeusaste on välillä 0-3
  - Määrän on oltava numero
  - Yksikkö ja ohjeet eivät ole välttämättömiä

#### Salasanan vaihto

- "View profile"-sivulla käyttäjä voi vaihtaa salasanansa syöttämällä ensin vanhan salasanan ja sen jälkeen kaksi kertaa uuden salasanan. Virheviesti tulostetaan kenttien yläpuolelle

#### Reseptihaku

- "Search recipes"-linkki vie käyttäjän reseptihakuun, jossa näytetään oletuksena kaikki kannan reseptit, uusin ensimmäisenä
  - Recipe name ja Username hakevat kaikki sellaiset reseptit, joissa esiintyy haettu sana
  - Maksimi ajat ja vaikeus rajaavat haun ulkopuolelle reseptit, joidenka kesto ylittää vaatimuksen
  - Kategoria näyttää vain siihen kategoriaan kuuluvat reseptit (all näyttää kaikkiin kategorioihin)
  - Voidaan valita missä järjestyksessä reseptit näytetään (aakkos tai aika)
  - add ingredient-napin avulla voidaan lisätä ainesosakenttiä, joiden avulla näytetään vain sellaiset reseptit, joihin ilmoitetut ainesosat riittävät
  - remove ingredient poistaa viimeisen ainesosan

- Reseptiä voi tarkastella klikkaamalla sen nimeä
- Klikkaamalla käyttäjänimeä näytetään kaikki sen käyttäjän reseptit

#### Reseptin muokkaaminen/poistaminen

- Reseptiä pääsee muokkaamaan siirtymällä ensin tarkastelemaan omaa reseptiä, ja valitsemlla Edit/delete recipe reseptin nimen alta
- Reseptiä muokataan samaan tapaan kuin se luotiin
- Alhaalla löytyy vaihtoehto confirm modification, joka tekee muutokset pysyviksi, mikäli ongelmia ei havaita
- Discard modifications peruuttaa muutokset, eikä reseptille tehdä mitään
- Delete recipe poistaa reseptin tietokannasta

#### Reseptin kommentoiminen ja tykkääminen

- Alkuun tulee siirtyä reseptin tarkasteluun esimerkiksi haun kautta
- Ohjeikkunan alapuolella näkyy, kuinka moni käyttäjä on tykännyt/vihannut reseptiä
- Jos tarkastelija on kirjautunut sisään eikä ole respetin luoja, voi hän tykätä/vihata reseptiä. Mielipidettä voi muuttaa myöhemmin
- Jos tarkastelija on kirjautunut sisään voi hän kommentoida reseptiä. Sallin reseptin kommentoimisen myös reseptin luojalle, jos hän haluaa vastata kommentteihin tai ilmoittaa muokanneensa reseptiä
- Oman kommentin tai muiden kommentteja omasta reseptistä voi poistaa painamalla "delete comment"-nappia kommentin yläpuolella
- Kommentit listataan uutuusjärjestyksessä
