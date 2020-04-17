# -*- coding: utf-8 -*-
from db_schema import *

""" Module which holds all SQL queries used for the process """


def sql_get_universe(ref_id_list=[]):
    """
    from a given ref_id list return url list
    """
    output = []
    ref_id = []
    ref_url = []
    ref_url2 = []

    if len(ref_id_list) == 0:
        qry = "SELECT ref_id, ref_url FROM ref where ref_end_d IS NULL"
        database_connection = db(qry)
        output_cursor = database_connection.return_cursor()

        for line in output_cursor:
            ref_id.append(line[0])
            ref_url.append('https://www.boursorama.com' + line[1])

            temp_ref_url2 = line[1].replace('/bourse/indices/cours/','')
            temp_ref_url2 = temp_ref_url2.replace('/cours/','')
            temp_ref_url2 = temp_ref_url2.replace('/','')
            ref_url2.append(temp_ref_url2)

    else:
        # loop to get urls
        for elt in ref_id_list:
            ref_id = str(elt)
            temp_qry = f'SELECT ref_url FROM ref WHERE ref_id = {ref_id} AND ref_end_d IS NULL'
            database_connection = db(temp_qry)
            output_cursor = database_connection.return_cursor()
            temp_ref_url = output_cursor.fetchone()[0]
            ref_url.append('https://www.boursorama.com' + temp_ref_url)

            temp_ref_url = temp_ref_url.replace('/bourse/indices/cours/','')
            temp_ref_url = temp_ref_url.replace('/cours/','')
            temp_ref_url = temp_ref_url.replace('/','')
            ref_url2.append(temp_ref_url)
            ref_id = ref_id_list

    output.append(ref_id)
    output.append(ref_url)
    output.append(ref_url2)
    return output

def sql_insert_data(ref_id, date, fermeture, ouverture, haut, bas, vol):
    """
    insert into data table info from internet
    """
    date_correct = '\'' + date + '\''
    qry = (
        f"INSERT INTO data (data_ref_id, data_ouverture, data_fermeture, data_haut, data_bas, data_volume, data_date)"
        f"SELECT {ref_id},{ouverture},{fermeture},{haut},{bas},{vol},ADDDATE({date_correct},0)"
        f"WHERE ("
        f"  SELECT data_id FROM data"
        f"  WHERE 1=1"
        f"  AND data_date = ADDDATE({date_correct},0)"
        f"  AND data_ref_id = {ref_id}"
        f") IS NULL;"
    )
    database_connection = db(qry)

def sql_date_add_price():
    """
    add lines in price table with date present
    in data table
    """

    date_to_add = []
    nb_date = 0

    price_date = dict()
    database_connection = db('SELECT DISTINCT price_date FROM price')
    output_cursor = database_connection.return_cursor()
    for elt in output_cursor:
        price_date[elt[0]] = 1

    data_date = dict()
    database_connection = db('SELECT DISTINCT data_date FROM data')
    output_cursor = database_connection.return_cursor()
    for elt in output_cursor:
        data_date[elt[0]] = 1

    for key in data_date:
        if key not in price_date:
            date_to_add.append(key)

    for date in date_to_add:
        temp_date = '\'' + date.strftime('%Y-%m-%d') + '\''
        qry = f'INSERT INTO price (price_date) VALUES ({temp_date})'
        database_connection = db(qry)
        nb_date += 1

    return nb_date

def sql_get_active_asset():
    """
    return active assets as a field list for price tables
    price_1, price_2
    in a dictionnary
    """
    active_asset_id = dict()
    database_connection = db('SELECT ref_id FROM ref WHERE ref_end_d IS NULL')
    output_cursor = database_connection.return_cursor()
    for elt in output_cursor:
        active_asset_id['price_' + str(elt[0])] = 1

    return active_asset_id

def sql_get_price_headers():
    """
    get current price sql_get_price_headers
    """
    field_in_price = dict()
    database_connection = db('DESCRIBE price')
    output_cursor = database_connection.return_cursor()
    for elt in output_cursor:
        if elt[0] != 'price_id' and elt[0] != 'price_date':
            field_in_price[elt[0]] = 1

    return field_in_price

def sql_add_asset_in_price_table(col_name):
    """
    alter price table, add new assets if detected
    """
    qry = f"ALTER TABLE price ADD COLUMN {col_name} DECIMAL(9, 3) NULL"
    database_connection = db(qry)

