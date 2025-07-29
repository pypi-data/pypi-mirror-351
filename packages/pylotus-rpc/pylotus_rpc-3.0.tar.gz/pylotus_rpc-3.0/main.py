import os
from pylotus_rpc import HttpJsonRpcConnector
from pylotus_rpc import LotusClient
from pylotus_rpc.types.message import Message
from pylotus_rpc.types.sector_pre_commit_info import SectorPreCommitInfo
from pylotus_rpc.util.sector_util import decode_sectors
from decimal import Decimal
from pylotus_rpc.types.cid import Cid
from pylotus_rpc.types.block_messages import BlockMessages
import json
from pprint import pprint
from typing import List


# test for environment variable
#if os.environ.get('LOTUS_RPC_TOKEN') is None:
#    print("Please set the environment variable LOTUS_RPC_TOKEN")
#    exit(1)

# LOTUS_RPC_TOKEN = os.environ.get('LOTUS_RPC_TOKEN')

# host = "https://node.filutils.com/rpc/v1"


# this works for list_state_actors
host = "https://filfox.info/rpc/v0"

# host = "https://rpc.ankr.com/filecoin"
# host = "https://filecoin.chainup.net/rpc/v1"
# host = "https://api.node.glif.io"

# connector = HttpJsonRpcConnector(host="http://lotus.filforge.io:1234/rpc/v0", api_token=LOTUS_RPC_TOKEN)
connector = HttpJsonRpcConnector(host=host)
client = LotusClient(connector)

good_msg = Message(
    version=0,  # Always 0 for now, as per Filecoin protocol
    to_addr="f086971",  # Destination address
    from_addr="f01986715",  # Source address
    nonce=5,  # Assume this sender has sent 4 messages previously, so this is the 5th message.
    value=10**19,  # Transfer 10 FIL (as attoFIL)
    gas_limit=1000000,  # A generous gas limit; in practice, one should estimate this
    gas_fee_cap=1,  # Maximum price per gas unit this sender is willing to pay
    gas_premium=5,  # Willing to pay half of GasFeeCap as a premium for faster inclusion
    method=0,  # Method 0 is a simple fund transfer in Filecoin
    params=""  # No params needed for simple transfers
)    

good_msg2 = Message(
    version=0,  # Always 0 for now, as per Filecoin protocol
    to_addr="f086971",  # Destination address
    from_addr="f01986715",  # Source address
    nonce=7,  # Assume this sender has sent 4 messages previously, so this is the 5th message.
    value=10**19,  # Transfer 10 FIL (as attoFIL)
    gas_limit=1000000,  # A generous gas limit; in practice, one should estimate this
    gas_fee_cap=1,  # Maximum price per gas unit this sender is willing to pay
    gas_premium=5,  # Willing to pay half of GasFeeCap as a premium for faster inclusion
    method=0,  # Method 0 is a simple fund transfer in Filecoin
    params=""  # No params needed for simple transfers
)    


# JSON string
spci_json_str = '''
{
    "SealProof": 8,
    "SectorNumber": 9,
    "SealedCID": {
      "/": "bafy2bzacea3wsdh6y3a36tb3skempjoxqpuyompjbmfeyf34fi3uy6uue42v4"
    },
    "SealRandEpoch": 10101,
    "DealIDs": [
      5432
    ],
    "Expiration": 10101,
    "ReplaceCapacity": true,
    "ReplaceSectorDeadline": 42,
    "ReplaceSectorPartition": 42,
    "ReplaceSectorNumber": 9
}
'''



# test net.connect
#result = client.Net.connect("12D3KooWGzxzKZYveHXtpG6AsrUJBcWxHBFS2HsEoGTxrMLvKXtf", ["/ip4/52.36.61.156/tcp/1347/p2p/12D3KooWFETiESTf1v4PGUvtnxMAcEFMzLZbJGg4tjWfGEimYior"])
# print(result)

