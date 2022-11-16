import requests
import json
import hashlib
import multiprocessing
from multiprocessing import Process, Value

# Compute the hash given a blob and miner id
def runblob(blob, lasthash):
  mid = 'be8a151b34eb633f052bb4725d307992607eb5ca5ecf938e18357858a8fd654b'
  string = 'CPEN 442 Coin2022'+ lasthash + blob + mid
  return hashlib.sha256(string.encode('utf-8')).hexdigest()

def submit_blob(blob, prev):
  result = json.dumps({"coin_blob": blob,
    "id_of_miner": 'be8a151b34eb633f052bb4725d307992607eb5ca5ecf938e18357858a8fd654b',
    "hash_of_last_coin": prev})
  hdr = {'Content-type': 'application/json'}
  return requests.post('http://cpen442coin.ece.ubc.ca/claim_coin', data=result, headers=hdr)

# textgen() generates string given a number works in base 36
def textgen(inputInt):
  ret = ''
  inputInt += 1
  while(inputInt > 0):
    n = inputInt % 96
    ret = chr(n+31) + ret
    inputInt = inputInt // 96
  return ret

def FindCollision(procnum, proccount, diff, lasthash, v, interval):
    rt = procnum * interval
    while(1):
      lasthash = requests.post("http://cpen442coin.ece.ubc.ca/last_coin").json()['coin_id']
      print('Starting ' + str(diff) + ' on ' + lasthash)
      for i in range(interval):
        string = textgen(rt + i)
        hash = runblob(string, lasthash)
        if hash[:diff] == '0' * diff:
            status = submit_blob(textgen(rt + i), lasthash)
            print (status.json())
      print('batch ' + str(rt) + '-' + str(rt + interval) + ' checked')
      rt += interval*(proccount-1) 
      diff = requests.post("http://cpen442coin.ece.ubc.ca/difficulty").json()['number_of_leading_zeros']
      lasthash = requests.post("http://cpen442coin.ece.ubc.ca/last_coin").json()['coin_id']
      print('Starting ' + str(diff) + ' on ' + lasthash)

if __name__ == "__main__":
    manager = multiprocessing.Manager()
    numcpu = multiprocessing.cpu_count()
    # determines how much a process should work on at a time (batch)
    intrvl = 10000000
    # prints number of CPUs available
    print (numcpu)
    v = manager.Value('i', 0)
    procs = []
    diff = requests.post("http://cpen442coin.ece.ubc.ca/difficulty").json()['number_of_leading_zeros']
    lasthash = requests.post("http://cpen442coin.ece.ubc.ca/last_coin").json()['coin_id']
    for i in range(numcpu):
        proc = Process(target=FindCollision, args=(i, numcpu, diff, lasthash, v, intrvl))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()
    print(textgen(v.value))
