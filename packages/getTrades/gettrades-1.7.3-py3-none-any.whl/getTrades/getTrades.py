#!/bin/python3

global debug
global uri
global arguments

debug=False
#debug=True
uri = "wss://ws.bitvavo.com/v2/"  # Bitvavo API endpoint


if debug: print_me('import hashlib')
import hashlib

if debug: print_me('import hmac')
import hmac

if debug: print_me('import json')
import json

if debug: print_me('import pandas')
import pandas as pd # pip install pandas

if debug: print_me('import websockets')
import websockets # pip install websockets

if debug: print_me('import StringIO')
from io import StringIO

if debug: print_me('import threading')
import threading

# if debug: print_me('import logging')
# import logging

if debug: print_me('import argparse')
import argparse

if debug: print_me('import datetime')
from datetime import datetime

if debug: print_me('import websockets')
from websockets.sync.client import connect

# if debug: print_me('import pprint')
# from pprint import pprint

if debug: print_me('import base64')
import base64

if debug: print_me('import time')
import time

if debug: print_me('import asyncio')
import asyncio

if debug: print_me('import sys')
import sys

if debug: print_me('import tabulate') 
from tabulate2 import tabulate # pip install tabulate2

if debug: print_me('import keyring') 
import keyring # pip install keyring

# if debug: print_me('import configparser')
# import configparser

# if debug: print_me('import jinja2')
# import jinja2 # pip install Jinja2

if debug: print_me('import os')
import os

if debug: print_me('import inspect')
import inspect
from inspect import currentframe, getframeinfo

if debug: print_me('import configparser-crypt')
from configparser_crypt import ConfigParserCrypt # pip install configparser-crypt

# if debug: print_me('import yubico')
# import yubico   # pip install python-yubico
# 
# from mfa import MFA # pip install mfa-authenticator
# if debug: print_me('import mfa-authenticator')
# 
# import qrcode # pip install qrcode
# if debug: print_me('import qrcode')


pd.options.display.max_seq_items = None
pd.options.display.max_rows=None

#pd.option_context('format.precision', 2)
pd.options.display.float_format = '{:.2f}'.format
#pd.set_option("display.float_format", None)

# Flag to control the sending process
sending = True

########
async def send_message(messages, responses,debug=False):
    """ Send a single message to the WebSocket server """
    message=''
    twister="|/-\\";x=-1

    try:
        if not debug:x=x+1 if x<3 else -1;print('\u001b[37;1m',twister[x],'\u001b[32;1m','\033[1A')
        if debug: print_me('-entry---',threading.current_thread().name,'-----------------------------------------------------')
        async with websockets.connect(uri) as websocket:
            last=False
            for cmd in messages:
                if not debug:x=x+1 if x<3 else -1;print('\u001b[37;1m',twister[x],'\u001b[32;1m','\033[1A')
                if cmd == messages[-1]:
                    if debug: print_me('! last')
                    last=True
                if debug: print_me('> sending   : ', threading.current_thread().name, cmd)
                #print(f'> {cmd}')
                await websocket.send(json.dumps(cmd))
                receiving=True
                while receiving:
                    if not debug:x=x+1 if x<3 else -1;print('\u001b[37;1m',twister[x],'\u001b[32;1m','\033[1A')
                    message = await websocket.recv()
                    if debug: print_me('< receiving : ', threading.current_thread().name, message )
                    responses.append(message)
                    msg=json.loads(message).keys()
                    if not debug:x=x+1 if x<3 else -1;print('\u001b[37;1m',twister[x],'\u001b[32;1m','\033[1A')

                    if 'response' in msg:
                        if debug: print_me('< RESPONSE')
                        receiving=False

                    if 'event' in msg:
                        if debug: print_me('< EVENT')
                        receiving=True

                    if 'authenticated' in msg:
                        if debug: print_me('< AUTHENTICATED')
                        receiving=False

                    if 'error' in msg:
                        if debug: print_me('< ERROR')
                        print(json.loads(message)['error'])
                        receiving=False
                        raise Exception(str(json.loads(message)['error']))

                    if debug: print_me(json.loads(message)['response'] or 'x')
                    

    except Exception as e:
        print("Exception: ", e)
    #print(responses)
    if not debug:x=x+1 if x<3 else -1;print('\u001b[37;1m',twister[x],'\u001b[32;1m','\033[1A')
    if debug: print_me('-exit----',threading.current_thread().name,'-----------------------------------------------------')
    return responses