# test net.block_remove
# result = client.Net.block_remove(ip_addrs=["127.0.0.1"])
# print(result)

# test net.block_list
#result = client.Net.block_list()
#pprint(result)

# test net.block_add
# result = client.Net.block_add(ip_addrs=["127.0.0.1"])
# print(result)

# test net.bandwidth_stats_by_protocol
#result = client.Net.bandwidth_stats_by_protocol()
#pprint(result)

# test net.bandwidth_stats_by_peer
# result = client.Net.bandwidth_stats_by_peer()
#pprint(result)

# test net.bandwidth_stats
# result = client.Net.bandwidth_stats()
# pprint(result)


# test net.auto_nat_status
# result = client.Net.auto_nat_status()
# pprint(result)

# test net.limit
#result = client.Net.limit("system")
#print(result)

# test net.stat
result = client.Net.stat("system")
pprint(result)

# test net.set_limit
#result = client.Net.set_limit("system", {"Memory": 1024 * 1024 * 1024, "Streams": 100})
#print(result)

# test net.pubsub_scores
#result = client.Net.pubsub_scores()
#pprint(result)

exit(0)

#test net.peers and net.connectedness and net.find_peer and net.peer_info
peers = client.Net.peers()
print(f"Got {len(peers)} peers")
# list the first 10 peers
for peer in peers[:2]:
    pprint(peer)
    result = client.Net.connectedness(peer.peer_id)
    print(f"Connectedness: {result}")
    result = client.Net.find_peer(peer.peer_id)
    print(f"Find Peer: {result}")
    result = client.Net.peer_info(peer.peer_id)
    print(f"Peer Info: {json.dumps(result, indent=4)}")
    result = client.Net.ping(peer.peer_id)
    print(f"Ping: {result}")
    result = client.Net.protect_add([peer.peer_id])
    print(f"Protect Add: {result}")


#  test net.agent_version
# version = client.Net.agent_version(peers[0].peer_id)
# print(version)

# test net.addrs_listen
# address_info = client.Net.addrs_listen()
# pprint(address_info)

# test chain.tip_set_weight
# tipset_key = client.Chain.head().get_tip_set_key()
# result = client.Chain.tip_set_weight(tipset_key)
# print(result)

# test chain.stat_obj, unable to test this, always gets a 504 error
# obj = Cid("bafy2bzacecwoxkpupvxhxjlz7yaibod7nsxqofxqcnvzefjtkqmdgpsurlm4c")
#result = client.Chain.stat_obj(obj)
#print(result)

# test chain.set_head
# tipset = client.Chain.get_chain_head()
# client.Chain.set_head(tipset)

# result = client.Chain.has_obj("bafy2bzaceawwl2d3byzcijj4arjwxnzawnuhlc4qn5gwuhagc4yzpntffomp6")
#print(result)

# tipset = client.Chain.get_chain_head()
# result = client.Chain.get_randomness_from_tickets(2, 10101, "Ynl0ZSBhcnJheQ==", tipset=tipset)
# print(result)

# test ChainGetRandomnessFromBeacon
# tipset = client.Chain.get_chain_head()
# result = client.Chain.get_randomness_from_beacon(2, 10101, "Ynl0ZSBhcnJheQ==", tipset=None)
# print(result)

# test ChainGetRandomnessFromTickets
# tipset = client.Chain.get_chain_head()
# result = client.Chain.get_randomness_from_tickets(2, 10101, "Ynl0ZSBhcnJheQ==", tipset=None)
# print(result)

# test ChainGetPath
# end_tipset = client.Chain.get_chain_head()
# start_tipset = client.Chain.get_tipset_by_height(end_tipset.height - 3)
# lst_head_changes = client.Chain.get_path(start_tipset.get_tip_set_key(), end_tipset.get_tip_set_key())
# print(f"Got {len(lst_head_changes)} head changes")

