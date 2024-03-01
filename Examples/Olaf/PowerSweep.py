import os
import datetime
import time
import asyncio
import pandas as pd
import numpy as np
import csv

from pylab import *

import sys
sys.path.append("../../Devices/Lakeshore")

from Lakeshore372 import LS372
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp import auth

from dotenv import load_dotenv

# Read in user / router details
load_dotenv()

csv_path = None

USER = "API_Controller_1"
USER_SECRET = "critical91"
url = "ws://smf-ox1.slac.stanford.edu:8080/ws"
realm = "ucss"

temperature_control_devices = ['DRI_CLD_S', 'DRI_MIX_CL.DRI_MIX_S', 'DRI_PT1_S', 'DRI_PT2_S', 'DRI_STL_S', 'PTR1_PT1_S',
                               'PTR1_PT2_S']
pressure_control_devices = ['3CL_PG_01', '3CL_PG_02', '3CL_PG_03', '3CL_PG_04', '3CL_PG_05', '3CL_PG_06', '3SP_PG_01']
heater_devices = ['DRI_MIX_CL.DRI_MIX_H', 'DRI_STL_H']

def getChannelSettings(minChan, maxChan):
    
    lakeshore = []
    
    for i in range(minChan, maxChan+1):
        chan = ls.channels[i]
        lakeshore.append(chan.get_resistance_reading())
        lakeshore.append(chan.get_excitation_power())    
    
    return lakeshore

class Component(ApplicationSession):
    """
    An application component that connects to a WAMP realm.
    """

    def onConnect(self):
        print("Client session connected.")
        print()
        print("Starting WAMP-CRA authentication on realm '{}' as user '{}'.".format(self.config.realm, USER))
        print()
        self.join(self.config.realm, ["wampcra"], USER)

    def onChallenge(self, challenge):
        if challenge.method == "wampcra":
            print("WAMP-CRA challenge received: {}".format(challenge))
            print()

            if 'salt' in challenge.extra:
                # salted secret
                key = auth.derive_key(USER_SECRET,
                                      challenge.extra['salt'],
                                      challenge.extra['iterations'],
                                      challenge.extra['keylen'])
            else:
                # plain, unsalted secret
                key = USER_SECRET

            # compute signature for challenge, using the key
            signature = auth.compute_wcs(key, challenge.extra['challenge'])

            # return the signature to the router for verification
            return signature

        else:
            raise Exception("Invalid authmethod {}".format(challenge.method))

    async def onJoin(self, details):

        global procedure
        global oxford
        
        global POWER_STEPS
        global TERMINATE
        global POWER
        global COUNTER
        
        
        self.start = time.time()
        print(f' ---------- Time at join: {self.start} ------------')

        ## Who is in control?
        controller = await self.call('oi.decs.sessionmanager.system_controller')
        if procedure == 'sweep':            
            try:            
                if controller.results[-1] == "":
                    await self.call(f'oi.decs.sessionmanager.claim_system_control')
                    controller = await self.call('oi.decs.sessionmanager.system_controller')
                    print(f'Switched control to {controller.results[-1]}')
                elif controller.results[-1] == "API_Controller_1":
                    print('Currently controlling remote interface...')
                else:
                    print('ERROR: Remote interface in manual control state, relinquish control to resume automatic procedure')
                    TERMINATE = True
                    self.leave()

                current_power = await self.call(f'oi.decs.temperature_control.DRI_MIX_CL.DRI_MIX_H.power')
                previous_call = await self.call('oi.decs.temperature_control.DRI_MIX_CL.DRI_MIX_H.power')

                print(f'Current power of mixing stage: {current_power.results[-2]} uW')

                resp = await self.call('oi.decs.temperature_control.DRI_MIX_CL.DRI_MIX_H.power', POWER, 1)
                print(f'Setting MIX heater to {POWER * 1e6} uW')
                print(resp.results)
            
            except Exception as e:
                print("Error: {}".format(e))

        elif procedure == 'log':
            print("-- Scanning all devices: --")
            for i, device in enumerate(temperature_control_devices[:-1]):
                try:
                    resp = await self.call(f'oi.decs.temperature_control.{device}.temperature')
                except Exception as e:
                    print("Error: {}".format(e))
                except KeyboardInterrupt:
                    print('Interrupted manually')
                else:
                    print(f'Current temperature for {device}: {resp.results[-2]}')
                    oxford.append(resp.results[-2])
            
            for i, device in enumerate(heater_devices):
                try:
                    resp = await self.call(f'oi.decs.temperature_control.{device}.power')
                except Exception as e:
                    print("Error: {}".format(e))
                except KeyboardInterrupt:
                    print('Interrupted manually')
                else:
                    print(f'Current power for {device}: {resp.results[-4]}')
                    oxford.append(resp.results[-4])
            
            for i, device in enumerate(pressure_control_devices):
                try:
                    resp = await self.call(f'oi.decs.proteox.{device}.pressure')
                except Exception as e:
                    print("Error: {}".format(e))
                except KeyboardInterrupt:
                    print('Interrupted manually')
                else:
                    print(f'Current pressure for {device}: {resp.results[-2]}')
                    oxford.append(resp.results[-2])


        self.leave()

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


if __name__ == '__main__':
      
    ls = LS372('192.168.1.144')

    if csv_path == None:
        date = str(datetime.datetime.now().date()).replace('-', '')
        csv_path = f'{date}_log_scan.csv'

    if not os.path.isfile(csv_path):
        df = pd.DataFrame(columns=['Time'] + temperature_control_devices + pressure_control_devices + heater_devices + list(np.array([[f'R{i}', f'P{i}'] for i in range(1, 17)]).flatten()))
        df.to_csv(csv_path, header=True, index=False)
    
    procedure = 'None'

    POWER_STEPS = np.concatenate([np.arange(8, 32, 2), np.arange(30, 6, -2), np.array([0])]) * 1e-6
    COUNTER = 0
    TERMINATE = False
    
    log_previous = 0
    sweep_previous = 0
    
    try:
        
        while True:

            if TERMINATE != True:
                if time.time() - sweep_previous >= 900:
                    procedure = 'sweep'
                    if COUNTER >= len(POWER_STEPS):
                        TERMINATE = True 
                        procedure = 'None'
                        print('SWEEP COMPLETE')
                    else:   
                        POWER = POWER_STEPS[COUNTER]
                        runner = ApplicationRunner(url, realm)
                        runner.run(Component)
                        
                        sweep_previous = time.time()
                        COUNTER += 1 
                        print(f'COUNTER: {COUNTER}')

                        procedure = 'None'
                     
            if time.time() - log_previous >= 30:
                procedure = 'log'
                oxford = []

                lakeshore = getChannelSettings(1,16)

                runner = ApplicationRunner(url, realm)
                runner.run(Component)

                data = [time.time()]

                with open(csv_path, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    for i in oxford:
                        data.append(i) 
                    for j in lakeshore:
                        data.append(j)
                    
                    writer.writerow(data)
                    csvfile.close()

                log_previous = time.time()
                procedure = 'None'
    
    except Exception as e:
        print("Error: {}".format(e))
        print('Aborted')

    except KeyboardInterrupt:
        print('Manually interrupted...')
        print('Aborted')

    else:
        print(' ------------------------- \n\n')
        print(f'All temperature values written to {csv_path}...')