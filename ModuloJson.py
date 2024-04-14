import pandas as pd
import re


def read_csv_table(name, columns):
    try:
        table = pd.read_csv(f"./Tabelle/{name}.csv", index_col=0)
        print("csv_table trovata")
        return table
    except FileNotFoundError:
        print("dati utente NON trovati")
        return pd.DataFrame(columns=columns)


def save_user_data(name, table):
    try:
        table.to_csv(f"./Tabelle/{name}.csv", index=True)
        print("csv_table salvata")
    except Exception as e:
        print(f"Errore durante la scrittura del file CSV {name}: {e}")


def add_new_line(name, columns, newline):
    try:
        table = read_csv_table(name, columns)
        tempInfo_df = pd.DataFrame.from_dict([newline])
        concat = pd.concat([table, tempInfo_df], ignore_index=True)
        save_user_data(name, concat)
    except Exception as e:
        print(f"Errore durante l'aggiunta della nuova riga in {name}: {e}")

# Assuming read_csv_table and save_user_data functions are defined elsewhere


def estrai_nomi_da_stringa(s):
    try:
        # Utilizza una regex per trovare tutti i tag nella stringa
        tags = re.findall(r'@(\w+)', s)

        # Se ci sono almeno due tag, restituisci i primi due
        if len(tags) >= 2:
            nome1, nome2 = tags[:2]
            return nome1, nome2
        else:
            # Se non ci sono abbastanza tag, restituisci None
            return None
    except Exception as e:
        # Gestisci eventuali errori
        print(f"Errore durante l'estrazione dei nomi: {e}")
        return None, None


def escape_special_chars(input_string):
    special_chars = ['-', '_', '|', '~',
                     '(', '[', '{', ')', ']', '}', '>', '`', '.']
    escaped_string = ''

    for char in input_string:
        if char in special_chars:
            escaped_string += '\\' + char
        else:
            escaped_string += char

    return escaped_string
