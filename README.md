Welche Paper benutzt: 

Schema Linking Ansätze: 
   Cross Encoder
    -> die Idee ein Modell hat alle Tabellen embedded
    -> Danach werden alle Wörter der Frage gesplitted und einzeln embeddiert zu den Tabellen 
    -> danach wird geschaut wie ähnlich ein Wort der Frage zu den Tabellen Namen sind 
    -> liegt die Ähnlichkeit > Treshhold -> nimmt man an, dass es die Tabelle ist 
    -> diese Tabellen werden dann dem LLM in den Prompt gegeben

    Auffälligkeiten: 
     bei Wort zu Wort kammen bei german Spider gute werte 
     bei Wort und Beschreibung -> nicht so oft erkannt , bei dem Datensatz Stat Bot Swiss Datensatz

    Fragen 
      -> was ist wenn Tabellenname schlecht ist und dann ähnlichkeit gering -> muss man dann die Bedeutung embedden oder 
       extra Spalte mit guten Namen zu jeder Tabelle bauen -> muss man noch untersuchen wie am besten 


 Performance beu Cross Encdoer Ansatz 
 Aufgabe : Prüfen ob in den Ausgegeben relevanten Tabellen vom Cross Encoder Ansatz:  die Tabelle / Tabellen in der Query vorhanden waren 
   bei Treshhold = 0.9 
 hier wurde geschickt ob diese vorhanden ist: also können auch nicht benötigte Tabellen sein   
 relevante Tabelle vom Cross Encoder Model ist in der Query: 582 
 keine Tabelle vom Cross Encoder Model ist in der Query: 148
 es wurde keine Tabelle zur Verfügng gestellet vom Cross Encoder Model : 304 

 => Performance 79 % Tabellen richtig erkannt/ in der Auswahl , wenn man die leeren wegläasst 
 
 => Performance 56 % Tabelle richtig erkannt / in der Auswahl, wenn man die leeren berücksichtigt


 wenn alle Tabellen in der liste der relevanten Queries in der Query vorkommen müssen bei treshhold 0.9: 

 => Performance 57 % bei den dass man die leeren liste weglasst 

 => Performance 40 % wenn man die leeren mitberücksichtig 


 => es werden nicht alle Tabellen erkannt die benötigt werden 
  
  -> eine Ursache kann sein, dass diese nicht explizieht im Satz steht jedoch gebraucht wird für das joinen 

  => um zu viele zu vermeiden : es davor ein anderes LLm geben mit Frage + relevanten Tabellen -> es nochmal fragen welche Relevant sind behalten 

  => um vielleicht fehlende zu bekommen -> ein anderes Model Fragen welche Tabellen notwendig sind -> soll sagen brauche dies und diese Tabellen 
  
  -> davon die ähnlichsten ausgeben lassen 

  Wenn man die leeren berücksichtigt mit dem Zusatz immer alle Beziehenden Tabellen hinzufügt 
  von den aus Frage erkannten bei treshhold 0.9: 

  hit min one table percentage  56.29 %
  miss table percentage 14.31 %
  no table percentage 29.4 %
  precision 19.44 %
  recall 29.69 %



  Wenn man die Tabellennamen und Wörter der Frage lemmatized und Füll wörter entfernt bei Treshhold 0.9

  wenn nur einige Tabellen erhalten sind 

  => Performance 86 % wenn man leere weglässt 

  => Performance 71 % wenn man leere berücksichtigt 
  
  -> vlt so ietrativer Prozess : die Tabellen finden wo sicher ist -> dann davon die relevanten die direkt kommen : alle Relationen geben und dann nochmal fragen 
  welche Tabellen notwendig sind 

  Wenn man die Tabellennamen und Wörter der Frage lemmatized und Füll wörter entfernt bei Treshhold 0.9

  wenn alleTabellen erhalten sind 

  => Performance  355/ (355 + 505) % wenn man leere weglässt 

  => Performance 355 / 1034 % wenn man leere berücksichtigt 
  
  -> vlt so ietrativer Prozess : die Tabellen finden wo sicher ist -> dann davon die relevanten die direkt kommen : alle Relationen geben und dann nochmal fragen 
  welche Tabellen notwendig sind 

  Schema Linking Ansatz anhand des Resd SQL Paper: 

  Was wurde übernommen : man hat so Tupel mit (Frage, Tabele: Spalte1, Spalte2 , ...) in einem Cross encoder zum Relevanz Schauen gegeben: 
  es wurden immer die top 5 Ergebnisse genommen 

   hit min one table percentage  77.27 %
   miss table percentage 22.73 % 
   no table percentage 0.0
   precision 0.19 % 
   recall 51.84 % 

   Was noch aufgefallen ist: 
   
         Im Deutschen heißen manche Tabellen identisch bzw im englischen sehr ähnlich 

         -> daraus wurden manche Tabellen nicht erkannt 
         -> daraus kann man vlt zu jeder gefundenen Tabelle die Tabellen raussuchen die genau gleich heißen/ sehr ähnlich sind 
         ->  diese Einfach in den Erweiternden Kreis aufnehmen und dannn kann vlt ein LLM diese Filtern welche wichtig sind 
         -> was noch hinzugefügt werden muss Spalte erkannt -> automatisch die Tabelle davon 
         -> werte in Db erkannt aus Frage -> spalte herausfinden -> Tabelle übergeben

Um die Sachen die oben aufgefallen sind 
 -> habe Tabellen die ähnlich heißen mit eingezogen visitor und Visistors 
 -> pro db_id ein Knowledge Graph gebaut -> wenn Tabelle gleich heißen -> folgt nicht alle möglichkeiten 
 -> hier vlt propleme noch ? 
 -> vlt noch so per value suche Verbssern ? 

 Ergebnisse 

 hit min one table percentage  65.09 % + 9% 