# test ChainGetTipSetByHeight
# start_tipset = client.Chain.get_tipset_by_height(end_tipset.height - 3)
# print(start_tipset.height)


# test ChainGetParentReceipts
# test_cid = "bafy2bzaceawwl2d3byzcijj4arjwxnzawnuhlc4qn5gwuhagc4yzpntffomp6"
# lst_receipts = client.Chain.get_parent_receipts(test_cid)
# print(f"Got {len(lst_receipts)} receipts")

# test ChaingGetParentMessages
# test_block = "bafy2bzaceawwl2d3byzcijj4arjwxnzawnuhlc4qn5gwuhagc4yzpntffomp6"
# lst_wrapped_messages = client.Chain.get_parent_messages(test_block)
# print(f"Got {len(lst_wrapped_messages)} wrapped messages")

# test StateGetRandomnessFromBeacon
# result = client.State.get_randomness_from_beacon(2, 10101, "Ynl0ZSBhcnJheQ==", tipset=None)
# print(result)

# test StateGetRandomnessFromTickets
# result = client.State.get_randomness_from_tickets(2, 10101, "Ynl0ZSBhcnJheQ==", tipset=None)
# print(result)

# test Filecoin.ChainExport
# tipset = client.Chain.get_chain_head()
# client.Chain.export(1, True, tipset.get_tip_set_key())

# test ChainDeleteObj
# tipset = client.Chain.get_chain_head()
# first_block_header = tipset.blocks[0]
# messages_cid = first_block_header.messages
# client.Chain.delete_obj(messages_cid.id)

# test ChainGetNode
# tipset = client.Chain.get_chain_head()
# actor = client.State.get_actor("f05", tipset=tipset)
# define the node selector path
# node_selector = f"{actor.head.id}/6"
# dict = client.Chain.get_node(node_selector)
# pprint(dict)

# get ChainGetMessagesInTipset
# head_tip_set = client.Chain.get_chain_head()
# messages = client.Chain.get_messages_in_tipset(head_tip_set.get_tip_set_key())
# pprint(messages)

# test ChainGetMessage
# get the tip set
# head_tip_set = client.Chain.get_chain_head()
# get the cid to that blocks messages
# first_block_cid = head_tip_set.cids[0]
# get the block messages
# block_messsages = client.Chain.get_block_messages(first_block_cid.id)
# in reality this is redundant because we already have the messages, but we're just testing here
# message_cid = block_messsages.cids[0].id
# message = client.Chain.get_message(message_cid.id)
# pprint(message)

# message = client.Chain.get_message("bafy2bzacecra2yhbpdinpcclshzemc4shv5ydv2h2j3kffivrg2klla3ejjaq")
# pprint(message)

# test ChainGetGenesis
# genesis_tipset = client.Chain.get_genesis()

# Test ChainGetBlockMessages
# tipset = client.Chain.get_chain_head()
#first_block_cid = tipset.cids[0]
# block_messsages = client.Chain.get_block_messages(first_block_cid.id)
# pprint(block_messsages)


# pprint(tipset.lst_dct_cids())

# test StateWaitMsgLimited
#result = client.State.wait_msg_limited("bafy2bzacecxnn5axzy3vvzwounoygubhbydfvfh5bopdhwoc5lfi6itwgj5tw", 0, 100000)
#pprint(result)


# # test StateWaitMsg
# result = client.State.wait_msg("bafy2bzacecxnn5axzy3vvzwounoygubhbydfvfh5bopdhwoc5lfi6itwgj5tw", 0)
# pprint(result)

# test VerifiedRegistryRootKey
# result = client.State.verified_registry_root_key()
# print(result)

# test VerifiedClientStatus
# client_address = "f1ynv3f5ne5k7xxr7z5q7coro7rqpls3ilhuz3ndy"
# client_id = "f02828410"
# int_datacap = client.State.verified_client_status(client_address, tipset=None)
# print(f"Client {client_address} has Datacap {int_datacap}")

