import sys
import json
from web3 import Web3
from web3.exceptions import ContractLogicError

ABI = json.load(open("truffle-election/build/contracts/Election.json",'r'))['abi']
USAGE="""
|￣￣￣￣￣￣￣￣￣￣￣￣￣|
|          Usage:          |
|   account <Nº account>   |
|       vote <party>       |
|      status <party>      |
| use <contract's address> |
|＿＿＿＿＿＿＿＿＿＿＿＿＿|
      (\__/) ||
      (•ㅅ•) ||
      / 　 づ||
"""
TYPO="""
  ⠀⠀⠀⠀⣠⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⣼⡟⠉⠉⠀⠀⠀⠀⢀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⢿⣇⠀⠀⠀⠀⣠⣶⣿⠿⣿⣿⡿⣷⡀⠸⣿⣶⡀
  ⠀⠀⠀⠘⢿⣆⠀⣠⣾⣿⣿⣿⣶⣿⣿⣶⣿⠁⠀⣠⣿⡇
  ⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢛⣁⣤⣴⣿⠟⠁
  ⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠋⠁⠀⠀
  ⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀
  ⠀⠀⠀⠀⣿⣿⡟⠉⠉⠀⠀⠈⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⢸⣿⣿⠁⠀⠀⠀⠀⠀⢻⣿⣿⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⣾⣿⠇⠀⠀⠀⠀⠀⠀⠀⢿⣿⠀⠀⠀⠀⠀⠀⠀
  ⠀⠀⠀⠹⢿⠁ ⠀⠀⠀⠀⠀⠀⠸⣿⣶⡄⠀⠀⠀⠀⠀
  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀
  Better u stop do typos!
"""


local_node = sys.argv[1] if len(sys.argv) > 1 else "HTTP://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(local_node))

if w3.isConnected(): print("Connected!")
else:
	print(f"No local node found at {local_node}")
	sys.exit(0)

w3.eth.defaultAccount = w3.eth.accounts[0]
print("Account in use:", w3.eth.defaultAccount)
contract = None

while True:
	cmd = input('> ').split(' ')
	try:
		if cmd[0] == "q": break
		if cmd[0] == "help":
			print(USAGE)
		elif cmd[0] == "account":
			# cmd[1] = number of account
			w3.eth.defaultAccount = w3.eth.accounts[int(cmd[1])]
			print("Account in use:", w3.eth.defaultAccount)
		elif cmd[0] == "vote":
			# cmd[1] = name of the party
			try:
				if contract is None:
					print("No contract in use")
				elif contract.functions.hasVoted(w3.eth.defaultAccount).call():
					print("You have already voted")
				elif contract.functions.vote(cmd[1]).call(): # guard to avoid spending gas if something is wrong
					contract.functions.vote(cmd[1]).transact()
			except ContractLogicError as e:
				print(e)
		elif cmd[0] == "status":
			# cmd[1] = name of the party
			if contract is None:
				print("No contract in use")
			else:
				status = contract.functions.parties(cmd[1]).call()
				print(status)
		elif cmd[0] == "use":
			# cmd[1] = address of the contract
			contract = w3.eth.contract(address=cmd[1], abi=ABI)
			print("Contract in use:", contract.functions.name().call())
		elif cmd[0] != "":
			print(TYPO)
	except Exception as e:
		print("Exception:", e)
		print(USAGE)