miss table percentage 5.51 %
no table percentage 29.4 %
precision 0.1 %
recall 51.06 % + ca 20% 

Mögliche Ansätze die man es gibt von Paper 

1. SQL Query generieren
   
-> zuerst SQL generieren -> anhand der dann Bedingungen bestimmen -> E SQL -> Wert der Bedingung in den Spalten suchen und ähnliche finden 
-> dies dann in Prompt geben mit ganzen Schema oder Schema aus LLm antwort was denkt sind wichtigsten

-> Frage -> erste Generieren -> daruch wissen welche Tabellen / Spalten gebraucht -> noch einmal generieren lassen -> aus der Spalte bekommen : RAT Methode 

2. LLM antwort

-> C3: bekommt aus Prompt wo man Frage und ganzes Schema sendet 

3. Embedden aus



Ergebnisse mit e5 embedding model basierend RAG auf Auto Link Ansatz: 

Mit db angegeben 

hit min one table percentage  94.78 %
miss table percentage 5.22 %
no table percentage 0.0 %
precision 16.34 %
recall 74.95 %


Wenn man von allen dies Indexe aufmeinmal vergleicht und sammelt nimmt 

hit min one table percentage  79.4 %
miss table percentage 20.6 %
no table percentage 0.0 %
precision 0.68 %
recall 51.35 %

-> wie man evntuell verbessern kann 
-> PCA und dann top 10 
-> Werte aus Spalte und Beschreibungen mit embedden 

Ergebnisse mit multi lang ev 

hit min one table percentage  86.46 %
miss table percentage 13.54 %
no table percentage 0.0 %
precision 8.03 %
recall 58.03 %

-> besser, weil versteht deutsche wörter besser 
was man probieren kann 
-> Tabelle klassifiezieren und wenn eine aus einem Kluster drin ist, die auch dazu 
-> Tabellen dazu die ähnlich geschrieben sind / ähnliches bedeuten 
-> Keywords weise embedding -> manchmal findet wörter die passen jedoch nicht für richtiges Wort

mit noch similar geschrieben dazu mit treshhold 0.8 

hit min one table percentage  91.3 %
miss table percentage 8.7 %
no table percentage 0.0 %
precision 3.38 %
recall 66.44 %

hier ohne similar wörter mit einbezogen jedoch wurden Tabellen und Datenbeschreibungen hiunzugefügt und dann embedded 

hit min one table percentage  92.65 %
miss table percentage 7.35 %
no table percentage 0.0 %
precision 8.8 %
recall 66.05 %

-> was aufgefallen ist. Manchmal ähnliche benutzt statt richtige 
-> manchmal keins weil Fokus auf andere Wörter 
   -> dies zu lösen entweder key weise 
   ->  beschreibungen genauer 
   -> question decomposition / umschreiben der question


Gleiche Bedingungen wie oben jedoch mit genauerern Spalten/ Tabellen Beschreibungen: 

hit min one table percentage  94.49 %
miss table percentage 5.51 %
no table percentage 0.0 %
precision 10.06 %
recall 69.44 %

mit anderen Embedding bei Tabellen Beschreibung und Spaltenbeschreibung: 

hit min one table percentage  94.78 %
miss table percentage 5.22 %
no table percentage 0.0 %
precision 10.15 %
recall 70.21 %

gleich wie oben jedoch noch ähnlich klingende dazu und joint tables auch dazu in predicted: 

hit min one table percentage  96.62 %
miss table percentage 3.38 %
no table percentage 0.0 %
precision 1.55 %
recall 92.75 %





Ansatz mit Table namen als anchor und ganze frage k = 5

hit min one table percentage  82.88 %
miss table percentage 17.12 %
no table percentage 0.0 %
precision 0.0 %
recall 57.64 %




Hier wie oben der Gleiche Ansazt dass die Werte aus den Tabellen genommen wurde beim embedden : 

hit min one table percentage  74.95 %
miss table percentage 25.05 %
no table percentage 0.0 %
precision 0.0 %
recall 41.59 %

=> etwas schlechter : vlt etwas schlechter weil in der Datenbank die Werte auf englisch stehen und Gefragt auf deutsch wird 



  
NER ? 
 
Fehler behebung ? 

Struktural Linking: 
Dieses Paper structural_parser_1.pdf soll eine Impl haben  mit spider als GNN darzustellen

Question Decomposition 

die bisherigen Prompts in Papern hatten Beispiele -> kann man auch ohne ? 

mit bidirectional paper (alle db schemas gegeben) mit mistral 7b 

Execution accuracy on all executed queries 21.66% 

mit nur richiger DB Execution accuracy on all executed queries 36.07% 

-> aufgefallen , manchmal murden die Queries mehrmals / verschiedene weil vlt mehrdeutig ist. 

mit den ersten exploring prompt von chain of style prompting mit allen db schemas 

Execution accuracy on all executed queries 5.61%

mit den ersten exploring prompt von chain of style prompting mit nur richtiger db schemas 

Execution accuracy on all executed queries 21.95%

mit den zweiten exploring prompt von chain of style prompting mit nur richtiger db schema 

Execution accuracy on all executed queries 40.62% 


Question Enrichment

Evaluieren 

Exact Matching 

Execution accuracy

Mit dem Ansatz mit den einfachen Prompt und gemma 27 b Model : 

51.05 % 

Mit dem Ansatz mit den einfachen Prompt und gemma 27 b , jetzt auch dazu zählen wenn nicht ausgeführt wurde 

 46.03 %

Self Correction 

einbauen von Fragen wenn etwas mehrdeutig ist ? Mit so vorschlagen welche Optionen ? 


Finetuning für SQL Generieren es allgemein besser kann. 


