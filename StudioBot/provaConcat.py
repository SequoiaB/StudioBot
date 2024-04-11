import pandas as pd
import ModuloJson
colonne = ['Materia', 'Tempo studiato','Tempo_studio','Tempo_pausa','nS','nP','Efficenza', 'Note']
df = ModuloJson.read_csv_table("tabella_studio", colonne)
ModuloJson.save_user_data("tabella_studio", df)

tempInfo = {'Materia': "?",
            'Tempo studiato': 0, 
            'Tempo_studio': 0,
            'Tempo_pausa': 0,
            'nS':0,
            'nP':0,
            'Efficenza': 0, 
            'Note': "?"
                }

print (type(tempInfo))

tempInfo_df = pd.DataFrame.from_dict(tempInfo)

concat = pd.concat([df,tempInfo_df], ignore_index=True)

print(concat)