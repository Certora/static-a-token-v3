import "erc20.spec"


using DummyERC20_rewardToken as aRewardToken


methods
{
    /*******************
    *     envfree      *
    ********************/
	getUnclaimedRewards(address user) returns (uint256) envfree
	rewardToken() returns address envfree
	aRewardToken.balanceOf(address user) returns (uint256) envfree

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
    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => NONDET

    // called by StaticATokenLM.collectAndUpdateRewards --> RewardsController._transferRewards()
    //implemented as simple transfer() in TransferStrategyHarness
    performTransfer(address,address,uint256) returns (bool) =>  DISPATCHER(true)

 }


// Ensures rewards are updated correctly after claiming, when there are enough
// reward funds.
/* Verified in:
https://vaas-stg.certora.com/output/98279/274946aa85a247149c025df228c71bc1?anonymousKey=5adb195fd1c025db104868af9aead15244995b7f
 */
rule rewardsConsistencyWhenSufficientRewardsExist() {
	require aRewardToken == rewardToken();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract
	uint256 rewardsBalancePre = aRewardToken.balanceOf(e.msg.sender);
	uint256 claimablePre = getClaimableRewards(e, e.msg.sender);

	// Ensure contract has sufficient rewards
	require aRewardToken.balanceOf(currentContract) == claimablePre;

	claimRewardsToSelf(e);

	uint256 rewardsBalancePost = aRewardToken.balanceOf(e.msg.sender);
	uint256 unclaimedPost = getUnclaimedRewards(e.msg.sender);
	uint256 claimablePost = getClaimableRewards(e, e.msg.sender);
	
	assert rewardsBalancePost >= rewardsBalancePre, "Rewards balance reduced after claim";
	uint256 rewardsGiven = rewardsBalancePost - rewardsBalancePre;
	assert claimablePre == rewardsGiven + unclaimedPost, "Rewards given unequal to claimable";
	assert claimablePost == unclaimedPost, "Claimable different from unclaimed";
}


// Ensures rewards are updated correctly after claiming, when there aren't
// enough funds.
/* Fails in:
https://vaas-stg.certora.com/output/98279/274946aa85a247149c025df228c71bc1?anonymousKey=5adb195fd1c025db104868af9aead15244995b7f
 * Probably because getUnclaimedRewards uses rayToWadRoundDown (StaticATokenLM.sol:332).
 */
rule rewardsConsistencyWhenInsufficientRewards() {
	require aRewardToken == rewardToken();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract
	uint256 rewardsBalancePre = aRewardToken.balanceOf(e.msg.sender);
	uint256 claimablePre = getClaimableRewards(e, e.msg.sender);

	// Ensure contract does not have sufficient rewards
	require aRewardToken.balanceOf(currentContract) < claimablePre;

	claimRewardsToSelf(e);

	uint256 rewardsBalancePost = aRewardToken.balanceOf(e.msg.sender);
	uint256 unclaimedPost = getUnclaimedRewards(e.msg.sender);
	uint256 claimablePost = getClaimableRewards(e, e.msg.sender);
	
	assert rewardsBalancePost >= rewardsBalancePre, "Rewards balance reduced after claim";
	uint256 rewardsGiven = rewardsBalancePost - rewardsBalancePre;
	if (rewardsGiven > 0) {
		assert claimablePre == rewardsGiven + unclaimedPost, "Rewards given unequal to claimable";
	} else {
		// In this case the unclaimed rewards are not updated
		assert claimablePre == claimablePost, "Claimable rewards mismatch";
	}
}
