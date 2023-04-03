import "erc20.spec"


using AToken as _AToken 
using DummyERC20_rewardTokenA as _rewardTokenA
using RewardsControllerHarness as _RewardsController


methods
{
    /*******************
    *     envfree      *
    ********************/
	// StaticATokenLM
	getUnclaimedRewards(address, address) returns (uint256) envfree
	isRegisteredRewardToken(address) returns (bool) envfree
    
	// Getters from munged/harness
    getRewardTokensLength() returns (uint256) envfree 

	// Reward tokens
	_rewardTokenA.balanceOf(address user) returns (uint256) envfree

	// RewardsController
    _RewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
    _RewardsController.getRewardsByAsset(address, uint128) returns (address) envfree

    /*******************
    *  StaticATokenLM  *
    ********************/
	getCurrentRewardsIndex(address reward) returns (uint256) => CONSTANT

    /*******************
    *     Pool.sol     *
    ********************/
    // In RewardsDistributor.sol called by RewardsController.sol
    getAssetIndex(address, address) returns (uint256, uint256) => NONDET

    // In RewardsDistributor.sol called by RewardsController.sol
    finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

    // In ScaledBalanceTokenBase.sol called by getAssetIndex
    scaledTotalSupply() returns (uint256) => NONDET
    
    /*****************************
    *     OZ ERC20Permit.sol     *
    ******************************/
    permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET

    /*********************
    *     AToken.sol     *
    **********************/
    mint(address,address,uint256,uint256) returns (bool) => NONDET
    burn(address,address,uint256,uint256) returns (bool) => NONDET
    
    /**********************************
    *     RewardsController.sol     *
    **********************************/
    // Called by RewardsController.IncentivizedERC20.sol and also by StaticATokenLM.sol
    handleAction(address,uint256,uint256) => NONDET

    // Called by  StaticATokenLM.claimRewardsToSelf  -->  RewardsController._getUserAssetBalances
    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => NONDET

    // Called by StaticATokenLM.collectAndUpdateRewards --> RewardsController._transferRewards()
    performTransfer(address,address,uint256) returns (bool) => NONDET
 }


// Set up a _rewardTokenA as the single reward token.
function single_RewardToken_setup() {
	require isRegisteredRewardToken(_rewardTokenA);
	require getRewardTokensLength() == 1;
}


// Set up _rewardTokenA as the single reward token for _AToken.
function rewardsController_arbitrary_single_reward_setup() {
    require _RewardsController.getAvailableRewardsCount(_AToken) == 1;
	require _RewardsController.getRewardsByAsset(_AToken, 0) == _rewardTokenA;
}


/*
 * Using an array with the same reward twice does not give more rewards,
 * assuming the contract has sufficient rewards.
 *
 * Passed with rule_sanity in: job-id=179a4f98a304475dab4df29fcfe7ae2c
 */
rule prevent_duplicate_reward_claiming_single_reward_sufficient() {
	single_RewardToken_setup();
	rewardsController_arbitrary_single_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract

	uint256 initialBalance = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 claimable = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

	// Ensure contract has sufficient rewards
	require _rewardTokenA.balanceOf(currentContract) >= claimable;

	// Duplicate claim
	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenA);
	
	uint256 duplicateClaimBalance = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 diff = duplicateClaimBalance - initialBalance;
	uint256 unclaimed = getUnclaimedRewards(e.msg.sender, _rewardTokenA);

	assert diff + unclaimed <= claimable, "Duplicate claim changes rewards";
}


/*
 * Using an array with the same reward twice does not give more rewards,
 * assuming the contract does not have sufficient rewards.
 *
 * Passed with rule_sanity in: job-id=7efe69f2711149c2bf98a6218bdd3849
 */
rule prevent_duplicate_reward_claiming_single_reward_insufficient() {
	single_RewardToken_setup();
	rewardsController_arbitrary_single_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract

	uint256 initialBalance = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 claimable = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

	// Ensure contract does not have sufficient rewards
	require _rewardTokenA.balanceOf(currentContract) < claimable;

	// Duplicate claim
	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenA);
	
	uint256 duplicateClaimBalance = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 diff = duplicateClaimBalance - initialBalance;
	uint256 unclaimed = getUnclaimedRewards(e.msg.sender, _rewardTokenA);

	assert diff + unclaimed <= claimable, "Duplicate claim changes rewards";
}
