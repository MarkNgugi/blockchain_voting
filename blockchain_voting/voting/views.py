from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from web3 import Web3
from django.conf import settings

# Connect to Ganache
ganache_url = settings.GANACHE_URL
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check if connected
if not web3.is_connected():
    print("Failed to connect to the blockchain")

# Replace with your actual contract address and ABI
contract_address = "0x5375C0FfC336bEB0daa9000bc570fcbD51123912"
abi = [
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "candidates",
        "outputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "uint256", "name": "voteCount", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True,
    },
    {
        "inputs": [],
        "name": "candidatesCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
        "constant": True,
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "hasVoted",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
        "constant": True,
    },
    {
        "inputs": [{"internalType": "string", "name": "_name", "type": "string"}],
        "name": "addCandidate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_candidateId", "type": "uint256"}],
        "name": "vote",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

contract = web3.eth.contract(address=contract_address, abi=abi)

def home(request):
    candidates = []
    try:
        # Fetch the list of candidates dynamically from the contract
        candidates = [
            {
                'id': candidate[0],
                'name': candidate[1],
                'voteCount': candidate[2],
            }
            for candidate in [
                contract.functions.candidates(i + 1).call()
                for i in range(contract.functions.candidatesCount().call())
            ]
        ]
        print(f"Fetched Candidates: {candidates}")
    except Exception as e:
        print(f"Error fetching candidates: {e}")

    if request.method == "POST":
        candidate_id = int(request.POST.get("candidate_id"))
        sender_address = "0x6C970697e442DDC740031DC953eb97c66ef03B7e"
        private_key = "0x37cdfee4c2cdc346560fc34a79c51a462533e9758c6289490b9b305492be3339"
        
        # Build the transaction for voting
        nonce = web3.eth.get_transaction_count(sender_address)
        tx = contract.functions.vote(candidate_id).build_transaction({
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei'),
        })
        
        # Sign the transaction
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        
        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for the transaction receipt to confirm the vote
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt['status'] == 1:
            print("Vote successfully casted!")
        else:
            print("Transaction failed!")

        return HttpResponseRedirect(reverse('home'))

    return render(request, 'voting/home.html', {'candidates': candidates})





def admin_panel(request):
    if request.method == "POST":
        candidate_name = request.POST.get("candidate_name")
        
        # Replace with appropriate sender address and private key
        sender_address = "0x6C970697e442DDC740031DC953eb97c66ef03B7e"  # The address from which the transaction will be sent
        private_key = "0x37cdfee4c2cdc346560fc34a79c51a462533e9758c6289490b9b305492be3339"  # The private key for signing the transaction
        
        # Debugging prints
        print("Web3 Connection: ", web3.is_connected())
        print("ETH Interface: ", web3.eth)

        # Ensure connection to blockchain is established and eth object is available
        if not web3.is_connected():
            return HttpResponseRedirect(reverse('home'))

        # Build the transaction for adding a candidate
        nonce = web3.eth.get_transaction_count(sender_address)  # Correct method name
        transaction = contract.functions.addCandidate(candidate_name).build_transaction({
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei'),  # Corrected method name
        })
        
        # Sign the transaction with the private key
        signed_tx = web3.eth.account.sign_transaction(transaction, private_key)  # Corrected method name
        
        # Send the signed transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)  # Corrected attribute name
        
        # Wait for the transaction receipt (confirmation) - Correct method name
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction Receipt:", receipt)
        
        # Redirect after adding the candidate
        return HttpResponseRedirect(reverse('home'))  # Redirect to home to see the updated list
    
    return render(request, 'voting/admin.html')







