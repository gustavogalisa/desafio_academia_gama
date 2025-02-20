import pyodbc
import api_request as api
from datetime import datetime, date, timedelta


def insert_data(cursor):
    endpoint_country = "https://api.covid19api.com/countries"
    countries = api.get_data_from_api(endpoint_country)

    insert_row_counter = 0

    for country in countries:

        try:
            country_id = 0
            cursor.execute("INSERT INTO COUNTRY VALUES (?,?,?)", country['Country'], country['ISO2'], country['Slug'])
            insert_row_counter += 1
            cursor.execute("SELECT @@IDENTITY AS ID;")
            country_id = cursor.fetchone()[0]

            # cursor.execute("SELECT * FROM COUNTRY WHERE SLUG=?", country['Slug'])
            # country_id = cursor.fetchone()[0]

            # start_date = datetime.strptime('2020-01-01', '%Y-%m-%d')
            # finish_date = datetime.strptime('2020-01-08', '%Y-%m-%d')
            current_date = date.today()
            # while finish_date.date() <= current_date:

            endpoint_country_data = f"https://api.covid19api.com/country/{country['Slug']}?" \
                                    f"from=2020-01-01T00:00:00Z&to={current_date}T00:00:00Z"
            country_covid = api.get_data_from_api(endpoint_country_data)
            # start_date = start_date + timedelta(8)
            # finish_date = finish_date + timedelta(8)

            if country_id != 0:
                for covid in country_covid:
                    if covid['Province'] == "":

                        modified_date = covid['Date'].split('T', 1)[0]
                        selected_day = modified_date.split('-')[2]
                        today = datetime.today().date()

                        try:
                            # insert confirmed (Case Type 1)
                            cursor.execute("INSERT INTO COUNTRY_COVID_DAILY_CASES VALUES (?,?,?,?)",
                                           (country_id, 1, covid['Confirmed'], covid['Date']))
                            insert_row_counter += 1

                            try:
                                # insert deaths (Case Type 2)
                                cursor.execute("INSERT INTO COUNTRY_COVID_DAILY_CASES VALUES (?,?,?,?)",
                                               (country_id, 2, covid['Deaths'], covid['Date']))
                                insert_row_counter += 1

                            except Exception as e:
                                cursor.rollback()
                                print(f'Erro de insert na Tabela COUNTRY_COVID_DAILY_CASES '
                                      f'do país {country["Country"]}. Erro encontrado: {e}')

                        except Exception as er:
                            cursor.rollback()
                            print(f'Erro de insert na Tabela COUNTRY_COVID_DAILY_CASES '
                                  f'do país {country["Country"]}. Erro encontrado: {er}')

                        print(f"{country['Country']} dia {covid['Date'].split('T', 1)[0]} salvos...")

        except Exception as err:
            cursor.rollback()
            print(f'Erro de insert na Tabela COUNTRY do país {country["Country"]}. Erro encontrado: {err}')

        print(f"Dados do país {country['Country']} salvos com sucesso...")

    print(f'Inseridos {insert_row_counter} registros inseridos no banco de dados.')


def opens_connection():
    try:
        # second connection available for testing
        """pyodbc.connect('Driver={SQL Server};'
                              'Server=sqlservergama.database.windows.net;'
                              'Database=db1;'
                              'UID=hanna;'
                              'PWD=P@ssw0rd;',
                              autocommit=True)"""

        # connection being used
        return pyodbc.connect('Driver={SQL Server};'
                              'Server=sqlcovid19.database.windows.net;'
                              'Database=DB_COVID_NINETEEN;''UID=datarangers;'
                              'PWD=data_rangers19;',
                              autocommit=True)

    except Exception as e:
        print(f'Erro ao conectar no SQL Server.', e)


def opens_cursor():
    connection = opens_connection()
    return connection, connection.cursor()


print(f'Iniciando execução do script Covid-19')
time_ini = datetime.now()

print('Testando conexão com o banco...')
conn, global_cursor = opens_cursor()
print("Conexão com o banco realizada com sucesso...")

print('Carga no banco iniciada...')
insert_data(global_cursor)
global_cursor.close()
conn.close()
print('Carga no banco finalizada.')

elapsed = datetime.now() - time_ini
print(f'Execução do script finalizada. Tempo gasto: {elapsed}')