######## 
def create_signature(timestamp: int):
    if debug: trace_me(inspect.stack())
    #Create a hashed code to authenticate your connection to Bitvavo API.

    string = str(timestamp) + 'GET' + '/v2/websocket'
    signature = hmac.new(config['api_secret'].encode('utf-8'), string.encode('utf-8'), hashlib.sha256).hexdigest()
    #if debug: print_me('sig: ',signature)
    if debug: trace_me(inspect.stack(),f'sig: {str(signature)}')
    return signature



####################################################################
def authenticate(requestId):
    #if debug: print_me('> def authenticate() |','\r')
    if debug: trace_me(inspect.stack(),'')
    access_window = 10000
    timestamp = int(time.time() * 1000)
    body = {
        'requestId': requestId,
        'action': 'authenticate',
        'key': config['api_key'],
        'signature': create_signature(timestamp),
        'timestamp': timestamp,
        'window': access_window,
    }
    return body

########
def sign(body):
    if debug: trace_me(inspect.stack(),'')
    access_window = 10000
    timestamp = int(time.time() * 1000)
    body.update({'key': config['api_key']})
    body.update({'signature': create_signature(timestamp)})
    body.update({'timestamp': timestamp})
    body.update({'window': access_window})

    return body


########
def tx2df(responses, col_types, columns_names):
    if debug: trace_me(inspect.stack(),'')
    if debug: print_me('responses: ',type(responses),len(responses))
    if debug: print_me('col_types: ',type(col_types))
    #print(responses)


    df = pd.DataFrame(columns=columns_names)


    #{"transactionId": "", "executedAt": "", "type": "", "priceCurrency": "", "priceAmount": "", "sentCurrency": "", "sentAmount": "", "receivedCurrency": "", "receivedAmount": "", "feesCurrency": "", "feesAmount": ""}


    for i in responses:
        items=json.dumps(i['response']['items'])
        itm=str(items)
        df_sub = pd.read_json(StringIO(itm), dtype=col_types, convert_dates=['executedAt'])
        df = pd.concat([df,df_sub], ignore_index=True)
    if debug: trace_me(inspect.stack(),'result')
    if debug: print_me(df.head(10))
    return df


####################################################################
def balance2df(response):

    col_types={'available':'float', 'inOrder':'float'}
    items=json.dumps(response['response'])
    itm=str(items)
    rename={'symbol':'symbol', 'available':'Balance-available', 'inOrder':'Balance-inOrder'}
    df = pd.read_json(StringIO(itm), dtype=col_types).rename(columns = rename)
    df['Balance-total']=df['Balance-available']+df['Balance-inOrder']

    return df

####################################################################
def group_tokens(df):

    r=['executedAt','type','sentCurrency','sentAmount','receivedCurrency','receivedAmount']

    ############ EUR to left ##############
    df['sentAmount'] *=-1 #make outgoing funds negative
    df['feesAmount'] *=-1 #make outgoing funds negative
    df['executedAt'] = pd.to_datetime(df["executedAt"].dt.strftime("%Y-%m-%d %H:%M:%S"))

    mtch1 = (df['receivedCurrency']=='EUR') # swap EUR to left / 29apr2025
    mtch2 = ((df['sentCurrency']!='EUR') & (df['receivedCurrency'].isna())) # swap EUR to left / 29apr2025
    df.loc[mtch1 | mtch2, ['sentCurrency','sentAmount','receivedCurrency','receivedAmount']] = (df.loc[mtch1 | mtch2, ['receivedCurrency','receivedAmount','sentCurrency','sentAmount']].values)

    return df