# test StateVmCirculatingSupplyInternal
# result = client.State.vm_circulating_supply_internal()
# print(json.dumps(result, indent=4))

# test StateSectorPreCommitInfo
# try:
#     # get the partitions for a miner at deadline 0
#     partitions = client.State.miner_partitions("f030125", 1)
#     # get the first sector from the first partition
#     first_sector = partitions[0].recovering_sectors[0]
#     sector_pc_info = client.State.sector_pre_commit_info("f030125", first_sector)
#     pprint(sector_pc_info)
# except Exception as e:
#     print(f"sector info not found: {e}")

# test StateSectorPartition
# try:
#     # get the partitions for a miner at deadline 0
#     partitions = client.State.miner_partitions("f030125", 1)
#     # get the first sector from the first partition
#     first_sector = partitions[0].active_sectors[0]
#     sector = client.State.sector_partition("f030125", first_sector)
#     print(json.dumps(sector, indent=4))
# except Exception as e:
#     print(f"sector not found: {e}")

# # test StateSectorGetInfo
# try:
#     # get the partitions for a miner at deadline 0
#     partitions = client.State.miner_partitions("f030125", 0)
#     # get the first sector from the first partition
#     first_sector = partitions[0].active_sectors[0]
#     sector = client.State.sector_get_info("f030125", first_sector)
#     pprint(sector)
# except Exception as e:
#     print(f"sector not found: {e}")

# test StateSectorExpiration
# try:
#     # get the partitions for a miner at deadline 0
#     partitions = client.State.miner_partitions("f030125", 0)
#     # get the first sector from the first partition
#     first_sector = partitions[0].active_sectors[0]
#     dct_expiration = client.State.sector_expiration("f030125", first_sector)
#     print(f"sector: {first_sector} expiration: {dct_expiration}")
# except Exception as e:
#     print(f"sector not found: {e}")
  

# test SearchMessageLimited
# result = client.State.search_message_limited("bafy2bzaceasvnmajn6e76xgnk42fco5tkwbg56hue5xy3kgbf4kbxh3g7kzei", 3677894)
# pprint(result)

# test SearchMessage
#result = client.State.search_message("bafy2bzaceasvnmajn6e76xgnk42fco5tkwbg56hue5xy3kgbf4kbxh3g7kzei")
# pprint(result)

# test StateReplay
# result = client.State.replay("bafy2bzaceasvnmajn6e76xgnk42fco5tkwbg56hue5xy3kgbf4kbxh3g7kzei", tipset=None)
# pprint(result)

# test NetworkVersion
#result = client.State.network_version()
#print(result)

# test NetworkName
# result = client.State.network_name()
# print(result)

# test MinerSectors
# result = client.State.miner_sectors("f01852677", [1, 2, 3], tipset=None)
# print(result)

# test MinerSectorCount
# result = client.State.miner_sector_count("f01852677", tipset=None)
# print(result)

# test MinerSectorAllocated
# result = client.State.miner_sector_allocated("f01852677", 1, tipset=None)
# print(result)

# test MinerRecoveries
# result = client.State.miner_recoveries("f01852677", tipset=None)
# print(result)

# test MinerProvingDeadline
# result = client.State.miner_proving_deadline("f01852677", tipset=None)
# print(result)

# test _miner_pre_commit_deposit_for_power
#sector_pre_commit_info = SectorPreCommitInfo.from_json(spci_json_str)
#result = client.State.miner_pre_commit_deposit_for_power("f01852677", sector_pre_commit_info, tipset=None)
# print(result)

# test StateMinerPower
# result = client.State.miner_power("f01852677", tipset=None)
# print(result)

# test StateMinerPartitions
# lst_partitions = client.State.miner_partitions("f01852677", 1, tipset=None)
# print(len(lst_partitions))

# test StateMinerInitialPledgeCollateral
#sector_pre_commit_info = SectorPreCommitInfo.from_json(spci_json_str)
#result = client.State.miner_initial_pledge_collateral("f01852677", sector_pre_commit_info, tipset=None)
#print(result)

