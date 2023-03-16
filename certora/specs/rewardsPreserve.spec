import "erc20.spec"


using AToken as _AToken 
using DummyERC20_rewardToken as _DummyERC20_rewardToken
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 
using RewardsControllerHarness as _RewardsController


methods
{
    /*******************
    *     envfree      *
    ********************/
	// StaticATokenLM
	getUnclaimedRewards(address, address) returns (uint256) envfree
    rewardTokens() returns (address[]) envfree
	isRegisteredRewardToken(address) returns (bool) envfree
    
	// getters from munged/harness
    getRewardTokensLength() returns (uint256) envfree 
    getRewardToken(uint256) returns (address) envfree

	// AToken
	_AToken.UNDERLYING_ASSET_ADDRESS() returns (address) envfree

	// Reward token
	_DummyERC20_rewardToken.balanceOf(address user) returns (uint256) envfree

	// RewardsController
    _RewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
    _RewardsController.getFirstRewardsByAsset(address) returns (address ) envfree

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
     
    /*****************************
    *     OZ ERC20Permit.sol     *
    ******************************/
    permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET

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

// @title Reward hook
// @notice allows a single reward
// TODO: allow 2 or 3 rewards
// hook Sload address reward _rewardTokens[INDEX  uint256 i] STORAGE {
//     require reward == _DummyERC20_rewardToken;
// } 
 

// Setup the StaticATokenLM's rewards so they contain a single reward token
// which is _DummyERC20_rewardToken.
function single_RewardToken_setup() {
	require isRegisteredRewardToken(_DummyERC20_rewardToken);
	require getRewardTokensLength() == 1;
	require getRewardToken(0) == _DummyERC20_rewardToken;
}


// Sets the first reward to _AToken as _DummyERC20_rewardToken
function rewardsController_reward_setup() {
    require _RewardsController.getAvailableRewardsCount(_AToken) > 0;
    require _RewardsController.getFirstRewardsByAsset(_AToken) == _DummyERC20_rewardToken;
}


/* Ensures rewards are updated correctly after claiming, when there are enough
 * reward funds.
 * Succeeds in:
 * https://vaas-stg.certora.com/output/98279/06bddfec425a4f63a4ee97fc688f626e?anonymousKey=bfc940b1fcf8a201007e87438bb92f8fda4775c5
 */
rule rewardsConsistencyWhenSufficientRewardsExist() {
	// Assuming single reward
	single_RewardToken_setup();
	// rewardsController_reward_setup(); // TODO: remove?

	// Create a rewards array
	address[] _rewards;
	require _rewards[0] == _DummyERC20_rewardToken;
	require _rewards.length == 1;

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract
	uint256 rewardsBalancePre = _DummyERC20_rewardToken.balanceOf(e.msg.sender);
	uint256 claimablePre = getClaimableRewards(e, e.msg.sender, _DummyERC20_rewardToken);

	// Ensure contract has sufficient rewards
	require _DummyERC20_rewardToken.balanceOf(currentContract) >= claimablePre;

	claimRewardsToSelf(e, _rewards);

	uint256 rewardsBalancePost = _DummyERC20_rewardToken.balanceOf(e.msg.sender);
	uint256 unclaimedPost = getUnclaimedRewards(e.msg.sender, _DummyERC20_rewardToken);
	uint256 claimablePost = getClaimableRewards(e, e.msg.sender, _DummyERC20_rewardToken);
	
	assert rewardsBalancePost >= rewardsBalancePre, "Rewards balance reduced after claim";
	uint256 rewardsGiven = rewardsBalancePost - rewardsBalancePre;
	assert claimablePre == rewardsGiven + unclaimedPost, "Rewards given unequal to claimable";
	assert claimablePost == unclaimedPost, "Claimable different from unclaimed";
}


/* Ensures rewards are updated correctly after claiming, when there aren't
 * enough funds.
 * Fails in:
 * https://vaas-stg.certora.com/output/98279/274946aa85a247149c025df228c71bc1?anonymousKey=5adb195fd1c025db104868af9aead15244995b7f
 * Reported in: https://github.com/bgd-labs/static-a-token-v3/issues/23
 * 
 * Passed after fix:
 * https://vaas-stg.certora.com/output/98279/f74b4265c1084fdf951f44e519a7cbc3?anonymousKey=2fdef305121e549c5062c641ffbe53120ff72cfd
 */
rule rewardsConsistencyWhenInsufficientRewards() {
	// Assuming single reward
	single_RewardToken_setup();
	// rewardsController_reward_setup(); // TODO: remove?

	// Create a rewards array
	address[] _rewards;
	require _rewards[0] == _DummyERC20_rewardToken;
	require _rewards.length == 1;

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract
	uint256 rewardsBalancePre = _DummyERC20_rewardToken.balanceOf(e.msg.sender);
	uint256 claimablePre = getClaimableRewards(e, e.msg.sender, _DummyERC20_rewardToken);

	// Ensure contract does not have sufficient rewards
	require _DummyERC20_rewardToken.balanceOf(currentContract) < claimablePre;

	claimRewardsToSelf(e, _rewards);

	uint256 rewardsBalancePost = _DummyERC20_rewardToken.balanceOf(e.msg.sender);
	uint256 unclaimedPost = getUnclaimedRewards(e.msg.sender, _DummyERC20_rewardToken);
	uint256 claimablePost = getClaimableRewards(e, e.msg.sender, _DummyERC20_rewardToken);
	
	assert rewardsBalancePost >= rewardsBalancePre, "Rewards balance reduced after claim";
	uint256 rewardsGiven = rewardsBalancePost - rewardsBalancePre;
	if (rewardsGiven > 0) {
		assert claimablePre == rewardsGiven + unclaimedPost, "Rewards given unequal to claimable";
	} else {
		// In this case the unclaimed rewards are not updated
		assert claimablePre == claimablePost, "Claimable rewards mismatch";
	}
}

/* Only claim rewards methods (and initialize) should cause total rewards to decline.
 * Except for metaWithdraw, redeem, claimSingleRewardOnBehalf, succeeded in: 
 * https://vaas-stg.certora.com/output/98279/632020a606444f5886390c8f5c02e583?anonymousKey=655b64a7c7a0cbf503036f107067b92030097ad7
 * NOTE: metaDeposit seems to be vacuous, i.e. always fails on a require statement.
 * 
 * metaWithdraw passed in (other methods were DISABLED):
 * https://vaas-stg.certora.com/output/98279/21e258b783a74c55bae60d408b6a2637?anonymousKey=b6c7b24e9d5bc54a8a632c9058c860e1db9fc4fb
 *
 * claimSingleRewardOnBehalf passed in (other methods were DISABLED):
 * https://vaas-stg.certora.com/output/98279/921238b5d35a402999f743cc0eb3dea2?anonymousKey=5e33696510484a2efade606642ca766284aecd17
 *
 * redeem(uint256,address,address,bool) passed in (other methods were DISABLED):
 * https://vaas-stg.certora.com/output/98279/497fa8295d62489b9b6f8515be5a06f7?anonymousKey=de80e3820be8d4e75312f8b8f17288d1c867b095
 */
rule rewardsTotalDeclinesOnlyByClaim(method f) {
	// Assuming single reward
	single_RewardToken_setup();
	rewardsController_reward_setup();

	require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;

	env e;

	require e.msg.sender != currentContract;
	require f.selector != initialize(address, string, string).selector;

	uint256 preTotal = getTotalClaimableRewards(e, _DummyERC20_rewardToken);

	calldataarg args;
	f(e, args);

	uint256 postTotal = getTotalClaimableRewards(e, _DummyERC20_rewardToken);

	assert (postTotal < preTotal) => (
		(f.selector == claimRewardsOnBehalf(address, address, address[]).selector) ||
		(f.selector == claimRewards(address, address[]).selector) ||
		(f.selector == claimRewardsToSelf(address[]).selector) ||
		(f.selector == claimSingleRewardOnBehalf(address,address,address).selector)
	), "Total rewards decline not due to claim";
}