def sql_insert_new_records_price():
    """
    check missing price in comparison with date_to_add
    add cash valo
    add a line with corresponding date
    """
    nb_new_record = 0

    # detect cash ref_id and create field
    qry_cash = 'SELECT ref_id FROM ref WHERE ref_nom = \'CASH\''
    database_connection = db(qry_cash)
    output_cursor = database_connection.return_cursor()
    cash_field = 'price_' + str(list(output_cursor)[0][0])

    dates = sql_get_data_dates()

    for date in dates:
        temp_date = '\'' + date[0].strftime('%Y-%m-%d') + '\''
        temp_qry = f'SELECT DISTINCT price_date FROM price WHERE price_date = {temp_date}'
        database_connection = db(temp_qry)
        output_cursor = database_connection.return_cursor()
        nb_elt = len(list(output_cursor))

        if nb_elt == 0:
            temp_qry = f'INSERT INTO price(price_date, {cash_field}) VALUES(ADDDATE({temp_date},0),1);'
            database_connection = db(temp_qry)
            print(temp_qry)
            nb_new_record += 1

    return nb_new_record

def sql_get_price_from_data():
    """
    create median price from data
    """
    qry_select_data = 'SELECT data_date, data_ref_id, ROUND((data_haut + data_bas)/2,2) from data'
    database_connection = db(qry_select_data)
    output_cursor = database_connection.return_cursor()
    data = list(output_cursor)
    return data

def sql_inser_price_if_null_or_empty(data):
    """
    from a given list of date price and asset id,
    update price table is price slot is null or empty
    """
    nb_price_inserted = 0

    # for each data set, upload the corresponding price record
    for elt in data:
        temp_date = '\'' + str(elt[0]) + '\''
        temp_ref = 'price_' + str(elt[1])
        temp_price = elt[2]

        temp_qry = f'SELECT {temp_ref} FROM price WHERE price_date = {temp_date}'
        database_connection = db(temp_qry)
        output_cursor = database_connection.return_cursor()
        price_in_price = list(output_cursor)

        if price_in_price[0][0] is None or int(price_in_price[0][0])==0:
            temp_qry = f'UPDATE price SET {temp_ref} = {str(temp_price)} where price_date = {temp_date}'
            database_connection = db(temp_qry)
            nb_price_inserted += 1

    # update cash
    qry_cash = 'SELECT ref_id FROM ref WHERE ref_nom = \'CASH\''
    database_connection = db(qry_cash)
    output_cursor = database_connection.return_cursor()
    cash_field = 'price_' + str(list(output_cursor)[0][0])
    qry_cash = f'UPDATE price SET {cash_field} = 1'
    database_connection = db(qry_cash)

    # Sort tables
    database_connection = db('ALTER TABLE price ORDER BY price_date ASC')

    return nb_price_inserted

def sql_portfolio_list():
    """ give the list of active portfolio """

    database_connection = db('SELECT DISTINCT port_id FROM portfolio WHERE port_date_f IS NULL')
    output_cursor = database_connection.return_cursor()

    output_list = []
    for elt in output_cursor:
        output_list.append(elt[0])

    return output_list

def sql_insert_update_valo(ptf_list = None, valo_date = None, historical_update = False):
    """
    insert or update valorisation
    By default update for previous pricing day, for all active portfolios
    """
    # Check portfolio list
    if ptf_list is None:
        ptf_list_temp = sql_portfolio_list()
    else:
        ptf_list_temp = ptf_list

    # Check date
    if date is None:
        valo_date = datetime.datetime.now() - datetime.timedelta(days = 1)
        valo_date = valo_date.strftime('%Y-%m-%d')
    else:
        valo_date = date

    valo_date = sql_get_last_price_date_from(valo_date)

    # Loop on portfolio list
    temp_ptf = portfolio()
    for ptf in ptf_list_temp:
        # calculate values to update or insert
        valo = temp_ptf.valo(ptf, valo_date)
        flow = temp_ptf.net_flow(ptf, valo_date)

        #################
        ################# Insert or update in valo table

    # test if there is already a record
    valo_port_id
    valo_valo
    valo_flow
    valo_date

    # test if there is a valo for the given date
    test_qry = f'SELECT * FROM valo WHERE valo_date = \'{valo_date}\' AND valo_port_id = {pft}'
    if sql_has_data(test_qry) == True:
        # Update existing record
        pass

    else:
        # insert a record
        pass

    return 'toto'

def sql_get_last_price_date_from(date):
    """ from a given date return same date if
    there is price at this date or return the last date with price
    """

    qry = f'SELECT MAX(price_date) FROM price WHERE price_date <= \'{date}\''
    database_connection = db(qry)
    output_cursor = database_connection.return_cursor()

    return output_cursor.fetchone()[0]

def sql_has_data(qry):
    """ from an input query, return True if there is data and false if not """
    database_connection = db(qry)
    output_cursor = database_connection.return_cursor()
    if output_cursor.fetchone() is None:
        return False
    else:
        return True
