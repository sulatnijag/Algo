#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
IG Markets Stream API sample with Python
2015 FemtoTrader
"""

import time
import sys
import traceback
import logging
import psycopg2
from psycopg2 import Error
import datetime

from trading_ig import IGService, IGStreamService
from trading_ig.config import config
from trading_ig.lightstreamer import Subscription



class FXdb:

    conn = None


    def __init__(self):
        self.create_connection()

    def create_connection(self):
        """ create a database connection to a SQLite database"""
        try:
            self.conn = psycopg2.connect('host=fxDB user=postgres password=abcd1234')
            print("Connected to DB")

        except Error as e:
            print(e)
        
        return self.conn
    


    def insert_fx_price(self,price):
        """
        Insert price into table
        :param conn:
        :param price:
        """

        sql = ''' INSERT INTO "fxDB".tbl_fx_majors (epic, utm, bid, ofr, time_utc)
                    VALUES(%s, %s, %s, %s, %s) '''


        try:
            cur = self.conn.cursor()
            cur.execute(sql,price)
            self.conn.commit()
            
        except Error as e:
            print("Error: %s" % e)

        return 0




class TickListeners:

    
    def __init__(self, fx_db):
        self.fx_db = fx_db
        
        

    # A simple function acting as a Subscription listener
    def on_prices_update(self, item_update):
        #print("price: %s - " % item_update, **item_update["values"])
        
        try:
            item = item_update["values"]
            time_utc = None
            
            if item["UTM"] is not None:
                time_utc = datetime.datetime.utcfromtimestamp(int(item["UTM"])/ 1000)
            
            price = (item_update["name"], item["UTM"], item["BID"], item["OFR"], time_utc)
            
            self.fx_db.insert_fx_price(price)

        except Error as e:
            print("price: %s - " % item_update, **item_update["values"])
            print("Error: %s" % e)
            




    def on_account_update(self, balance_update):
        print("balance: %s " % balance_update)


def main():
    logging.basicConfig(level=logging.INFO)
    # logging.basicConfig(level=logging.DEBUG)

    print("Algo main() started")

    # create / connect to database
    fx_db = FXdb()
    
    tick_listeners = TickListeners(fx_db)


    ig_service = IGService(
        config.username, config.password, config.api_key, config.acc_type
    )

    ig_stream_service = IGStreamService(ig_service)
    ig_session = ig_stream_service.create_session(encryption=True)
    # Ensure configured account is selected
    accounts = ig_session[u"accounts"]
    for account in accounts:
        if account[u"accountId"] == config.acc_number:
            accountId = account[u"accountId"]
            break
        else:
            print("Account not found: {0}".format(config.acc_number))
            accountId = None
    ig_stream_service.connect(accountId)

    # Making a new Subscription in MERGE mode

    subscription_account = Subscription(
        mode="MERGE", items=["ACCOUNT:" + accountId], fields=["AVAILABLE_CASH"],
    )
    #    #adapter="QUOTE_ADAPTER")

    # Adding the "on_balance_update" function to Subscription
    subscription_account.addlistener(tick_listeners.on_account_update)

    # Registering the Subscription
    sub_key_account = ig_stream_service.ls_client.subscribe(subscription_account)


    # Making a new Subscription in MERGE mode
    subscription_fx = Subscription(
        mode="DISTINCT",
        items=["CHART:CS.D.EURUSD.CSD.IP:TICK", "CHART:CS.D.USDJPY.CSD.IP:TICK","CHART:CS.D.GBPUSD.CSD.IP:TICK","CHART:CS.D.AUDUSD.CSD.IP:TICK","CHART:CS.D.USDCHF.CSD.IP:TICK","CHART:CS.D.USDCAD.CSD.IP:TICK","CHART:CS.D.NZDUSD.CSD.IP:TICK", "CHART.CS.D.USDPHP.CSM.IP:TICK"],
        fields=["BID", "OFR", "UTM"],
    )
    # adapter="QUOTE_ADAPTER")

    # Adding the "on_price_update" function to Subscription
    subscription_fx.addlistener(tick_listeners.on_prices_update)

    # Registering the Subscription
    sub_key_fx = ig_stream_service.ls_client.subscribe(subscription_fx)


    input(
        "{0:-^80}\n".format(
            "HIT CR TO UNSUBSCRIBE AND DISCONNECT FROM \
    LIGHTSTREAMER"
        )
    )

    # Disconnecting
    ig_stream_service.disconnect()
    
    # close database
    fx_db.conn.close()


if __name__ == "__main__":

    main()
