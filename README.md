# La esperanto-kurso laŭ la Zagreba metodo

[![Aliĝu la babililon https://gitter.im/Esperanto/kurso-zagreba-metodo](https://badges.gitter.im/Esperanto/kurso-zagreba-metodo.svg)](https://gitter.im/Esperanto/kurso-zagreba-metodo?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Tiu deponejo enhavas la Esperanto-kurson laŭ la [Zagreba metodo](https://eo.wikipedia.org/wiki/Zagreba_metodo) en strukturita datumaranĝo. Do, la kompleta enhavo estas konservita per [YAML](https://en.wikipedia.org/wiki/YAML)-dosieroj, facile legeblaj per diversaj komputilaj programlingvoj – kaj ankaŭ por homoj.

Tiel oni facile kaj rapide povos krei eldonaĵojn de la kurso en HTML, EPUB, PDF aŭ ia ajn formo.

## Demonstraĵo

- https://esperanto12.net/

## Kiel krei eligon
### HTML

    python generate.py --lingvo en --eligformo html

Kreas HTML-dosierujon en `html_generiloj/output/en`.

### PDF kaj EPUB

Vi bezonas [Pandoc](https://pandoc.org), minimume versionon 2.

    python generate.py --lingvo en --eligformo md 

Eligas la tutan kurson en Markdown al `STDOUT`, tial per:

    python generate.py --lingvo en --eligformo md | pandoc --latex-engine=xelatex -o en.pdf
    python generate.py --lingvo en --eligformo md | pandoc -o en.epub

oni povas krei kaj PDF kaj EPUB dosieron.

#### Limigu enhavon

    python generate.py --lingvo en --eligformo md --printendaj-partoj ekzerco2 solvo2
      --printendaj-lecionoj 1 2 3
    
Eligu nur ekzercon 2 kaj sian solvon, kaj nur de lecionoj 1, 2, 3. Legu plu per `python generate.py  --help`.

## Eksperimenta PWA-subteno

- https://esperanto.github.io/kurso-zagreba-metodo/ - En Android, aperas sugesto instali la aplikaĵon, en aliaj platformoj eblas instali ĝin per la opcio en la menuo en Chrome. Sendepende de tia instalado, la paĝaro ebligas uzi la paĝojn eksterrete post unuafoja vizitado.

## Permesiloj

Tiun ĉi kurson oni povas libere uzi, kondiĉe ke oni nomas la [aŭtorojn](AUTHORS.md).

### Esperantaj tekstoj

![permesilo](bildoj/by-nd.png) 

La Esperantaj leciontekstoj en la kurso `enhavo/netradukenda/tekstoj` devas resti neŝanĝitaj. Tial aplikas la [CC BY-ND 4.0](enhavo/netradukenda/tekstoj/PERMESILO.md).

### Aliaj dosieroj

![permesilo](bildoj/by.png)

Ĉion alian oni povas ŝanĝi. Tial aplikas la [CC BY 4.0](PERMESILO.md).

## Pliaj tradukoj?

Ĉu vi volas traduki la kurson al nova lingvo? Belege! Bonvole [plulegu tie](enhavo/tradukenda).
