import "erc20.spec"


methods
{
    /*******************
    *     envfree      *
    ********************/

    /*******************
    *     Pool.sol     *
    ********************/

    //in RewardsDistributor.sol called by RewardsController.sol
    getAssetIndex(address, address) returns (uint256, uint256) =>  DISPATCHER(true)

    //in RewardsDistributor.sol called by RewardsController.sol
    finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

    //in ScaledBalanceTokenBase.sol called by getAssetIndex
    scaledTotalSupply() returns (uint256)  => DISPATCHER(true) 

    /*******************************
    *     RewardsController.sol    *
    ********************************/
    // claimRewards(address[],uint256,address,address) => NONDET
     
    /*****************************
    *     OZ ERC20Permit.sol     *
    ******************************/
    //permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET

    /*********************
    *     AToken.sol     *
    **********************/
    mint(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    burn(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    //getIncentivesController() returns (address) => CONSTANT
    //UNDERLYING_ASSET_ADDRESS() returns (address) => CONSTANT
    
    /**********************************
    *     RewardsDistributor.sol     *
    **********************************/
    //getRewardsList() returns (address[]) => NONDET

    /**********************************
    *     RewardsController.sol     *
    **********************************/
    //call by RewardsController.IncentivizedERC20.sol and also by StaticATokenLM.sol
    handleAction(address,uint256,uint256) => DISPATCHER(true)

    // called by  StaticATokenLM.claimRewardsToSelf  -->  RewardsController._getUserAssetBalances
    // get balanceOf and totalSupply of _aToken
    // todo - link to the actual token.
    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => DISPATCHER(true)

    // called by StaticATokenLM.collectAndUpdateRewards --> RewardsController._transferRewards()
    //implemented as simple transfer() in TransferStrategyHarness
    performTransfer(address,address,uint256) returns (bool) =>  DISPATCHER(true)

 }

/* Ensure rate is non-decreasing (except for initialize method)
 * from IStaticATokenLM: “Returns the Aave liquidity index of the underlying
 * aToken, denominated rate here as it can be considered as an ever-increasing
 * exchange rate”
 * Except for initialize and metaDeposit, all other methods passed in:
 * https://vaas-stg.certora.com/output/98279/34caebcbc4de4a779c90545ef8b0a0cc?anonymousKey=41598195e1afbc432ed75d9108392732d40fbfb2
 *
 * Note: metaDeposit seems to be vacuous, i.e. always fails on a require statement.
 */
rule nonDecreasingRate(method f) {
	require f.selector != initialize(address, string, string).selector;

	env e1;
	env e2;
	require e1.block.timestamp < 2^32;
	require e2.block.timestamp < 2^32;
	require e1.block.timestamp <= e2.block.timestamp;

	uint256 earlyRate = rate(e1);

	calldataarg args;
	f(e1, args);

	uint256 postRate = rate(e1);
	uint256 lateRate = rate(e2);

	assert earlyRate <= postRate, "rate declines after method";
	assert postRate <= lateRate, "rate declines with time";
}
