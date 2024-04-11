import pandas as pd
import ModuloJson
colonne = ['Materia', 'Tempo studiato', 'Tempo_studio',
           'Tempo_pausa', 'nS', 'nP', 'Efficenza', 'Note']
df = ModuloJson.read_csv_table("tabella_studio", colonne)
print(df.dtypes)
ModuloJson.save_user_data("tabella_studio", df)

tempInfo = {'Materia': "Storia",
            'Tempo studiato': 10,
            'Tempo_studio': 1,
            'Tempo_pausa': 2,
            'nS': 4,
            'nP': 3,
            'Efficenza': 10,
            'Note': "no"
            }

print(type(tempInfo))

# tempInfo_df = pd.DataFrame.from_dict([tempInfo])

# concat = pd.concat([df, tempInfo_df], ignore_index=True)

ModuloJson.add_new_line("tabella_studio", colonne, tempInfo)
