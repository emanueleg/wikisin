# Sinonimi dal Wikizionario
Semplice tool in Python3 che estrae dal [Wikizionario](https://it.wiktionary.com) i sinonomi dei lemmi italiani (NB funziona offline usando il dump xml del sito).

## Funzionamento
1. scaricare il dump del database di it_wiktionary da https://dumps.wikimedia.org/backup-index.html
2. scompattare l'archivio nella stessa cartella del programma
3. avviare lo script

In un terminale Linux la sequenza di comandi è:

    wget https://dumps.wikimedia.org/itwiktionary/latest/itwiktionary-latest-pages-meta-current.xml.bz2
    bzip2 -f -d itwiktionary-latest-pages-meta-current.xml.bz2
    python3 wiktionaryit2sin.py

## Opzioni avanzate

E possibile utilizzare le opzioni a linea di comando:
* `-f NOMEFILEDUMP` per indicare un diverso file xml (default `itwiktionary-latest-pages-meta-current.xml`)
* `-l` per mostrare in output il link alla pagina del lemma nel wikizionario
* `-s` per inserire i risultati su db sqlite3 invece che stamparli a schermo
* `-d` per indicare un diverso nome file per il db sqlite3 (default `wiki.sqlite3`)
* `-t` per indicare una diversa tabella nel db (default `itwiktionary`)
