import "erc20.spec"


using AToken as _AToken 
using DummyERC20_rewardToken as _DummyERC20_rewardToken
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
    //permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET

    /*********************
    *     AToken.sol     *
    **********************/
    //mint(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    //burn(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
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


// Returns an array of reward tokens, containing a single reward token.
function gen_single_reward_array() returns address[]{
	address[] _rewards;
	require _rewards[0] == _DummyERC20_rewardToken;
	require _rewards.length == 1;
	return _rewards;
}


// Sets the first reward to _AToken as _DummyERC20_rewardToken
function rewardsController_reward_setup() {
    require _RewardsController.getAvailableRewardsCount(_AToken) > 0;
    require _RewardsController.getFirstRewardsByAsset(_AToken) == _DummyERC20_rewardToken;
}


rule mini_test() {
	single_RewardToken_setup();
	rewardsController_reward_setup(); // TODO: remove?
	address[] _rewards = gen_single_reward_array();
	require _rewards.length == 1;

	assert getRewardTokensLength() == 1, "rewardTokens length is wrong";
	assert getRewardToken(0) == _DummyERC20_rewardToken, "Reward in rewardTokens is wrong";
	assert _rewards.length == 1, "rewards length is wrong";
	assert _rewards[0] == _DummyERC20_rewardToken, "Reward in rewards is wrong";
}


// Ensures rewards are updated correctly after claiming, when there are enough
// reward funds.
rule rewardsConsistencyWhenSufficientRewardsExist() {
	// Assuming single reward
	single_RewardToken_setup();
	rewardsController_reward_setup(); // TODO: remove?
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

rule simplified() {
	// Assuming single reward
	single_RewardToken_setup();
	address[] _rewards;
	require _rewards[0] == _DummyERC20_rewardToken;
	require _rewards.length == 1;

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract
	uint256 claimablePre = getClaimableRewards(e, e.msg.sender, _rewards[0]);

	// Ensure contract has sufficient rewards
	require _DummyERC20_rewardToken.balanceOf(currentContract) >= claimablePre;

	claimRewardsToSelf(e, _rewards);

	uint256 rewardsBalancePost = _DummyERC20_rewardToken.balanceOf(e.msg.sender);

	assert rewardsBalancePost >= claimablePre, "Rewards less than claimable";
}

rule simplified_use_existing_array() {
	// Assuming single reward
	single_RewardToken_setup();
	rewardsController_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract
	uint256 claimablePre = getClaimableRewards(e, e.msg.sender, _DummyERC20_rewardToken);

	// Ensure contract has sufficient rewards
	require _DummyERC20_rewardToken.balanceOf(currentContract) >= claimablePre;

	claimRewardsToSelf(e, rewardTokens());

	uint256 rewardsBalancePost = _DummyERC20_rewardToken.balanceOf(e.msg.sender);

	assert rewardsBalancePost >= claimablePre, "Rewards less than claimable";
}


/* Ensures rewards are updated correctly after claiming, when there aren't
 * enough funds.
 * Fails in:
 * https://vaas-stg.certora.com/output/98279/274946aa85a247149c025df228c71bc1?anonymousKey=5adb195fd1c025db104868af9aead15244995b7f
 * Reported in: https://github.com/bgd-labs/static-a-token-v3/issues/23
 */
rule rewardsConsistencyWhenInsufficientRewards() {
	// Assuming single reward
	single_RewardToken_setup();
	rewardsController_reward_setup();
	address[] rewards = gen_single_reward_array();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract
	uint256 rewardsBalancePre = _DummyERC20_rewardToken.balanceOf(e.msg.sender);
	uint256 claimablePre = getClaimableRewards(e, e.msg.sender, rewards[0]);

	// Ensure contract does not have sufficient rewards
	require _DummyERC20_rewardToken.balanceOf(currentContract) < claimablePre;

	claimRewardsToSelf(e, rewards);

	uint256 rewardsBalancePost = _DummyERC20_rewardToken.balanceOf(e.msg.sender);
	uint256 unclaimedPost = getUnclaimedRewards(e.msg.sender, rewards[0]);
	uint256 claimablePost = getClaimableRewards(e, e.msg.sender, rewards[0]);
	
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
 * Except for metaDeposit (and initialize) all other methods passed in:
 * https://prover.certora.com/output/98279/05e0d056329345c5a6ba8136e75f5c03?anonymousKey=edc61d598888d191816304c44d2ced0e678d3d8b
 * Note: metaDeposit seems to be vacuous, i.e. always fails on a require statement.
 */
rule rewardsTotalDeclinesOnlyByClaim(method f) {
	// Assuming single reward
	single_RewardToken_setup();
	rewardsController_reward_setup();

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
		(f.selector == claimRewardsToSelf(address[]).selector)
	), "Total rewards decline not due to claim";
}
