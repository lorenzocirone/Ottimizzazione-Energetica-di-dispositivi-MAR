import time
from cProfile import label
from math import exp, sqrt
from math import log2
from math import pi
from turtle import color
from gekko import GEKKO
import matplotlib.pyplot as plt
import numpy as np

start_time = time.time()

def distanza(x_ap, y_ap, x , y):      #funzione per il calcolo della distanza
    d = sqrt(pow(x_ap - x, 2) + pow(y_ap - y, 2) ) 
    return d
  
x_ap = 0; y_ap = 0          # posizione fissa dell' AP
  
x_u = [100] ; y_u = [0]     # vettori posizione utente con solo posizione inziale

v_x = 0 ; v_y = 2           # componenti costanti della velocità dell' utente

d = []      # vettore record per la distanza
E_t = []    # vettore record per il consumo energetico
A_t = []    # vettore record Accuracy
Q_t = []    # vettore record Accuracy Loss
C_t = []    # vettore record Cost

t_start = 0 ; t_end = 60 ; t_opt = 1   # tempo di inizio e fine e tempo di ottimizzazione

# Pt = 50 dBm
G_t = 3.0                   # guadagno di trasmissione, del telefono
G_r = 15.0                  # guadagno di ricezione, consideriamo una BS 5G con un'antenna MIMO ad alto guadagno
                  
wave_length = 0.005         # lunghezza d'onda di un segnale 5G, sono onde millimetriche che vanno da 1mm a 10mm [30-300 GHz], scegliamo ad esempio 5mm
W_u = 1.0 * 10**6           # banda assegnata all'utente (1 MHz)
N_0 = 10**(-15.4)           # -154 dBm/Hz = 10^-17.4 mW/Hz        
P_N = W_u * N_0             # potenza del rumore in mW
alpha = 4                   # fattore di peso per la perdita precisione (potremmo cambiarlo)
delta = 0.85                # precisione minima richiesta
lat_max = 0.85              # latenza massima accettata       

s_opt = []                  # pixel della risoluzione (variabile di controllo)
p_opt = []                  # potenza ricevuta dall'AP (variabile di controllo) 
K = 4.0 *10**5              # pixel grezzi
V = 100.0*10**6             # velocità di compressione 100Mbps = 100000000 bps
f = 0.5                     # velocità minima di elaborazione 0.5 TFLOPS = 0.5*10^12 FLOPS 
sigma = 24.0                # ogni pixel contiene 24 bit informativi
epsi = 2.0 * 10**-8


for i in range(t_start, t_end, t_opt):

    # problema di ottimizzazione
    m = GEKKO(remote=False)
    p = m.Var()
    s = m.Var()
    # lower bounds
    p.lower = 1
    s.lower = 0

    # Upper bounds
    p.upper = 1000 #mW      
    s.upper = K
    
    d.append( distanza(x_ap, y_ap, x_u[i], y_u[i]) )             # calcolo la distanza e la salvo

    LOSS = (wave_length/( 4*pi*d[i] ) )**2
    
    SNR = ( p*G_t*G_r * LOSS ) / P_N        # calcolo del rapporto segnale rumore
    print("Iterazione: ",i)
    print("Distanza: " + str(d[i]) + " m")
    print("Fading:", G_t*G_r*LOSS)
    
    R = W_u * (m.log(1 + SNR)/m.log(2) )    # calcolo del data rate

   
    A = 1 - ( 1.578 * m.exp(-6.5*10**-3 * m.sqrt(s))  )         # Precisione
    Q = 1 - A                                                   # Perdita di Precisione
    elab = ( 7 * pow(10, -10) * pow(s, 3/2) + 0.083  )          # modello di elaborazione del carico 1 TFLOPS = 1x10^12 FLOPS

    latenza_tot = (sigma * s)/R + elab/f + (sigma * K)/V        # calcolo latenza totale

    # La potenza era in mW la riporto in W
    E = epsi * sigma *(K-s) + (sigma * (p*10**-3) * s)/R             


    # subjects
    m.Equation(latenza_tot <= lat_max)
    m.Equation(A >= delta )

    # obiettivo
    m.Obj(E + alpha*Q)

    # Set global options
    m.options.IMODE = 3 
    m.options.SOLVER = 3

    # Solve simulation
    m.solve(disp=False) 
    
    
    p_opt.append(p.value[0])        # salvo potenza e risoluzione nei vettori record
    s_opt.append(s.value[0])
    print("Potenza: " + str(p.value[0]) + " mW")
    print("Risoluzione: " + str(s.value[0]) + " pixels")
    
    # ricalcolo questi termini per non avere conflitti con gli operatori GEKKO
    H = p.value[0] * G_r * G_t 
    LOSS = (wave_length/( 4*pi*d[i] ) )**2 
    SNR_t = ( H * LOSS ) / P_N
    R_t = W_u * log2(1 + SNR_t)
    print("Data Rate: ", R_t)
    print("SNR:",SNR_t)

    elab_t = ( 7 * pow(10, -10) * pow(s.value[0], 3/2) + 0.083  )
    latenza_tot_t = (sigma * s.value[0])/R_t + elab_t/f + (sigma * K)/V
    print("Latenza: " + str(latenza_tot_t) + " s")

    A_t.append(1 - ( 1.578 * exp(-6.5*10**-3 * sqrt(s.value[0]))  ))
    print("Accuratezza attuale(%): " + str(A_t[i] * 100) )
    
    Q_t.append((1 - A_t[i])*100)  # moltiplicare per 100 se si vuole graficare l'accuracy loss (%)
    print("Accuracy Loss(%): ", Q_t[i])
    
    E_t.append((epsi*delta*(K-s.value[0]) ) + ((sigma* (p.value[0]*10**-3) *s.value[0])/(R_t)) )
    print("Consumo Energetico: " + str( E_t[i]) + " Joule")

    
    

    C_t.append(E_t[i] + alpha*Q_t[i])
    print("Funzione di Costo: ", C_t[i])         


    x_u.append(x_u[i] + t_opt*v_x)     # faccio evolvere il sistema
    y_u.append(y_u[i] + t_opt*v_y)

    print("\n")

  

