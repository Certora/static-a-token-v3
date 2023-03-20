import "erc20.spec"

using AToken as _AToken 
using RewardsControllerHarness as _RewardsController 
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 
using DummyERC20_rewardToken as _DummyERC20_rewardToken 
using SymbolicLendingPoolL1 as _SymbolicLendingPoolL1 
using TransferStrategyHarness as _TransferStrategy
using StaticATokenLMHarness as _StaticATokenLM
using ScaledBalanceTokenHarness as _ScaledBalanceToken

methods
{

    totalSupply() returns uint256 envfree
	balanceOf(address) returns (uint256) envfree
    rewardTokens() returns (address[]) envfree

    // getters from munged/harness
    getRewardTokensLength() returns (uint256) envfree 
    getRewardToken(uint256) returns (address) envfree
    isRegisteredRewardToken(address) envfree

    _AToken.totalSupply() returns uint256 envfree
	_AToken.balanceOf(address) returns (uint256) envfree
	_AToken.scaledTotalSupply() returns (uint256) envfree
    _AToken.scaledBalanceOf(address) returns (uint256) envfree
    _AToken.transferFrom(address,address,uint256) returns (bool)
    
    _RewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
    _RewardsController.getDistributionEnd(address, address)  returns (uint256) envfree
    _RewardsController.getRewardsByAsset(address,uint128) returns (address ) envfree
    _RewardsController.getUserAccruedRewards(address, address) returns (uint256) envfree
    _RewardsController.getAssetByIndex(uint256) returns (address) envfree
    _RewardsController.getAssetListLength() returns (uint256) envfree
    _RewardsController.getUserAccruedReward(address, address, address) returns (uint256) envfree
    _RewardsController.getAssetDecimals(address) returns (uint8) envfree 
    _RewardsController.getRewardsData(address,address) returns (uint256,uint256,uint256,uint256) envfree
    _RewardsController.getUserAssetIndex(address,address, address) returns (uint256) envfree 
    
    _DummyERC20_rewardToken.balanceOf(address) returns (uint256) envfree

    /*******************
    *     Pool.sol     *
    ********************/
    //getReserveNormalizedIncome(address) returns (uint256) => ALWAYS(1000000000000000000000000000)

    //in RewardsDistributor.sol called by RewardsController.sol
    getAssetIndex(address, address) returns (uint256, uint256) =>  DISPATCHER(true)
    
    //caled by AToken.sol.  function executeFinalizeTransfer is defined in SupplyLogic.sol
    finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

    //in ScaledBalanceTokenBase.sol called by getAssetIndex
    scaledTotalSupply() returns (uint256) envfree => DISPATCHER(true) 
    

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
    mint(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    burn(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
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
    //defined in ScaledBalanceTokenBase.sol called in RewardsController.sol
    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => DISPATCHER(true)
//    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => NONDET

    // called by StaticATokenLM.collectAndUpdateRewards --> RewardsController._transferRewards()
    //implemented as simple transfer() in TransferStrategyHarness
    performTransfer(address,address,uint256) returns (bool) =>  DISPATCHER(true)

 }

/// @notice Claim rewards methods
definition claimFunctions(method f) returns bool = 
            f.selector == claimRewardsToSelf(address[]).selector ||
            f.selector == claimRewards(address, address[]).selector ||
            f.selector ==claimRewardsOnBehalf(address, address,address[]).selector ||
            f.selector == collectAndUpdateRewards(address).selector;



/// @title Reward hook
/// @notice allows a single reward
//todo: allow 2 or 3 rewards
hook Sload address reward _rewardTokens[INDEX  uint256 i] STORAGE {
    require reward == _DummyERC20_rewardToken;
} 


///////////////////////////
/// @title Sum of balances of StaticAToken 
ghost sumAllBalance() returns mathint {
    init_state axiom sumAllBalance() == 0;
}

hook Sstore balanceOf[KEY address a] uint256 balance (uint256 old_balance) STORAGE {
  havoc sumAllBalance assuming sumAllBalance@new() == sumAllBalance@old() + balance - old_balance;
}

hook Sload uint256 balance balanceOf[KEY address a] STORAGE {
    require balance <= sumAllBalance();
} 

/// @title Sum of scaled balances of AToken 
ghost sumAllATokenScaledBalance() returns mathint {
    init_state axiom sumAllATokenScaledBalance() == 0;
}

hook Sstore _AToken._userState[KEY address a] .(offset 0) uint128 balance (uint128 old_balance) STORAGE {
  havoc sumAllATokenScaledBalance assuming sumAllATokenScaledBalance@new() == sumAllATokenScaledBalance@old() + balance - old_balance;
}

hook Sload uint128 balance _AToken._userState[KEY address a] .(offset 0) STORAGE {
    require balance <= sumAllATokenScaledBalance();
} 


/// @title balancerOf(user) <= totalSupply()
invariant inv_balanceOf_leq_totalSupply(address user)
	balanceOf(user) <= totalSupply()
	{
		preserved {
			requireInvariant sumAllBalance_eq_totalSupply();
		}
	}

/// @title AToken balancerOf(user) <= AToken totalSupply()
//timeout on redeem metaWithdraw
invariant inv_atoken_balanceOf_leq_totalSupply(address user)
	_AToken.balanceOf(user) <= _AToken.totalSupply()
     filtered { f -> !f.isView && f.selector != redeem(uint256,address,address,bool).selector}
    {
		preserved with (env e){
			requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
        }
	}

/// @dev case split of inv_atoken_balanceOf_leq_totalSupply
invariant inv_atoken_balanceOf_leq_totalSupply_redeem(address user)
	_AToken.balanceOf(user) <= _AToken.totalSupply()
    filtered { f -> f.selector == redeem(uint256,address,address,bool).selector}
    {
		preserved with (env e){
			requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
    	}
	}

/// @title AToken sum of 2 balancers <= AToken totalSupply()
invariant inv_atoken_balanceOf_2users_leq_totalSupply(address user1, address user2)
	(_AToken.balanceOf(user1) + _AToken.balanceOf(user2))<= _AToken.totalSupply()
    {
		preserved with (env e1){
            setup(e1, user1, user2);
		}
        preserved redeem(uint256 shares, address receiver, address owner) with (env e2){
            require user1 != user2;
            require _AToken.balanceOf(currentContract) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
        }
        preserved redeem(uint256 shares, address receiver, address owner, bool toUnderlying) with (env e3){
            require user1 != user2;
        	requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
            require _AToken.balanceOf(e3.msg.sender) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
            require _AToken.balanceOf(currentContract) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
        }
        preserved withdraw(uint256 assets, address receiver,address owner) with (env e4){
            require user1 != user2;
        	requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
            require _AToken.balanceOf(e4.msg.sender) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
            require _AToken.balanceOf(currentContract) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
        }

        preserved metaWithdraw(address owner, address recipient,uint256 staticAmount,uint256 dynamicAmount,bool toUnderlying,uint256 deadline,_StaticATokenLM.SignatureParams sigParams)
        with (env e5){
            require user1 != user2;
        	requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
            require _AToken.balanceOf(e5.msg.sender) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
            require _AToken.balanceOf(currentContract) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
        }

	}

/// @title AToken scaled balancerOf(user) <= AToken scaled totalSupply()
invariant inv_atoken_scaled_balanceOf_leq_totalSupply(address user)
	_AToken.scaledBalanceOf(user) <= _AToken.scaledTotalSupply()
    {
		preserved {
			requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
		}
	}

/// @title Sum of balances=totalSupply()
invariant sumAllBalance_eq_totalSupply()
	sumAllBalance() == totalSupply()

/// @title Sum of AToken scaled balances = AToken scaled totalSupply()
invariant sumAllATokenScaledBalance_eq_totalSupply()
	sumAllATokenScaledBalance() == _AToken.scaledTotalSupply()



/// @title Assumptions that should hold in any run
/// @dev Assume that RewardsController.configureAssets(RewardsDataTypes.RewardsConfigInput[] memory rewardsInput) was called
function setup(env e, address user1, address user2)
{
    
    //assume a single reward
    //todo: allow multiple rewards
    require getRewardTokensLength() == 1;
    require getRewardToken(0) == _DummyERC20_rewardToken;

    require _RewardsController.getAvailableRewardsCount(_AToken)  > 0;
    require _RewardsController.getRewardsByAsset(_AToken, 0) == _DummyERC20_rewardToken;

    require currentContract != e.msg.sender;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    require _DummyERC20_rewardToken != e.msg.sender;
    require _SymbolicLendingPoolL1 != e.msg.sender;
    require _TransferStrategy != e.msg.sender;
    require _ScaledBalanceToken != e.msg.sender;
    require _TransferStrategy != e.msg.sender;
   

    require currentContract != user1;
    require _AToken != user1;
    require _RewardsController !=  user1;
    require _DummyERC20_aTokenUnderlying  != user1;
    require _DummyERC20_rewardToken != user1;
    require _SymbolicLendingPoolL1 != user1;
    require _TransferStrategy != user1;
    require _ScaledBalanceToken != user1;
    require _TransferStrategy != user1;
   
    require currentContract != user2;
    require _AToken != user2;
    require _RewardsController !=  user2;
    require _DummyERC20_aTokenUnderlying != user2;
    require _DummyERC20_rewardToken  != user2;
    require _SymbolicLendingPoolL1 != user2;
    require _TransferStrategy != user2;
    require _ScaledBalanceToken != user2;
    require _TransferStrategy != user2;
   
}

//todo: debug fail
//https://vaas-stg.certora.com/output/99352/0dcf7300c5cb485b89a9961a67854e25/?anonymousKey=f36833d4033d955e25d6af7fdef259337cb3f9cc
invariant singleAssetAccrruedRewards(env e0, address asset, address reward, address user)
    ((_RewardsController.getAssetListLength() == 1 && _RewardsController.getAssetByIndex(0) == asset)
        => (_RewardsController.getUserAccruedReward(asset, reward, user) == _RewardsController.getUserAccruedRewards(reward, user)))
        {
            preserved with (env e1){
                //setup(e1, user, reward); //pass with setup() requirements
                //setup(e1, user, asset);

                require e1.msg.sender == e0.msg.sender;
                require e1.msg.sender != asset;
                require e1.msg.sender != reward;
                require e1.msg.sender != user;

                require e1.msg.sender != _StaticATokenLM;
                require e1.msg.sender != _SymbolicLendingPoolL1;
                require e1.msg.sender != _RewardsController;
                require e1.msg.sender != _DummyERC20_aTokenUnderlying;
                require e1.msg.sender != _ScaledBalanceToken;
                require user != _RewardsController;
                require user != _ScaledBalanceToken;
                require user != _TransferStrategy;
                require asset != _RewardsController;
                require asset != _TransferStrategy;
                require asset != _ScaledBalanceToken;
                require reward != _StaticATokenLM;
                require reward != _AToken;
                require reward != _ScaledBalanceToken;
                require reward != _TransferStrategy;
            }
        }


//pass
/// @title The return value of totalAssets() should be unchanged after reward claim
rule totalAssets_stable(method f)
    filtered { f -> (f.selector == claimRewardsToSelf(address[]).selector ||
                    f.selector == claimRewards(address, address[]).selector ||
                    f.selector == claimRewardsOnBehalf(address, address,address[]).selector) }
{
    env e;
    calldataarg args;
    mathint totalAssetBefore = totalAssets(e);
    f(e, args); 
    mathint totalAssetAfter = totalAssets(e);
    assert totalAssetAfter == totalAssetBefore;
}

//todo: remove this rule
//pass
rule totalAssets_stable_after_collectAndUpdateRewards()
{
    env e;
    require _RewardsController.getRewardsByAsset(_AToken, 0) != _AToken;
    require _RewardsController.getUserAccruedReward(currentContract, _AToken, _AToken) ==0;
    address reward;
    mathint totalAssetBefore = totalAssets(e);
    collectAndUpdateRewards(e, reward); 
    mathint totalAssetAfter = totalAssets(e);
    assert totalAssetAfter == totalAssetBefore;
}


//pass
rule reward_balance_stable_after_collectAndUpdateRewards()
{
    env e;
    address reward;
    address sender;
    uint256 amount;

    storage initial = lastStorage;
    collectAndUpdateRewards(e, reward); 
    mathint reward_balance_before = _DummyERC20_rewardToken.balanceOf(currentContract);

    _AToken.transferFrom(e, sender, currentContract, amount) at initial;
    collectAndUpdateRewards(e, reward); 
    mathint reward_balance_after = _DummyERC20_rewardToken.balanceOf(currentContract);

    assert reward_balance_before == reward_balance_after;
}



//pass
rule totalAssets_stable_after_claimRewardsOnBehalf()
{
    env e;
    calldataarg args;
    // address onBehalfOf;
    // address receiver;
    // address[] rewards;

    mathint totalAssetBefore = totalAssets(e);
    // claimRewardsOnBehalf(e, onBehalfOf, receiver, rewards);
    claimRewardsOnBehalf(e, args);
    mathint totalAssetAfter = totalAssets(e);
    assert totalAssetAfter == totalAssetBefore;
}

//pass as expected
// rule totalAssets_stable_after_claimSingleRewardOnBehalf()
// {
//     env e;
//     calldataarg args;
//     // address onBehalfOf;
//     // address receiver;
//     // address reward;

//     mathint totalAssetBefore = totalAssets(e);
// //    claimSingleRewardOnBehalf(e, onBehalfOf, receiver, reward);
//     claimSingleRewardOnBehalf(e, args);
//     mathint totalAssetAfter = totalAssets(e);
//     assert totalAssetAfter == totalAssetBefore;
// }




/// @title The return value of getUnclaimableRewards() should be unchanged unless rewards were claimed
//fail
//https://vaas-stg.certora.com/output/99352/9c9d8a8a9ab5420082c4193b4b4a8c13/?anonymousKey=59fbb313753ef7f12073e1a56d5eb4c279c4c19d
//https://vaas-stg.certora.com/output/99352/dc12bed9e34845ccaf077a1cd4f1a2bf/?anonymousKey=ce81c372f7d33946448b49cbf3f25cd3c3a8c436
rule totalClaimableRewards_stable(method f)
    filtered { f -> !f.isView && !claimFunctions(f)  }
{
    env e;
    calldataarg args;
    address reward;
    mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    f(e, args); 
    mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
}


//fail
//
rule totalClaimableRewards_stable_excl_currentContract(method f)
    filtered { f -> !f.isView && !claimFunctions(f)  }
{
    env e;
    calldataarg args;
    address reward;
    require reward != currentContract;
  
    mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    f(e, args); 
    mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
}

/// @title The return value of getClaimableRewards() should be unchanged unless rewards were claimed
//fail
//https://vaas-stg.certora.com/output/99352/9c699ff3d7754f668bc56acf4af5b45d/?anonymousKey=8c9d2f41b8b8c878d3380d3803f832148ac2ac21
//https://vaas-stg.certora.com/output/99352/9c699ff3d7754f668bc56acf4af5b45d/?anonymousKey=8c9d2f41b8b8c878d3380d3803f832148ac2ac21
rule getClaimableRewards_stable(method f)
    filtered { f -> !f.isView && !claimFunctions(f)  && f.selector != initialize(address,string,string).selector}
{
    env e;
    calldataarg args;
    address user;
    address reward;
    
    require user != 0;

    setup(e, user, reward);    
    //assume a single reward
    //todo: allow multiple rewards
    require reward == _DummyERC20_rewardToken;
    require getRewardTokensLength() == 1;
    require getRewardToken(0) == _DummyERC20_rewardToken;
    
    require isRegisteredRewardToken(reward); //todo: review the assumption
 
    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    f(e, args); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}
//pass
//todo: remove
rule getClaimableRewards_stable_after_atoken_transferFrom()
{
    env e;
    calldataarg args;
    address user;
    address reward;

    address sender;
    uint256 amount;
    
    require user != 0;
    //setup(e, user, sender);
    //assume a single reward
    //todo: allow multiple rewards
    // require reward == _DummyERC20_rewardToken;
    // require getRewardTokensLength() == 1;
    // require getRewardToken(0) == _DummyERC20_rewardToken;
    
    //require isRegisteredRewardToken(reward); //todo: review assumption
 
    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    _AToken.transferFrom(e, sender, currentContract, amount);
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}
 
/// @title special case of rule getClaimableRewards_stable for initialize
//fail
//todo: consider removing this rule. no method is called before initialize()
rule getClaimableRewards_stable_after_initialize(method f)
    filtered { f -> !f.isView && !claimFunctions(f) }{

    env e;
    address newAToken;
    string staticATokenName;
    string staticATokenSymbol;

    calldataarg args;
    address user;
    address reward;
    
  
    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    require isRegisteredRewardToken(reward); //todo: review assumption
 

    initialize(e, newAToken, staticATokenName, staticATokenSymbol);
    //assume a single reward
    //todo: allow multiple rewards
    require reward == _DummyERC20_rewardToken;
    require newAToken == _AToken;
    require getRewardTokensLength() == 1;
    require getRewardToken(0) == _DummyERC20_rewardToken;
    setup(e, user, user);    
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}
//todo: remove
//pass
rule getClaimableRewards_stable_after_refreshRewardTokens()
{

    env e;
    address user;
    address reward;
    require isRegisteredRewardToken(reward); //todo: review assumption

    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    refreshRewardTokens(e);

    setup(e, user, user);    

    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}


/// @title The amount of rewards that was actually received by claimRewards() cannot exceed the initial amount of rewards
rule getClaimableRewardsBefore_leq_claimed_claimRewardsOnBehalf(method f)
{   
    env e;
    address onBehalfOf;
    address receiver; 
    address my_reward;
    address[] rewards;
    //setup(e, onBehalfOf, receiver);   
    
    mathint balanceBefore = _DummyERC20_rewardToken.balanceOf(onBehalfOf);
    mathint claimableRewardsBefore = getClaimableRewards(e, onBehalfOf, my_reward);
    claimRewardsOnBehalf(e, onBehalfOf, receiver, rewards);
    mathint balanceAfter = _DummyERC20_rewardToken.balanceOf(onBehalfOf);
    mathint deltaBalance = balanceAfter - balanceBefore;
   
    assert deltaBalance <= claimableRewardsBefore;
}





rule sanity(method f)
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}


//
// Examples for development
//keep these rules until a Jira ticket is opened
//

rule sanity_metaDeposit    ()
{
	env e;
	calldataarg args;
	metaDeposit(e,args);
	assert false;
}
rule sanity_metaWithdraw()
{
	env e;
	calldataarg args;
	metaWithdraw(e,args);
	assert false;
}

rule getClaimableRewards_stable_after_metaWithdraw(){

    env e;
    calldataarg args;
    address user;
    address reward;

    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    metaWithdraw(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;

}

rule getClaimableRewards_stable_after_withdraw(){

    env e;
    calldataarg args;
    address user;
    address reward;

    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    withdraw(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;

}


//     require totalSupply() <= _AToken.scaledTotalSupply();
//     require totalSupply() <= _AToken.totalSupply();
//     mathint oldInd;
//     mathint newInd;
//     oldInd, newInd = _RewardsController.getAssetIndex(e, _AToken, _DummyERC20_rewardToken);
//     require oldInd >= 1;

//     mathint oldIndRewCtrl;
//     mathint newIndRewCtrl;
//     oldIndRewCtrl, newIndRewCtrl = _RewardsController.getAssetIndex(e, _AToken, _RewardsController);
//     require oldIndRewCtrl >= 1;



// rule getClaimableRewards_after_claimRewardsToSelf()
// {
//     env e;
//     claimRewardsToSelf(e);
//     mathint claimableRewardsAfter = getClaimableRewards(e, e.msg.sender);
//     assert claimableRewardsAfter == 0;
// }