####################################################################
####################################################################
async def query_bv(uri, args=None):
    global config
    global requestId
    global debug
    global arguments
    """ Main function that runs listen and send tasks together """

    resultset = []
    reread=True # always reread from bitvavo by default
    selected_Config_Nr=None

    parser = argparse.ArgumentParser(prog='python -m getTrades | pipx run getTrades',epilog="Initial run will ask for API and Secret to api.bitvavo.com and store this information encrypted in a config.ini file.\nThe AES encryption key is stored in your local kerring, hence a password will be asked ")
    group = parser.add_mutually_exclusive_group()

    try:
        parser.add_argument("-v", "--verbose", action="store_true", help="show debug output")
        parser.add_argument("-k", "--keep",    action="store_true", help="(Advanced) use saved result set, don't query Bitvavo again")
        parser.add_argument("-s", "--sort",    action="store_true", help="sort by token name")
        group.add_argument( "-l", "--list",    action="store_true", help="list all config section and their numbers")
        group.add_argument( "-a", "--add",     action="store_true", help="add a new config section")
        group.add_argument( "-d", "--delete",  default=[-1], type=int, nargs=1, metavar='#', help="delete a config section by number")
        group.add_argument( "-u", "--use",     default=[-1], type=int, nargs=1, metavar='#', help="use a config section by number")
    
    except Exception(e):
        print(e)
        raise

    arguments = parser.parse_args()
    
    config_count=count_config_sections()

    try:
        if arguments.verbose:
            debug=True
            trace_me(inspect.stack(),'########## debug turned on ##########')
            if debug: trace_me(inspect.stack(), args)

        if arguments.keep:
            resultset = load_json('resultset.json')
            if len(resultset)==0:
                print('NO PREVIOUS RESULTSET')
                reread=True
                resultset = []
            else:
                reread=False

        if arguments.list:
            list_all_config_sections();exit('')

        if arguments.add:
            write_new_config_section();exit('')

        if arguments.delete[0]!=-1:
            selected_Config_Nr=int(arguments.delete[0])
            if debug: trace_me(inspect.stack(),'d: '+str(selected_Config_Nr))
            delete_config_section(selected_Config_Nr);exit('')

        if arguments.use[0]==-1 and arguments.delete[0]==-1: #use and delete not used
            if config_count>1:
                print('More than 1 config available, use -u # to select which to use.');exit('')
            selected_Config_Nr=0
            if debug: trace_me(inspect.stack(),'o: '+str(selected_Config_Nr))

        if arguments.use[0]!=-1 and arguments.delete[0]==-1: #use used
            selected_Config_Nr=int(arguments.use[0])
            if debug: trace_me(inspect.stack(),'u: '+str(selected_Config_Nr))


    except KeyboardInterrupt:
        raise Exception('Keyboard stop')

    #return df_trades, df_price
    
    try:

        config = read_config(selected_Config_Nr) # Bitvavo_Home

        tasks = []
        cmd_seq = {}
        if reread:        
            cmdID=1
            cmd_seq[cmdID] = []
            requestId = 1
            cmd_seq[cmdID].append({'action':'getTime','requestId':requestId})

            tasks.append(threading.Thread(target=asyncio.run, name='1:getTime', args=(send_message(cmd_seq[cmdID],resultset), )))
            if debug: trace_me(inspect.stack(),'length of task queue: '+str(len(tasks)))
            
            tasks[-1].start()

        if reread:
            cmdID=2
            cmd_seq[cmdID] = []
            requestId = 2
            cmd_seq[cmdID].append(authenticate(requestId))
            requestId = 3
            cmd_seq[cmdID].append({'action':'privateGetTransactionHistory','fromDate':1,'maxItems':1, 'requestId': requestId})
            requestId = 4
            cmd_seq[cmdID].append({'action':'privateGetBalance', 'requestId': requestId})

            tasks.append(threading.Thread(target=asyncio.run, name='234:privateGet..', args=(send_message(cmd_seq[cmdID],resultset, False), )))
            if debug: trace_me(inspect.stack(),'length of task queue: '+str(len(tasks)))
            
            tasks[-1].start()

            for t in tasks:
                t.join()
                #if debug: print_me(f'< task {t.name} done')
                if debug: trace_me(inspect.stack(),f'task {t.name} done')
            if debug: trace_me(inspect.stack(),'')
        tasks = []


        x=4 # privateGetBalance
        y = [json.loads(r) for r in resultset if json.loads(r)['requestId'] == x] # = dict

        # make into DF's

        if len(y) == 1: 
            df_wallet_balance = balance2df(y[0]) #balance per token
            df_wallet_balance.set_index(['symbol'], inplace=True)

            df_wallet_balance.loc['EUR_wallet']=df_wallet_balance.loc['EUR'] #swap out real EURO balance
            df_wallet_balance.drop(['EUR'],axis=0,inplace=True) # drop original EUR line as it is now in EUR_Wallet

            if debug: trace_me(inspect.stack(),'print(df_wallet_balance)')
            if debug: print_me(df_wallet_balance)
        else:
            raise Exception('unexpected return length (line #355)')

            
    
        ################ add tx history

        x=3 # privateGetTransactionHistory (summary)
        y = [json.loads(r) for r in resultset if json.loads(r)['requestId'] == x]

        if debug: trace_me(inspect.stack(),'y=3 length privateGetTransactionHistory')
        
        if len(y)!=1:
            raise Exception('No results (line #367)')

        total_records = y[0]['response']['totalPages']
        print('Total trade records: ',total_records)

        cmdID=3
        cmd_seq[cmdID] = []

        if reread:
            for i in range(1,(total_records//100)+2):
            #for i in range(4,6):
                cmd_seq[cmdID] = []
                requestId = 5
                cmd_seq[cmdID].append(authenticate(requestId))
                requestId = 6
                cmd_seq[cmdID].append({'action':'privateGetTransactionHistory','fromDate':1,'maxItems':100, 'page': i, 'requestId': requestId})

                tasks.append(threading.Thread(target=asyncio.run, name='56:privateGetTransactionHistory: '+str(i), args=(send_message(cmd_seq[cmdID],resultset), )))
                if debug: trace_me(inspect.stack(),f'length of task queue: ,{str(len(tasks))}')
                
                tasks[-1].start()
    
            for t in tasks:
                t.join()
                if debug: trace_me(inspect.stack(),f'! task {t.name} done')
    
            await asyncio.sleep(2)
        tasks = []

        x=6 # privateGetTransactionHistory (details)
        y = [json.loads(r) for r in resultset if json.loads(r)['requestId'] == x]

        col_types=   {'priceAmount': 'float', 'sentAmount': 'float', 'receivedAmount': 'float', 'feesAmount':'float' }
        columns=["transactionId","executedAt","type","priceCurrency","priceAmount","sentCurrency","sentAmount","receivedCurrency","receivedAmount","feesCurrency","feesAmount"]
        if len(y) >= 0: df_trades = tx2df(y, col_types, columns) # tx history to df_trades

        ################ add now-ticker-price
        if debug: trace_me(inspect.stack(),'add tickerprice ')
        
        symbols = df_wallet_balance.loc[df_wallet_balance['Balance-total'] > 0].index.to_list() #list of symbols
        
        if debug: trace_me(inspect.stack(),'symbols in wallet')
        if debug: print_me(symbols)
        
        if reread: # reread if no previous resultset file
            cmdID=4
            cmd_seq[cmdID] = []
            requestId = 7
            for i in symbols:
                if i not in ('EUR','_EUR_d','_EUR_w','EUR_wallet'):
                    cmd_seq[cmdID].append({'action':'getTickerPrice', 'market':i+'-EUR' ,'requestId': requestId })
            tasks.append(threading.Thread(target=asyncio.run, name='7:getTickerPrice: '+str(i), args=(send_message(cmd_seq[cmdID],resultset), ))) #getTickerPrice

            if debug: trace_me(inspect.stack(),'length of task queue: '+str(len(tasks)))
            
            tasks[-1].start()
    
            for t in tasks:
                t.join()
                if debug: trace_me(inspect.stack(),f'! task {t.name} done')

        ### make into df
        if debug: trace_me(inspect.stack(),'ticker price > df_wallet x EURO')

        x=7 # getTickerPrice
        y = [json.loads(r) for r in resultset if json.loads(r)['requestId'] == x]
    
        itmsbase={'response':{'items':[]}}
        itms=itmsbase['response']['items']
        #itms.append({'EUR': 1.0})
        itms.append({'EUR_wallet': 1.0})
        if debug: trace_me(inspect.stack(),'')
        if debug: print_me('############### ',type(itms),itms)

        for i in y:
            i["response"]["symbol"]=i["response"]["market"][0:-4]
            i["response"]["price"]=float(i["response"]["price"])
            if debug: print_me({i["response"]["symbol"]:float(i["response"]["price"])})
            itms.append({i["response"]["symbol"]:float(i["response"]["price"])})

        if debug: trace_me(inspect.stack(),'')
        if debug: print_me('############### ',type(itms),itms)
        
        #columns=[[{'EUR_wallet': 1.0}, {'BTT': 6.7639e-07}]
        if len(itms) >= 0: df_price = tx2df([itmsbase],col_types, None) # unrealized
        
        #get price into right format for merge
        df_price = df_price.stack(future_stack=False) #drop NaN's and make symbols the index
        df_price = pd.DataFrame(df_price.droplevel(0)).reset_index() # lose the rangeindex
        df_price.index=df_price['index']   # put an index on symbol
        df_price.index.name='symbol' # name  it symbol
        df_price = df_price.drop(['index'], axis=1) #drop the old index column
        df_price.rename({0:'price'}, axis=1, inplace=True) #rename column 0 into price

        # merge wallet balance with current price to get to 'EUR balance unrealized'
        df_price = pd.merge(df_price, df_wallet_balance, left_index=True, right_index=True, how='outer')
    
        if debug: trace_me(inspect.stack(),'df_price')
        if debug: print_me(df_price)

        df_price['EUR(unrealized)'] = df_price['price']*df_price['Balance-total'] # add total unrealized

        save_json('resultset.json',resultset)

    except KeyboardInterrupt:
        raise Exception('Keyboard stop')
    return df_trades, df_price




####################################################################
####################################################################
def read_config(selected_Config_Nr=None):

    file = 'config.ini'

    print('Check for config file ',file)
    if not os.path.exists(file):
        print('No previous config file found, create new')
        write_new_config()
        exit()

    conf_file = ConfigParserCrypt()

    #if debug: print_me('pk:',keyring.get_password("system", "getTrades"))
    conf_file.aes_key = base64.b64decode(keyring.get_password("system", "getTrades"))
    
    # Read encrypted config file
    conf_file.read_encrypted(file)

    conf_file_sections=conf_file.sections()
    if len(conf_file_sections)==0:
        print('No previous config sections foufound, create new config.ini file')
        os.remove("config.ini") 
        write_new_config()
        exit()

    
    if debug:
        print('\u001b[33;1m') #Yellow 
        for i in conf_file_sections:
            print(i)
            print(conf_file[i]['api_key'])
            print(conf_file[i]['api_secret'])
            print()

        print('selected_Config_Nr:     ',selected_Config_Nr)
        print('conf_file_sections:     ',conf_file_sections)
        print('len conf_file_sections: ',len(conf_file_sections)) 
        print('\u001b[32;1m') #Green 

    if len(conf_file_sections)==0 and selected_Config_Nr is None:
        selected_Config_Nr=0
        if conf_file_sections is None or conf_file_sections == '' or len(conf_file_sections)>1:
            if conf_file_sections is not None :
                print('Available configs: ')
                j=0
                for i in conf_file_sections:
                    print(str(j)+') '+str(i))
                    j=j+1
                selected_Config_Nr = input("Enter Config Nr: ")            
    else:
        if len(conf_file_sections)==1:
            print('NOTICE: only 1 config section, using default config')
            selected_Config_Nr=0

    section=conf_file_sections[int(selected_Config_Nr)]

    return conf_file[section]



####################################################################
def write_new_config():
    file = 'config.ini'
    conf_file = ConfigParserCrypt()

    # Create new AES key
    conf_file.generate_key()

    # Don't forget to backup your key somewhere
    base64EncodedStr = base64.b64encode(conf_file.aes_key).decode() # encode bytestring, then decode into string

    keyring.set_password("system", "getTrades", base64EncodedStr)

    default_value = 'Bitvavo_Home'

    configname = input(f"Config name [{default_value}]: ") or default_value
    api_key    = input("API Key                      : ") 
    api_secret = input("API Secret                   : ") 

    conf_file.add_section(configname)
    conf_file[configname]['api_key']     = api_key
    conf_file[configname]['api_secret']  = api_secret

    # Write encrypted config file
    with open(file, 'wb') as file_handle:
        conf_file.write_encrypted(file_handle)
        print('New config written')
        print()
    return


####################################################################
def write_new_config_section():
    file = 'config.ini'
    conf_file = ConfigParserCrypt()

    file = 'config.ini'

    print('Check for config file ',file)
    if not os.path.exists(file):
        print('No previous config file found, create new')
        write_new_config()

    conf_file = ConfigParserCrypt()

    #if debug: print_me('pk:',keyring.get_password("system", "getTrades"))
    conf_file.aes_key = base64.b64decode(keyring.get_password("system", "getTrades"))
    
    # Read encrypted config file
    conf_file.read_encrypted(file)

    conf_file_sections=conf_file.sections()
    
    print('###################')

    if conf_file_sections is not None :
        print('Current configs:')
        j=0
        for i in conf_file_sections:
            print(str(j)+') '+str(i))
            j=j+1

    default_value = ''

    configname     =input(f"New config name              : ") or default_value
    if configname not in conf_file_sections:
        api_key    = input("API Key                      : ") 
        api_secret = input("API Secret                   : ") 

        conf_file.add_section(configname)
        conf_file[configname]['api_key']     = api_key
        conf_file[configname]['api_secret']  = api_secret
    else:
        print('error, section already exists')
        exit()

    # Write encrypted config file
    with open(file, 'wb') as file_handle:
        conf_file.write_encrypted(file_handle)
        print('New Config written')
        print()
    return



####################################################################
def delete_config_section(selected_Config_Nr=None):
    file = 'config.ini'

    print('Check for config file ',file)
    if not os.path.exists(file):
        print('No previous config file found, create new')
        return 'no config file'

    conf_file = ConfigParserCrypt()

    # if debug: print_me('pk:',keyring.get_password("system", "getTrades"))
    conf_file.aes_key = base64.b64decode(keyring.get_password("system", "getTrades"))
    
    # Read encrypted config file
    conf_file.read_encrypted(file)

    conf_file_sections=conf_file.sections()
    
    if debug:
        print('\u001b[33;1m') #Yellow 
        print('###################')
        print(type(conf_file_sections),conf_file_sections)
        print('###################')
        print('\u001b[32;1m') #Green 

    if selected_Config_Nr is not None:
        section_nr_to_delete = int(selected_Config_Nr)
    else:
        if conf_file_sections is not None :
            print('Available configs:')
            j=0
            for i in conf_file_sections:
                print(str(j)+') '+str(i))
                j=j+1
    
        section_nr_to_delete = int(input("Enter Config Nr to delete: "))

    print('deleting: '+conf_file_sections[section_nr_to_delete])
    conf_file.remove_section(conf_file_sections[section_nr_to_delete])
    print('Config section deleted')
    
    # Write encrypted config file
    with open(file, 'wb') as file_handle:
        #file_handle.seek(0)
        conf_file.write_encrypted(file_handle)
        print('New Config file written')
        print()
    return

####################################################################
def count_config_sections():
    file = 'config.ini'

    print('Check for config file ',file)
    if not os.path.exists(file):
        print('No previous config file found, create new')
        return 'no config file'

    conf_file = ConfigParserCrypt()

    #print('pk:',keyring.get_password("system", "getTrades"))
    conf_file.aes_key = base64.b64decode(keyring.get_password("system", "getTrades"))
    
    # Read encrypted config file
    conf_file.read_encrypted(file)

    conf_file_size=len(conf_file.sections()) or 0
    
    if debug:
        trace_me(inspect.stack(),'###################')
        print('\u001b[33;1m') #Yellow 
        print('###################')
        print(type(conf_file_size),conf_file_size)
        print('###################')
        print('\u001b[32;1m') #Green 

    return conf_file_size


####################################################################
def list_all_config_sections():
    file = 'config.ini'

    print('Check for config file ',file)
    if not os.path.exists(file):
        print('No previous config file found, create new')
        return 'no config file'

    conf_file = ConfigParserCrypt()

    #print('pk:',keyring.get_password("system", "getTrades"))
    conf_file.aes_key = base64.b64decode(keyring.get_password("system", "getTrades"))
    
    # Read encrypted config file
    conf_file.read_encrypted(file)

    conf_file_sections=conf_file.sections()
    
    if debug:
        trace_me(inspect.stack(),'###################')
        print('\u001b[33;1m') #Yellow 
        print('###################')
        print(type(conf_file_sections),conf_file_sections)
        print('###################')
        print('\u001b[32;1m') #Green 


    if conf_file_sections is not None :
        print('Available configs:')
        j=0
        for i in conf_file_sections:
            print(str(j)+') '+str(i))
            j=j+1
    return

####################################################################
def save_dataset(dataset_file, df):
    print('save_dataset: ',dataset_file,' / ',len(df),' entries')

    store = pd.HDFStore(dataset_file,'w')
    try:
        if len(df) == 0:
            raise ValueError('no entries to save')
        store.put('df_raw_trx', df,  format='table')
        store.close()
    except Exception as e:
        # # # print()
        print('!! save_dataset !!!!!!!!!!!!!!!!!!!!')
        store.close()
        traceback.print_exc(file=sys.stdout)
        pass
    return


####################################################################
def load_dataset(dataset_file):

    print('load: ',dataset_file)
    try:
        with pd.HDFStore(dataset_file) as hdf:
            print(hdf.keys())
            df=hdf.get(key='/df_raw_trx', format='table')
            #print(len(df))
    except Exception as e:
        print('no previous datasets found, load empty, ',e)
        all_collumns=['transactionId', 'executedAt', 'type', 'priceCurrency', 'priceAmount','sentCurrency', 'sentAmount', 'receivedCurrency', 'receivedAmount','feesCurrency', 'feesAmount', 'address']
        df=pd.DataFrame(all_collumns)
        raise e

    df.index.name='token'
    return df

####################################################################
####################################################################
def save_json(dataset_file, json_data):
    print('save_json: ',dataset_file,' / ',len(json_data),' entries')
    try:
        if len(json_data) == 0:
            raise ValueError('no entries to save')
        with open(dataset_file, 'w') as f:
            json.dump(json_data, f)
    except Exception as e:
        print('!! save_json !!!!!!!!!!!!!!!!!!!!')
        traceback.print_exc(file=sys.stdout)
        pass
    return


####################################################################
def load_json(dataset_file):
    print('load_json: ',dataset_file)
    try:
        with open(dataset_file, 'r') as f:
            json_data = json.load(f)
    except Exception as e:
        print('no previous json file found, load empty, ',e)
        json_data=[]
        pass
    return json_data

####################################################################
def trace_me(s, remark=''):
    f=s[0]
    print('\u001b[33;1m') #Yellow 
    print(f"########## [{f.function}]",f"Line# {f.lineno}")
    print(f"########## {remark}")
    print('\u001b[32;1m') #Green
    return

####################################################################
def print_me(*args):
    print('\u001b[33;1m',args,'\u001b[32;1m')


####################################################################
####################################################################
def main_cli_entrypoint():

    # get all data from BV into dataframes
    if debug: trace_me(inspect.stack(),'main_cli_entrypoint()')
    if debug: print_me(type(sys.argv),sys.argv)
    if len(sys.argv) > 1:
        args=sys.argv
    else:
        args=None
    df_trades, df_wallet = asyncio.run(query_bv(uri, args))

    if debug: trace_me(inspect.stack(),'after query_bv()')

    if debug: trace_me(inspect.stack(),'df_trades.columns')
    if debug: print_me(df_trades.columns)
    
    r=['type', 'receivedCurrency',
                 'receivedAmount','priceCurrency', 'priceAmount',
                 'sentCurrency', 'sentAmount', 'feesCurrency', 'feesAmount']

    if debug: print_me(df_trades[r].head(10))

    df = group_tokens(df_trades)
    df.set_index('receivedCurrency', inplace=True)

    ######### manage fees    
    mtch = (df['feesCurrency']=='EUR') # handle fees / 6may2025
    df.loc[mtch, ['sentAmount+fees']] = (df.loc[mtch, ['sentAmount']].fillna(0).values + df.loc[mtch, ['feesAmount']].fillna(0).values)
    df.loc[mtch, ['receivedAmount+fees']] = (df.loc[mtch, ['receivedAmount']].fillna(0).values)
    
    mtch = (df['feesCurrency']!='EUR') # handle fees / 6may2025
    df.loc[mtch, ['sentAmount+fees']] = (df.loc[mtch, ['sentAmount']].fillna(0).values)
    df.loc[mtch, ['receivedAmount+fees']] = (df.loc[mtch, ['receivedAmount']].fillna(0).values + df.loc[mtch, ['feesAmount']].fillna(0).values)


    agginstruction = {'receivedAmount':'sum', 'receivedAmount+fees':'sum','sentAmount':'sum','sentAmount+fees':'sum','feesAmount':'sum'}
    #fmtinstruction = {'EUR(C-realized)':'{:.2f}', 'EUR(D-realized)':'{:.2f}','creditAmount':'{:.2f}'}

    r5=['type','receivedAmount','receivedAmount+fees', 'sentCurrency', 'sentAmount','sentAmount+fees', 'feesCurrency', 'feesAmount']
    df5 = df[r5].groupby('receivedCurrency').agg(agginstruction)

    if debug: trace_me(inspect.stack(),'df5.columns')
    if debug: print_me(df5.columns)

    r5=['receivedAmount+fees', 'sentAmount+fees', 'feesAmount']
    if debug: print_me('df5.len: ',len(df5))

    ############ ADD UNREALIZED ##############

    r5=['receivedAmount+fees', 'sentAmount+fees']
    df_bySymbol = pd.merge(df5, df_wallet, how='outer', left_index=True, right_on=['symbol'])
    #print_me(df_bySymbol.index)
    if df_bySymbol.index.name!='symbol':
        df_bySymbol.set_index(['symbol'], inplace=True)
    
    if debug: trace_me(inspect.stack(),'df_bySymbol.columns')
    if debug: print_me(df_bySymbol.index)
    if debug: print_me(df_bySymbol.columns)

    ############ RENAME ##############
    values={'receivedAmount+fees':'Token Balance', 'sentAmount+fees':'EUR(realized)'}
    df_bySymbol = df_bySymbol.rename(columns = values)


    t=['EUR(realized)','EUR(unrealized)']
    df_bySymbol['EUR(total)']=df_bySymbol[t].agg('sum',axis=1) #add column _total per symbol

    pd.options.display.float_format = '{:.2f}'.format
    if debug: trace_me(inspect.stack(),'end of rename')
    
    ############ ADD BE ##############
        
    df_bySymbol['|'] = "|"
    df_bySymbol_orders=df_bySymbol

    df_bySymbol['BE-price']  = (df_bySymbol.loc[ \
        (df_bySymbol['EUR(unrealized)'].notna())& \
        (df_bySymbol['price'].ne(0))& \
        (df_bySymbol['EUR(realized)'].lt(0)),'EUR(realized)'].div(df_bySymbol['Token Balance']).agg('abs')) #BE price new

    df_bySymbol['BE%'] = round(((df_bySymbol['BE-price']-df_bySymbol['price'])/(df_bySymbol['price']))*100,2) #% distance of current price away from Break even price (- means already in profit)
  
    if arguments.sort:
        use_sort=['symbol','EUR(total)','EUR(unrealized)','EUR(realized)']
    else:
        use_sort=['BE%','EUR(unrealized)','EUR(realized)']

    df_bySymbol=df_bySymbol.sort_values(by=use_sort)
    df_bySymbol.loc['_TOTALS']=df_bySymbol[t+['EUR(total)']].agg('sum') # add row totals for t


    ############ ADD IO (in_order vs total) ##############
     
    df_bySymbol_orders['IO%'] = round(df_bySymbol['Balance-inOrder']/df_bySymbol['Token Balance']*100,2) #% distance of current price away from Break even price (- means already in profit)    
    df_bySymbol_orders = df_bySymbol_orders.loc[df_bySymbol_orders['EUR(unrealized)'].notna()]

    if arguments.sort:
        use_sort=['symbol','IO%','EUR(unrealized)']
    else:
        use_sort=['EUR(unrealized)','IO%']
        use_sort=['IO%','EUR(unrealized)']

    df_bySymbol_orders=df_bySymbol_orders.sort_values(by=use_sort)
    df_bySymbol_orders.loc['_TOTALS']=df_bySymbol_orders[['EUR(unrealized)']].agg('sum') # add row totals for t



    if debug: trace_me(inspect.stack(),'df_bySymbol')
    r9=['Token Balance', 'EUR(realized)','EUR(unrealized)','EUR(total)','|','price','BE-price','BE%']
    if debug: print_me(df_bySymbol[r9])


    ######################## print it

    pd.set_option('expand_frame_repr', True)

    print('---------------------------------')
    print(6 * "\n")

    def txt_color_negative_red(x):
        if isinstance(x,float):
            r=x<0
            s=x>0
            t=x==0
            #print(r,s,t)
            if r:  x='\u001b[31;1m'+str(x)+'\u001b[37;1m'
            if s:  x='\u001b[32;1m'+str(x)+'\u001b[37;1m'
            if t:  x='\u001b[33;1m'+str(x)+'\u001b[37;1m'
        return x

    df_bySymbol_ur_txt = df_bySymbol.map(txt_color_negative_red)

    df_bySymbol_orders = df_bySymbol_orders.map(txt_color_negative_red)
    
    print('\u001b[32;1m') #Green
    print('\u001b[33;1m') #Yellow 
    print('\u001b[31;1m') #Red
    print('\u001b[37;1m') #White


    colnames=['Token Balance', 'EUR(realized)','EUR(unrealized)','EUR(total)','price','BE-price','BE%']
    numfmt=[".2f",".2f",".2f",".2f",".2f",".5f",".5f",".1f"]
    print(tabulate(df_bySymbol_ur_txt[colnames],headers=colnames,floatfmt=numfmt, tablefmt="simple_outline"))

    colnames=['Token Balance','Balance-inOrder','EUR(unrealized)','price','BE-price','BE%','IO%']
    numfmt=[".5f",".5f",".5f",".2f",".5f",".5f",".1f",".1f",]
    print(tabulate(df_bySymbol_orders[colnames],headers=colnames,floatfmt=numfmt, tablefmt="simple_outline"))




    exit()

####################################################################
####################################################################

if __name__ == "__main__":
    main_cli_entrypoint()

'''
python -m build --wheel
python -m twine upload dist/*
'''