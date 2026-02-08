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
  
  -> vlt so ietrativer Prozess : die Tabellen finden wo sicher ist -> dann davon die relevanten die direkt kommen : alle Relationen geben und dann nochmal fragen 
  welche Tabellen notwendig sind 

NER ? 
 
Fehler behebung ? 

Struktural Linking: 
Dieses Paper structural_parser_1.pdf soll eine Impl haben  mit spider als GNN darzustellen


Evaluieren 

Exact Matching 

Execution accuracy
