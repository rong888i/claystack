from web3 import Web3, HTTPProvider
from time import sleep
from web3.middleware import geth_poa_middleware


class EthHandler:
    def __init__(self, rpc=None, Contract_Add=None, abi=None, key=None):
        self.web3 = Web3(HTTPProvider(rpc))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        # 检查是否连接成功
        if not self.web3.isConnected():
            print(f"RPC {rpc} False")
            exit()
        else:
            print(f"RPC {rpc} True")
            acct = self.web3.eth.account.privateKeyToAccount(key)
            self.key = key
            self.my_address = acct.address
            if Contract_Add is not None and abi is not None:
                self.contract = self.web3.eth.contract(address=self.ca(Contract_Add), abi=abi)

    def ca(self, address):
        if self.web3.isChecksumAddress(address):
            return address
        else:
            return self.web3.toChecksumAddress(address)

    def getUserStart(self):
        self.contract.functions.getUserStart(self.my_address).call()

    def getNextClaim(self):
        nexttime = self.contract.functions.userNextClaim(self.my_address).call()
        if nexttime[1] != 1:
            print("未到收集时间", self.my_address, nexttime[0])
        return nexttime[1]

    def get_sign(self):
        txn = self.contract.functions.package().buildTransaction({
            'nonce': self.web3.eth.getTransactionCount(self.my_address),
            'gas': 500000,
            'gasPrice': self.web3.eth.gas_price,
        })
        signed_txn = self.web3.eth.account.sign_transaction(
            txn,
            self.key
        )
        txn = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        txn_receipt = self.web3.eth.waitForTransactionReceipt(txn)
        if txn_receipt["status"] == 1:
            return True, self.my_address
        else:
            return False, self.my_address


rpc = 'https://eth-goerli.alchemyapi.io/v2/OePDKEAtMy2lr5W5J8aBCML6qYmeCaFX'
Contract_address = "0x7b067b776dec24cf0c2390e76dea20217e75d9f7"
abi = open(r"D:\python\claystack.json", "r").read()  # abi路径
key = {
}  # key

while True:
    for keys in key:
        eth = EthHandler(rpc=rpc, Contract_Add=Contract_address, abi=abi, key=keys)
        eth.getUserStart()
        claim = eth.getNextClaim()
        if claim == 0:
            print("收集", eth.get_sign())
    sleep(60 * 30)
