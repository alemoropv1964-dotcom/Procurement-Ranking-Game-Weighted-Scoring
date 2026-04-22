import streamlit as st
import random
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------
# TITOLO E INTRODUZIONE
# ---------------------------------------------------------
st.title("🔄 Simulatore di Procurement – Ciclo Mod 4")
st.write("""
Questo simulatore permette di esplorare dinamiche di procurement multi-fornitore
con fallback ciclico **mod 4**, considerando:
- costo unitario
- lead time
- probabilità di ritardo
- capacità massima
- quantità ordinate
- lead time massimo accettabile

Modifica i parametri e premi **Simula** per vedere i risultati.
""")


# ---------------------------------------------------------
# VISUALIZZAZIONE GRAFICA DEL CICLO
# ---------------------------------------------------------
st.header("🔁 Visualizzazione del ciclo Mod 4")

st.code("F1 → F2 → F3 → F4 → F1", language="text")

st.write("Il ciclo rappresenta l'ordine dei fallback: se un fornitore fallisce, si passa al successivo nel ciclo.")


# ---------------------------------------------------------
# PARAMETRI FORNITORI
# ---------------------------------------------------------
st.header("📦 Parametri dei 4 Fornitori")

fornitori = []
for i in range(4):
    st.subheader(f"Fornitore F{i+1}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        costo = st.number_input(f"Costo F{i+1}", 1, 100, 10)

    with col2:
        lt = st.number_input(f"Lead Time F{i+1}", 1, 60, 5)

    with col3:
        prob = st.slider(f"Prob. Ritardo F{i+1}", 0.0, 1.0, 0.10)

    with col4:
        cap = st.number_input(f"Capacità F{i+1}", 1, 500, 100)

    fornitori.append({
        "costo": costo,
        "lead_time": lt,
        "prob_ritardo": prob,
        "capacita": cap
    })


# ---------------------------------------------------------
# PARAMETRI PROCUREMENT
# ---------------------------------------------------------
st.header("📝 Parametri Procurement")

colA, colB, colC, colD = st.columns(4)

with colA:
    q1 = st.number_input("Ordine 1", 0, 500, 50)
with colB:
    q2 = st.number_input("Ordine 2", 0, 500, 40)
with colC:
    q3 = st.number_input("Ordine 3", 0, 500, 70)
with colD:
    q4 = st.number_input("Ordine 4", 0, 500, 30)

ordini = [q1, q2, q3, q4]

lead_time_max = st.number_input("Lead Time massimo accettabile", 1, 60, 10)

# ---------------------------------------------------------
# PESI PER LA FUNZIONE DI SCELTA
# ---------------------------------------------------------
st.header("⚖️ Pesi per la funzione di scelta (somma = 1)")

col_p1, col_p2 = st.columns(2)

with col_p1:
    peso_lt = st.slider("Peso Lead Time", 0.0, 1.0, 0.5)

with col_p2:
    peso_costo = 1 - peso_lt

st.write(f"Peso costo totale = **{peso_costo:.2f}**")


# ---------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------
def ciclo_mod4(i):
    return (i + 1) % 4

def penalita(lead_time, costo_totale, w_lt, w_c):
    return w_lt * lead_time + w_c * costo_totale


# ---------------------------------------------------------
# SEZIONE FALLBACK PER OGNI ORDINE
# ---------------------------------------------------------
st.header("📌 Logica dei fallback per ogni ordine")

for i in range(4):
    primario = i
    fb1 = ciclo_mod4(primario)
    fb2 = ciclo_mod4(fb1)
    fb3 = ciclo_mod4(fb2)

    st.write(f"""
### Ordine {i+1}
- **Fornitore primario:** F{primario+1}
- **Fallback 1:** F{fb1+1}
- **Fallback 2:** F{fb2+1}
- **Fallback 3:** F{fb3+1}
""")


# ---------------------------------------------------------
# SIMULAZIONE
# ---------------------------------------------------------
st.header("🚀 Esegui Simulazione")

if st.button("Simula"):

    st.subheader("📊 Risultati")
    risultati_radar = []

    for i, quantita in enumerate(ordini):
        st.write(f"## 🔹 Ordine {i+1}: {quantita} unità")

        confronto = []   # per tabella comparativa
        penalita_fornitori = []

        # Valuto TUTTI i fornitori
        for idx, f in enumerate(fornitori):

            costo_totale = quantita * f["costo"]
            stato = "OK"
            pen = None

            # Controllo capacità
            if quantita > f["capacita"]:
                stato = "Scartato: capacità"
            else:
                # Controllo ritardo
                if random.random() < f["prob_ritardo"]:
                    stato = "Scartato: ritardo"
                else:
                    # Controllo lead time
                    if f["lead_time"] > lead_time_max:
                        stato = "Scartato: lead time"
                    else:
                        # Tutto OK → calcolo penalità
                        pen = penalita(f["lead_time"], costo_totale, peso_lt, peso_costo)
                        penalita_fornitori.append({
                            "fornitore": idx + 1,
                            "costo": costo_totale,
                            "lead_time": f["lead_time"],
                            "penalita": pen
                        })

            confronto.append({
                "Fornitore": f"F{idx+1}",
                "Capacità OK": "✔" if quantita <= f["capacita"] else "✘",
                "Ritardo OK": "✔" if stato not in ["Scartato: ritardo"] else "✘",
                "LT OK": "✔" if f["lead_time"] <= lead_time_max else "✘",
                "Costo Totale": costo_totale,
                "Penalità": pen if pen is not None else "-",
                "Stato": stato
            })

        # Mostra tabella comparativa
        st.write("### 📋 Tabella comparativa fornitori")
        st.dataframe(confronto, use_container_width=True)

        # Se nessun fornitore è valido
        if len(penalita_fornitori) == 0:
            st.error("❌ Nessun fornitore disponibile per questo ordine.")
            continue

        # Scelta del fornitore con penalità minima
        best = min(penalita_fornitori, key=lambda x: x["penalita"])

        st.success(
            f"🏆 Fornitore selezionato: **F{best['fornitore']}** "
            f"(Costo totale: {best['costo']}, LT: {best['lead_time']}, Penalità: {best['penalita']:.2f})"
        )

        # Salvo per radar
        risultati_radar.append({
            "ordine": i+1,
            "fornitore": f"F{best['fornitore']}",
            "costo": best["costo"],
            "lead_time": best["lead_time"],
            "penalita": best["penalita"]
        })


    # ---------------------------------------------------------
    # GRAFICO RADAR
    # ---------------------------------------------------------
    st.header("📈 Grafico Radar – Confronto Fornitori Vincitori")

    if len(risultati_radar) > 0:

        costi = np.array([r["costo"] for r in risultati_radar])
        lts = np.array([r["lead_time"] for r in risultati_radar])
        pens = np.array([r["penalita"] for r in risultati_radar])

        costi_norm = costi / costi.max() if costi.max() > 0 else costi
        lts_norm = lts / lts.max() if lts.max() > 0 else lts
        pens_norm = pens / pens.max() if pens.max() > 0 else pens

        labels = ["Costo", "Lead Time", "Penalità"]
        num_vars = len(labels)

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, polar=True)

        for idx, r in enumerate(risultati_radar):
            valori = [costi_norm[idx], lts_norm[idx], pens_norm[idx]]
            valori += valori[:1]

            angoli = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            angoli += angoli[:1]

            ax.plot(angoli, valori, label=f"Ordine {r['ordine']} – {r['fornitore']}")
            ax.fill(angoli, valori, alpha=0.1)

        ax.set_xticks(angoli[:-1])
        ax.set_xticklabels(labels)
        ax.set_title("Confronto tra i fornitori vincitori (valori normalizzati)")
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

        st.pyplot(fig)

    else:
        st.info("Nessun ordine assegnato, impossibile generare il grafico radar.")