print("Vettore coordinata x nel tempo:", x_u)
print("\n")
print("Vettore coordinata y nel tempo:", y_u)
print("\n")
print("Vettore distanze nel tempo:", d)
print("\n")

print("Vettore potenza ottima in mW:", p_opt)
print("\n")
print("Vettore risoluzione ottima in pixel:", s_opt)
print("\n")

print("Vettore Consumo energetico:", E_t)
print("\n")
print("Vettore Accuracy Loss:", Q_t)
print("\n")
print("Vettore Funzione di Costo:", C_t)
print("\n")

print("--- Running Time : %s seconds ---" % round((time.time() - start_time), 3))

#PLOTTING

# Subplot 1 di Potenza, Risoluzione, Accuracy Loss, Consumo Energetico 
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
fig.suptitle('Grafici di Potenza e Risoluzione Ottimali, Accuracy Loss e Consumo Energetico')

fig.subplots_adjust(hspace=0.35)
fig.subplots_adjust(wspace=0.38)

ax1.set_title("Grafico Potenza-Distanza")
ax1.set_xlabel("d(m)")
ax1.set_ylabel("P(mW)")
ax2.set_title("Grafico Risoluzione-Distanza")
ax2.set_xlabel("d(m)")
ax2.set_ylabel("s(pixels)")
ax3.set_title("Accuracy Loss")
ax3.set_xlabel("d(m)")
ax3.set_ylabel("Accuracy Loss(%)")
ax4.set_title("Consumo energetico")
ax4.set_xlabel("d(m)")
ax4.set_ylabel("E(J)")

ax1.plot(d,p_opt, color='blue', label= r'$\alpha$' + " = " + str(alpha))
ax1.grid()
ax1.legend()

ax2.plot(d,s_opt, color='blue', label=r'$\alpha$' + " = " + str(alpha))
ax2.grid()
ax2.legend()

ax3.plot(d, Q_t,  color='blue', label=r'$\alpha$' + " = " + str(alpha)) 
ax3.grid()
ax3.legend()

ax4.plot(d,E_t,  color='blue', label=r'$\alpha$' + " = " + str(alpha))
ax4.grid()
ax4.legend()


# Subpplot 2 di movimento e distanza
fig2, ((gx1, gx2)) = plt.subplots(2, 1)
fig2.suptitle('Grafici di Distanza e Movimento Utente')

fig2.subplots_adjust(hspace=0.35)

gx1.set_title("Movimento Utente")
gx1.scatter(x_ap,y_ap, color="green", marker="o", label="AP")
gx1.set_xlabel("x")
gx1.set_ylabel("y")
gx1.set_xlim(-150,150)     
gx1.set_ylim(-150,150)
gx1.scatter(x_u,y_u, color="red", marker="x", label="UE")
gx1.legend()
gx1.grid()

gx2.set_title("Distanza AP - UE")
gx2.plot(d, color='blue')
gx2.set_xlabel("t(m)")
gx2.set_ylabel("d(m)")
gx2.grid()

plt.show()


# Salavataggio del full subplot
fig.savefig("Grafico1.png", dpi = 1000)  
fig2.savefig("Grafico2.png", dpi = 1000) 


# Salvataggio dei singoli plot

# Salvo primo grafico
extent1 = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
fig.savefig('P-d.png', bbox_inches=extent1)
# Salvo secondo grafico
extent2 = ax2.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
fig.savefig('R-d.png', bbox_inches=extent2)
# Salvo terzo grafico
extent3 = ax3.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
fig.savefig('AccLoss.png', bbox_inches=extent3)
# Salvo quarto grafico
extent4 = ax4.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
fig.savefig('EnCons.png', bbox_inches=extent4)

# Pad the saved area by 10% in the x-direction and 20% in the y-direction
fig.savefig('P-d_expanded.png', dpi=500, bbox_inches=extent1.expanded(1.35, 1.35))       
fig.savefig('R-d_expanded.png', dpi=500, bbox_inches=extent2.expanded(1.35, 1.35))
fig.savefig('AccLoss_expanded.png', dpi=500 ,bbox_inches=extent3.expanded(1.35, 1.32))
fig.savefig('EnCons_expanded.png', dpi=500, bbox_inches=extent4.expanded(1.35, 1.32))