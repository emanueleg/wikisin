import xml.etree.ElementTree as ET
import re
import argparse
import sqlite3

MW_NS = '{http://www.mediawiki.org/xml/export-0.10/}'
SYN_TPL = "{{-sin-}}"

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', type=str, required=False, default='itwiktionary-latest-pages-meta-current.xml')
parser.add_argument('-l', '--link', required=False, action='store_true')
parser.add_argument('-s', '--sql', required=False, action='store_true')
parser.add_argument('-d', '--db', type=str, required=False, default='wiki.sqlite3')
parser.add_argument('-t', '--table', type=str, required=False, default='itwiktionary')
args = parser.parse_args()

xml_wikidump_file = args.filename

if args.sql:
    con = sqlite3.connect(args.db)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS " + args.table +  ";")
    cur.execute('CREATE TABLE "' + args.table +  '" ("lemma" TEXT NOT NULL, "link" TEXT, "sinonimi" TEXT )')


tree = ET.parse(xml_wikidump_file)
root = tree.getroot()

for c in root.findall(MW_NS+'page'):
    wiki_title = c.find(MW_NS+'title')
    wiki_ns = c.find(MW_NS+'ns')
    
    # salta pagine senza titolo
    if wiki_title is None:
        continue

    # salta pagine non in NameSpace 0 (discussioni, utenti, template, etc)
    if wiki_ns.text != "0":
        continue
    
    lemma = wiki_title.text.strip()
        
    # salta locuzioni, parole composte o espressioni idiomatiche
    if lemma.find(" ") > -1:
        continue
    if lemma.find("-") > -1:
        continue	
    if lemma.find("'") > -1:
        continue

    wiki_revision = c.find(MW_NS+'revision')

    # salta pagine senza revisioni
    if wiki_revision is None:
        continue

    # salta pagine senza testo
    wiki_text = wiki_revision.find(MW_NS+'text')
    if wiki_text is None:
        continue

    p = re.compile(r'<!--(.|\s|\n)*?-->')
    wiki_text.text = re.sub(p, '', wiki_text.text)
    start_it = wiki_text.text.find("{{-it-}}")

    # salta pagine senza definizione in italiano
    if wiki_text.text.find("{{-it-}}") < 0:
        continue

    wiki_text = wiki_text.text[start_it:]                
    start_sin = wiki_text.find(SYN_TPL)

    # salta pagine senza sinonimi
    if start_sin < 0:
        continue

    # salta pagine con sinonimi in altre lingue
    other_lang_start1 = wiki_text[10:].find("== {{-")
    if other_lang_start1 > 0 and start_sin > other_lang_start1:
        continue

    other_lang_start2 = wiki_text[10:].find("=={{-")
    if other_lang_start2 > 0 and start_sin > other_lang_start2:
        continue
    
    # estrate tutta la parte dei sinonimi
    end_sin = wiki_text[start_sin + len(SYN_TPL) + 3:].find("{{")
    sin1 = wiki_text[start_sin+len(SYN_TPL):start_sin+len(SYN_TPL)+end_sin+3].strip()

    # salta pagine con sinonimi vuota
    if len(sin1) < 1:
        continue

    # salta pagine con codice html o template nei sinonimi
    if sin1.find("<") > -1 or sin1.find(">") > -1 or sin1.find("!") > -1 or sin1.find("{") > -1:
        continue

    # toglie le glosse tra parentesi per la disambiguazione dei termini
    sin1 = sin1.replace("''(", "(")
    sin1 = sin1.replace("'(", "(")
    sin1 = sin1.replace(")''", ")")
    sin1 = sin1.replace(")'", ")")
    sin1 = re.sub(p, '', sin1)
    p = re.compile(r'\([^)]*\)')
    sin1 = re.sub(p, '', sin1)

    # elimina punto e virgola, punti, asterischi, e link con quadre
    sin1 = sin1.replace("\n", ",")
    sin1 = sin1.replace("  ", " ")
    sin1 = sin1.replace(";", "")
    sin1 = sin1.replace(".", "")
    sin1 = sin1.replace("*", "")
    sin1 = sin1.replace("[", "")
    sin1 = sin1.replace("]", "")
    sin1 = sin1.replace(",,", ",")
    sin1 = sin1.strip(',')

    # salta se non è rimasto testo
    if len(sin1) < 1:
        continue

    # mette lowercase
    #sin1 = sin1.lower()
    
    # esplode list
    #sin_list = [x.strip() for x in sin1.split(',')]
    sin_list = map(str.strip, sin1.split(','))
    
    wiki_link = "https://it.wiktionary.org/wiki/"+wiki_title.text
    sinonimi = '|'.join(sin_list)

    # inserisce nel db sqlite3 oppure stampa lemma, sinonimi e link alla pagina del wikizionario
    if args.sql:
        cur.execute("INSERT INTO " + args.table + " (`lemma`, `link`, `sinonimi`) VALUES (?, ?, ?)", (lemma, wiki_link, sinonimi))
    else:
        if args.link:
            print(lemma + ";" + sinonimi + ";" + wiki_link)
        else:
            print(lemma + ";" + sinonimi)


if args.sql:
    con.commit()
    cur.execute("VACUUM `main`"); 
    con.commit()
    cur.close()
    con.close()
