import "erc20.spec"


using AToken as _AToken 
using DummyERC20_rewardTokenA as _rewardTokenA
using DummyERC20_rewardTokenB as _rewardTokenB
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 
using RewardsControllerHarness as _RewardsController

/**
 * @notice Using mostly `NONDET` in the methods block, to speed up verification.
 */
methods
{
	// envfree
	// -------
	getUnclaimedRewards(address, address) returns (uint256) envfree
    rewardTokens() returns (address[]) envfree
	isRegisteredRewardToken(address) returns (bool) envfree
    
	// getters from munged/harness
    getRewardTokensLength() returns (uint256) envfree 
    getRewardToken(uint256) returns (address) envfree

	// AToken
	_AToken.UNDERLYING_ASSET_ADDRESS() returns (address) envfree

	// Reward tokens
	_rewardTokenA.balanceOf(address user) returns (uint256) envfree
	_rewardTokenB.balanceOf(address user) returns (uint256) envfree

	// RewardsController
    _RewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
    _RewardsController.getRewardsByAsset(address, uint128) returns (address) envfree

	// Summary
	// -------
	getCurrentRewardsIndex(address reward) returns (uint256) => getCurrentRewardsIndex_summary(reward)

    // Pool.sol
	// --------
    // In RewardsDistributor.sol called by RewardsController.sol
    getAssetIndex(address, address) returns (uint256, uint256) => NONDET

    // In RewardsDistributor.sol called by RewardsController.sol
    finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

    // In ScaledBalanceTokenBase.sol called by getAssetIndex
    scaledTotalSupply() returns (uint256) => NONDET
    
    // ERC20Permit
    // -----------
    permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET

    // AToken.sol
    // ----------
    mint(address,address,uint256,uint256) returns (bool) => NONDET
    burn(address,address,uint256,uint256) returns (bool) => NONDET
    
    // RewardsController.sol
	// ---------------------
    // Called by IncentivizedERC20.sol and by StaticATokenLM.sol
    handleAction(address,uint256,uint256) => NONDET

    // Called by rewardscontroller.sol
    // Defined in scaledbalancetokenbase.sol
    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => NONDET

    // Called by RewardsController._transferRewards()
    // Defined in TransferStrategyHarness as simple transfer() 
    performTransfer(address,address,uint256) returns (bool) => NONDET
 }


/// This ghost is used in summarizing `getCurrentRewardsIndex`.
ghost mapping(address => uint256) _rewards_indexes;


/// Summarizes `getCurrentRewardsIndex` as constant per reward.
function getCurrentRewardsIndex_summary(address reward) returns uint256 {
	return _rewards_indexes[reward];
}


function rewardsController_arbitrary_dual_reward_setup() {
    require _RewardsController.getAvailableRewardsCount(_AToken) == 2;
	require _RewardsController.getRewardsByAsset(_AToken, 0) == _rewardTokenA;
	require _RewardsController.getRewardsByAsset(_AToken, 1) == _rewardTokenB;
}


// Setup the `StaticATokenLM`s rewards so they contain exactly two reward tokens.
function dual_RewardToken_setup() {
	require _rewardTokenA != _rewardTokenB;
	require isRegisteredRewardToken(_rewardTokenA);
	require isRegisteredRewardToken(_rewardTokenB);
	require getRewardTokensLength() == 2;
}


/*
 * Claiming two reward tokens in one array is the same as claiming each one separately.
 * This is based on two rules from `rewardsPreserve.spec`:
 * `rewardsConsistencyWhenSufficientRewardsExist` and `rewardsConsistencyWhenInsufficientRewards`.
 *
 * Previous version passed without rule_sanity in: job-id=`3f8335e5b0a046b384062b5899337b00`
 * Previous version manual sanity test: job-id=`7987b62318ed431997b24948af9fcc23`
 */
rule dual_reward_claiming() {
	dual_RewardToken_setup();
	rewardsController_arbitrary_dual_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract

	uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

	uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
	
	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
	
	uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 diffA = postBalanceA - initialBalanceA;
	uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
	uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

	uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 diffB = postBalanceB - initialBalanceB;
	uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
	uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	assert (
        ( (diffA > 0) => (diffA + unclaimedA == claimableA) ) &&
        (( diffA == 0) => (claimableA == claimablePostA) )
	), "Two rewards claim changes reward A";
	assert (
        ( (diffB > 0) => (diffB + unclaimedB == claimableB) ) &&
        (( diffB == 0) => (claimableB == claimablePostB) )
	), "Two rewards claim changes reward B";
}


