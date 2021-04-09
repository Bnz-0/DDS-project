#!/bin/bash

if [[ $2 == "" ]]
then
	echo "Usage: makeStript.sh <file.sol> <contract name>"
	exit 1
fi

solc $1

if [[ $? -ne 0 ]]
then
	echo "Compilation failed"
	exit $?
fi

BIN=$(solc $1 --bin 2> /dev/null | tail -n 1)
ABI=$(solc $1 --abi 2> /dev/null | tail -n 1)

echo Abi: $ABI
echo Binary: $BIN

# ABI
cat > $2.abi << EOF
var ${2}Contract = eth.contract($ABI)
EOF

# BIN
cat > $2.bin << EOF
personal.unlockAccount(eth.accounts[0])
var $2 = ${2}Contract.new({
	from: eth.accounts[0],
	data: "0x$BIN",
	gas: 500000,
})
EOF
