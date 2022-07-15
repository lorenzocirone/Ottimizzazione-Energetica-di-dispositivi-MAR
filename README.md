# Ottimizzazione-Energetica-di-dispositivi-MAR
L'obiettivo di questo progetto è trovare la coppia della potenza di trasmissione ottimale p e il numero ottimale di pixel s per ridurre al minimo il consumo di energia del dispositivo MAR con la minima perdita di precisione soddisfacendo al contempo i vincoli di latenza e precisione.

La funzione di costo mira quindi a ridurre al minimo il consumo di energia dell'MD con la minima perdita di precisione considerando un compromesso tra il consumo di energia e precisione. Inoltre, per un servizio MAR soddisfacente, dovrebbero essere garantiti il livello di precisione minimo richiesto, δ, e la latenza massima, μ.

PSEUDOCODICE:
1. Definire la velocità costante dell’utente che si muove di moto rettilineo uniforme 𝑣= (𝑣_𝑥¦𝑣_𝑦 ), la posizione iniziale dell’utente 𝑝_0= (𝑥_0¦𝑦_0 ) , la posizione fissa dell’ access point 𝑝_𝐴𝑃= (𝑥_𝐴𝑃¦𝑦_𝐴𝑃 ) , il tstart , il tend e il il topt .
2. Calcolo della distanza iniziale tra access point e utente 𝑑= √((𝑥_0  −𝑥_𝐴𝑃 )^2+ (𝑦_0− 𝑦_𝐴𝑃 )^2 )   .
3. Impostare il problema di ottimizzazione: nel termine energetico della funzione di costo compare il data  rate R con la distanza tra AP e UE appena trovata.
4. Risolvere e trovare la prima potenza ottima p0 e la risoluzione s0 .
5. Salvare tali valori in due vettori record.
6. Far evolvere il sistema 𝑥_(𝑖+1)= 𝑥_𝑖 + 𝑣_𝑥 * 𝑡_𝑜𝑝𝑡   ,  𝑦_(𝑖+1)= 𝑦_𝑖 + 𝑣_𝑦 * 𝑡_𝑜𝑝𝑡   in questo modo la posizione dell’ utente varia in modo lineare.
7. Tornare allo step 3 e iterare fino a raggiungere tend .
8. Plottare i vettori record.