/**
 * Passed in: job-id=`898ad8ac9ae247248867b8a42edddebb`
 * using: `--settings -t=3600,-mediumTimeout=50,-depth=7`
 */
rule dual_reward_claiming_assuming_sufficient_rewards() {
	dual_RewardToken_setup();
	rewardsController_arbitrary_dual_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract

	uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

	uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
	
	// Ensure contract has sufficient rewards
	require _rewardTokenA.balanceOf(currentContract) >= claimableA;
	require _rewardTokenB.balanceOf(currentContract) >= claimableB;

	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
	
	uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 diffA = postBalanceA - initialBalanceA;
	uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
	uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

	uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 diffB = postBalanceB - initialBalanceB;
	uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
	uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	assert (diffA > 0) => (diffA + unclaimedA == claimableA), "Two rewards claim changes reward A";
	assert (diffB > 0) => (diffB + unclaimedB == claimableB), "Two rewards claim changes reward B";
}

rule manual_sanity_dual_reward_claiming_assuming_sufficient_rewards() {
	dual_RewardToken_setup();
	rewardsController_arbitrary_dual_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract

	uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

	uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
	
	// Ensure contract has sufficient rewards
	require _rewardTokenA.balanceOf(currentContract) >= claimableA;
	require _rewardTokenB.balanceOf(currentContract) >= claimableB;

	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
	
	uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 diffA = postBalanceA - initialBalanceA;
	uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
	uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

	uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 diffB = postBalanceB - initialBalanceB;
	uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
	uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	assert false;
}


/**
 * Passed in: job-id=`3b17ee1dfee3420ba4eaa61cace2c278`
 * using: `--settings -t=3600,-mediumTimeout=50,-depth=7`
 */
rule dual_reward_claiming_assuming_sufficientA_insufficientB() {
	dual_RewardToken_setup();
	rewardsController_arbitrary_dual_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract

	uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

	uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
	
	// Ensure contract has sufficient/insufficient rewards
	require _rewardTokenA.balanceOf(currentContract) >= claimableA;
	require _rewardTokenB.balanceOf(currentContract) < claimableB;

	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
	
	uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 diffA = postBalanceA - initialBalanceA;
	uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
	uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

	uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 diffB = postBalanceB - initialBalanceB;
	uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
	uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	assert (diffA > 0) => (diffA + unclaimedA == claimableA), "Two rewards claim changes reward A";
	assert (
        ( (diffB > 0) => (diffB + unclaimedB == claimableB) ) &&
        (( diffB == 0) => (claimableB == claimablePostB) )
	), "Two rewards claim changes reward B";
}

rule manual_sanity_dual_reward_claiming_assuming_sufficientA_insufficientB() {
	dual_RewardToken_setup();
	rewardsController_arbitrary_dual_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract

	uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

	uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
	
	// Ensure contract has sufficient/insufficient rewards
	require _rewardTokenA.balanceOf(currentContract) >= claimableA;
	require _rewardTokenB.balanceOf(currentContract) < claimableB;

	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
	
	uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 diffA = postBalanceA - initialBalanceA;
	uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
	uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

	uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 diffB = postBalanceB - initialBalanceB;
	uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
	uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	assert false;
}


/**
 * Passed in: job-id=`f0e8ae865b4642f1bbed174490b4ea3d`
 * using: `--settings -t=7200,-mediumTimeout=100,-depth=10`
 */
rule dual_reward_claiming_assuming_insufficientA_sufficientB() {
	dual_RewardToken_setup();
	rewardsController_arbitrary_dual_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract

	uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

	uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	// Ensure contract has sufficient/insufficient rewards
	require _rewardTokenA.balanceOf(currentContract) < claimableA;
	require _rewardTokenB.balanceOf(currentContract) >= claimableB;

	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
	
	uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 diffA = postBalanceA - initialBalanceA;
	uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
	uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

	uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 diffB = postBalanceB - initialBalanceB;
	uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
	uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	assert (
        ( (diffA > 0) => (diffA + unclaimedA == claimableA) ) &&
        (( diffA == 0) => (claimableA == claimablePostA) )
	), "Two rewards claim changes reward A";
	assert (diffB > 0) => (diffB + unclaimedB == claimableB), "Two rewards claim changes reward B";
}

