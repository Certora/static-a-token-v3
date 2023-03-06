import "erc20.spec"


// using DummyERC20_rewardToken as aRewardToken
// using RewardsControllerHarness as aRewardsController
// using AToken as _AToken 


methods
{
    /*******************
    *     envfree      *
    ********************/
	// getUnclaimedRewards(address user) returns (uint256) envfree
	// rewardToken() returns address envfree
	// aRewardToken.balanceOf(address user) returns (uint256) envfree
	// incentivesController() returns (address) envfree

    // aRewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
    // aRewardsController.getFirstRewardsByAsset(address) returns (address ) envfree

    /*******************
    *     Pool.sol     *
    ********************/
    // can we assume a fixed index? 1 ray?
    // getReserveNormalizedIncome(address) returns (uint256) => DISPATCHER(true)

    //in RewardsDistributor.sol called by RewardsController.sol
    getAssetIndex(address, address) returns (uint256, uint256) =>  DISPATCHER(true)
    //deposit(address,uint256,address,uint16) => DISPATCHER(true)
    //withdraw(address,uint256,address) returns (uint256) => DISPATCHER(true)
    finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

    //in ScaledBalanceTokenBase.sol called by getAssetIndex
    scaledTotalSupply() returns (uint256)  => DISPATCHER(true) 
    
    //IAToken.sol
    mint(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    burn(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)

    /*******************************
    *     RewardsController.sol    *
    ********************************/
   // claimRewards(address[],uint256,address,address) => NONDET
     
   /*****************************
    *     OZ ERC20Permit.sol     *
    ******************************/
    permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET

    /*********************
    *     AToken.sol     *
    **********************/
    getIncentivesController() returns (address) => CONSTANT
    UNDERLYING_ASSET_ADDRESS() returns (address) => CONSTANT
    
    /**********************************
    *     RewardsDistributor.sol     *
    **********************************/
    getRewardsList() returns (address[]) => NONDET

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


rule nonDecreasingRate(method f) {
	require f.selector != initialize(address, address, string, string).selector;

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
