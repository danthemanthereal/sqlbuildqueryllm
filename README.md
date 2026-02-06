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

NER ? 
 
Fehler behebung ? 

Struktural Linking: 
Dieses Paper structural_parser_1.pdf soll eine Impl haben  mit spider als GNN darzustellen


Evaluieren 

Exact Matching 

Execution accuracy