rule manual_sanity_dual_reward_claiming_assuming_insufficientA_sufficientB() {
	dual_RewardToken_setup();
	rewardsController_arbitrary_dual_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract

	uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

	uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	// Ensure contract has sufficient/insufficient rewards
	require _rewardTokenA.balanceOf(currentContract) < claimableA;
	require _rewardTokenB.balanceOf(currentContract) >= claimableB;

	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
	
	uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 diffA = postBalanceA - initialBalanceA;
	uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
	uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

	uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 diffB = postBalanceB - initialBalanceB;
	uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
	uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	assert false;
}


/**
 * Passed in: job-id=`26df38ab84f641969692a4181228a6ef`
 * using: `--settings -t=3600,-mediumTimeout=50,-depth=7`
 */
//rule dual_reward_claiming_assuming_insufficientA_exactly_sufficientB() {
//	dual_RewardToken_setup();
//	rewardsController_arbitrary_dual_reward_setup();
//
//	env e;
//	require e.msg.sender != currentContract;  // Cannot claim to contract
//
//	uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
//	uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);
//
//	uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
//	uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
//
//    require _rewards_indexes[_rewardTokenA] == 1;
//    require _rewards_indexes[_rewardTokenB] == 1;
//
//	require _rewardTokenA.balanceOf(currentContract) == claimableA - 1;
//	require _rewardTokenB.balanceOf(currentContract) == claimableB;
//
//	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
//	
//	uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
//	uint256 diffA = postBalanceA - initialBalanceA;
//	uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
//	uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);
//
//	uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
//	uint256 diffB = postBalanceB - initialBalanceB;
//	uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
//	uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);
//
//	assert (
//        ( (diffA > 0) => (diffA + unclaimedA == claimableA) ) &&
//        (( diffA == 0) => (claimableA == claimablePostA) )
//	), "Two rewards claim changes reward A";
//	assert (diffB > 0) => (diffB + unclaimedB == claimableB), "Two rewards claim changes reward B";
//}


/*
 * Passed (without rule_sanity) in: job-id=39a25c6f9785451b8eaa587a4184bbf4
 */
rule dual_reward_claiming_insufficient_rewards_both() {
	dual_RewardToken_setup();
	rewardsController_arbitrary_dual_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract

	uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

	uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	// Ensure contracts have insufficient rewards
	require _rewardTokenA.balanceOf(currentContract) < claimableA;
	require _rewardTokenB.balanceOf(currentContract) < claimableB;
	
	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
	
	uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 diffA = postBalanceA - initialBalanceA;
	uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
	uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

	uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 diffB = postBalanceB - initialBalanceB;
	uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
	uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	assert (
        ( (diffA > 0) => (diffA + unclaimedA == claimableA) ) &&
        (( diffA == 0) => (claimableA == claimablePostA) )
	), "Two rewards claim changes reward A";
	assert (
        ( (diffB > 0) => (diffB + unclaimedB == claimableB) ) &&
        (( diffB == 0) => (claimableB == claimablePostB) )
	), "Two rewards claim changes reward B";
}

rule manual_sanity_dual_reward_claiming_insufficient_rewards_both() {
	dual_RewardToken_setup();
	rewardsController_arbitrary_dual_reward_setup();

	env e;
	require e.msg.sender != currentContract;  // Cannot claim to contract

	uint256 initialBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 claimableA = getClaimableRewards(e, e.msg.sender,_rewardTokenA);

	uint256 initialBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 claimableB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

	// Ensure contracts have insufficient rewards
	require _rewardTokenA.balanceOf(currentContract) < claimableA;
	require _rewardTokenB.balanceOf(currentContract) < claimableB;
	
	claimDoubleRewardOnBehalf(e, e.msg.sender, e.msg.sender, _rewardTokenA, _rewardTokenB);
	
	uint256 postBalanceA = _rewardTokenA.balanceOf(e.msg.sender);
	uint256 diffA = postBalanceA - initialBalanceA;
	uint256 unclaimedA = getUnclaimedRewards(e.msg.sender, _rewardTokenA);
	uint256 claimablePostA = getClaimableRewards(e, e.msg.sender, _rewardTokenA);

	uint256 postBalanceB = _rewardTokenB.balanceOf(e.msg.sender);
	uint256 diffB = postBalanceB - initialBalanceB;
	uint256 unclaimedB = getUnclaimedRewards(e.msg.sender, _rewardTokenB);
	uint256 claimablePostB = getClaimableRewards(e, e.msg.sender,_rewardTokenB);

    assert false;
}