# test StateMinerInfo
#result = client.State.miner_info("f01852677", tipset=None)
# print(result)

# test StateMinerFaults
# result = client.State.miner_faults("f01852677", tipset=None)
# pprint(result)

# test MinerDeadlines
#result = client.State.miner_deadlines("f01852677", tipset=None)
#for deadline in result:
#    print(f"Post Submissions {deadline.post_submissions} and Disputable Proof Count {deadline.disputable_proof_count}") 


# test MinerAvailableBalance
# result = client.State.miner_available_balance("f02244985", tipset=None)
# print(f"Miner Available Balance {result}")

# test MinerActiveSectors
# result = client.State.miner_active_sectors("f02244985", tipset=None)
# print(len(result))

# test StorageMarketDeal
# result = client.State.storage_market_deal(68901592, tipset=None)
# print(result)

# test StateMarketParticipants
#result = client.State.market_participants(tipset=None)
#print(f"Market Participants {len(result)}")

# test StateMarketDeals
# result = client.State.market_deals(tipset=client.Chain.get_chain_head())
# print(f"Market Deals {result}")

# test StateMarketBalance
# result = client.State.market_balance("f02620", tipset=None)
# print(f"Market Balance {result}")

# test StateLookupID
# results = client.State.lookup_id("f1gdqsyh2twcmimfujjkgajqccx6v4bbywy33xpuq", tipset=None)
# print(results)

# test StateListMiners
#results = client.State.list_miners(tipset=None)
# print(f"Got {len(results)} miners")

# test ListMessages
#tip_set = client.Chain.get_chain_head()
#client.State.list_messages("f05", None, tip_set.height, tipset=tip_set)


# test StateReadState
# result = client.State.read_state("f05", tipset=None)
#lt_cid = Cid.from_dict(result.state['LockedTable'])
# cbor_obj = client.Chain.read_obj(lt_cid.id)
# print(cbor_obj)

# test StateGetRandomnessFromBeacon
# result = client.State.get_randomness_from_beacon(2, 10101, "Ynl0ZSBhcnJheQ==", tipset=None)
# print(result)

# test decode_params
# lst_messages  = [good_msg, good_msg2]
# client.State.decode_params("f05", 6, "goEaA5wJ/BoASmsX")
# client.State.decode_params("f2kemhdxzy6lc2zt2c7gzr6h5d3mlurcbllfodqyq", 3, "ghibQA==")

# test deal_provider_collateral_bounds
# [min, max] = client.State.deal_provider_collateral_bounds(34359738368, True, None)
# print(f"min {min} and max {max} ATTOFIL")

# state_compute_testing
# state_compute_output = client.State.state_compute(tipset.height, lst_messages, tipset=tipset)
#print(state_compute_output.root)
# print(f"Got {len(state_compute_output.trace)} invocation results")

# testings circ supply
#supply = client.State.circulating_supply()
#print(f"Circulating Supply in attoFil {supply}")

# testing changed_actors
# cid1 = "bafy2bzacedbc3m6k3q36p2uzrxc776u4ebexmtqz7mq65fgdnwuc5wukyygx6"
# cid2 = "bafy2bzacebr4rqbdsm4xiba24cpx3tzf2mcdhny7qbhw5pjs773rbpa5yxpyw"

# blockheader1 = client.Chain.get_block(cid1)
# blockheader2 = client.Chain.get_block(cid2)
# root1 = blockheader1.parent_state_root
# root2 = blockheader2.parent_state_root
# lst_actors = client.State.changed_actors(root1, root2)
# print(f"Got actors {len(lst_actors)} count")


#address = client.State.account_key("f047684", tipset=tipset)
#print(address)

# res = client.State.list_actors(tipset=None)
# print(len(res))

# actor = client.State.get_actor("f05", tipset=None)
# print(actor)
