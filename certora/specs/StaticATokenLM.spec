import "erc20.spec"

using AToken as _AToken 
using RewardsControllerHarness as _RewardsController 
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 
using DummyERC20_rewardToken as _DummyERC20_rewardToken 
using SymbolicLendingPoolL1 as _SymbolicLendingPoolL1 
using TransferStrategyHarness as _TransferStrategyHarness
using StaticATokenLM as _StaticATokenLM

methods
{

    totalSupply() returns uint256 envfree
	balanceOf(address) returns (uint256) envfree
    _AToken.totalSupply() returns uint256 envfree
	_AToken.balanceOf(address) returns (uint256) envfree
	_AToken.scaledTotalSupply() returns (uint256) envfree
    _AToken.scaledBalanceOf(address) returns (uint256) envfree
    _RewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
    _RewardsController.getDistributionEnd(address, address)  returns (uint256) envfree
    _RewardsController.getFirstRewardsByAsset(address) returns (address ) envfree

    /*******************
    *     Pool.sol     *
    ********************/
    // can we assume a fixed index? 1 ray?
//    getReserveNormalizedIncome(address) returns (uint256) => DISPATCHER(true)
//    getReserveNormalizedIncome(address) returns (uint256) => ALWAYS(1000000000000000000000000000)

    //in RewardsDistributor.sol called by RewardsController.sol
    getAssetIndex(address, address) returns (uint256, uint256) =>  DISPATCHER(true)
    //deposit(address,uint256,address,uint16) => DISPATCHER(true)
    //withdraw(address,uint256,address) returns (uint256) => DISPATCHER(true)
    finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

    //in ScaledBalanceTokenBase.sol called by getAssetIndex
    scaledTotalSupply() returns (uint256) envfree => DISPATCHER(true) 
    
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
    //handleAction(address,uint256,uint256) => DISPATCHER(true)

    // called by  StaticATokenLM.claimRewardsToSelf  -->  RewardsController._getUserAssetBalances
    // get balanceOf and totalSupply of _aToken
    // todo - link to the actual token.
    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => NONDET

    // called by StaticATokenLM.collectAndUpdateRewards --> RewardsController._transferRewards()
    //implemented as simple transfer() in TransferStrategyHarness
    performTransfer(address,address,uint256) returns (bool) =>  DISPATCHER(true)

 }


definition claimFunctions(method f) returns bool = 
            f.selector == claimRewardsToSelf().selector ||
            f.selector == claimRewards(address).selector ||
            f.selector ==claimRewardsOnBehalf(address,address).selector ||
            f.selector == collectAndUpdateRewards().selector;



/**
 * @title Sum of balances of underlying asset 
 **/
ghost sumAllBalance() returns mathint {
    init_state axiom sumAllBalance() == 0;
}

hook Sstore balanceOf[KEY address a] uint256 balance (uint256 old_balance) STORAGE {
  havoc sumAllBalance assuming sumAllBalance@new() == sumAllBalance@old() + balance - old_balance;
}

hook Sload uint256 balance balanceOf[KEY address a] STORAGE {
    require balance <= sumAllBalance();
} 

ghost sumAllATokenScaledBalance() returns mathint {
    init_state axiom sumAllATokenScaledBalance() == 0;
}

hook Sstore _AToken._userState[KEY address a] .(offset 0) uint128 balance (uint128 old_balance) STORAGE {
  havoc sumAllATokenScaledBalance assuming sumAllATokenScaledBalance@new() == sumAllATokenScaledBalance@old() + balance - old_balance;
}

hook Sload uint128 balance _AToken._userState[KEY address a] .(offset 0) STORAGE {
    require balance <= sumAllATokenScaledBalance();
} 



// INV #2
/**
* @title User's balance not greater than totalSupply()
*/
//pass
invariant inv_balanceOf_leq_totalSupply(address user)
	balanceOf(user) <= totalSupply()
	{
		preserved {
			requireInvariant sumAllBalance_eq_totalSupply();
		}
	}

//fail on deposit and redeem
//https://vaas-stg.certora.com/output/99352/6355b694cd684e979531ae94b1e67adb/?anonymousKey=eb3d06c220ab788ba118e7152814b3ed8dc20bd5
invariant inv_atoken_balanceOf_leq_totalSupply(address user)
	_AToken.balanceOf(user) <= _AToken.totalSupply()
    {
		preserved with (env e){
			requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
            setup(e, user, user);
            requireInvariant inv_atoken_scaled_balanceOf_leq_totalSupply(user);
		}
	}

invariant inv_atoken_balanceOf_2users_leq_totalSupply(address user1, address user2)
	(_AToken.balanceOf(user1) + _AToken.balanceOf(user2))<= _AToken.totalSupply()
    {
		preserved with (env e1){
			//requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
            setup(e1, user1, user2);
		}
        preserved redeem(uint256 shares, address receiver, address owner) with (env e2){
            require user1 != user2;
        	//requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
            //require _AToken.balanceOf(e2.msg.sender) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
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
//timeout (any inswx)
rule rule_atoken_balanceOf_leq_totalSupply_after_deposit()
{	
     env e;
    calldataarg args;
    address user;
    uint256 assets;
    address recipient;
    uint16 referralCode;
    bool fromUnderlying;

    requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
    setup(e, user, recipient);
    require _AToken.balanceOf(user) <= _AToken.totalSupply();
    require _AToken.balanceOf(recipient) <= _AToken.totalSupply();
    require (_AToken.balanceOf(user) + _AToken.balanceOf(recipient)) <= _AToken.totalSupply();
    
    deposit(e, assets, recipient, referralCode, fromUnderlying);
    assert _AToken.balanceOf(user) <= _AToken.totalSupply();
}

rule rule_atoken_balanceOf_leq_totalSupply_after_redeem()
{	
     env e;
    calldataarg args;
    address user;
    uint256 shares;
    address receiver;
    address owner;


    requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
    setup(e, user, receiver);
    setup(e, user, owner);
    require _AToken.balanceOf(user) <= _AToken.totalSupply();
    redeem(e, shares, receiver,owner);
    assert _AToken.balanceOf(user) <= _AToken.totalSupply();
}

//pass
invariant inv_atoken_scaled_balanceOf_leq_totalSupply(address user)
	_AToken.scaledBalanceOf(user) <= _AToken.scaledTotalSupply()
    {
		preserved {
			requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
		}
	}

//pass
invariant sumAllBalance_eq_totalSupply()
	sumAllBalance() == totalSupply()

    //pass
invariant sumAllATokenScaledBalance_eq_totalSupply()
	sumAllATokenScaledBalance() == _AToken.scaledTotalSupply()


function setup(env e, address user1, address user2)
{
    require _RewardsController.getAvailableRewardsCount(_AToken)  > 0;
    require _RewardsController.getFirstRewardsByAsset(_AToken) == _DummyERC20_rewardToken;

    require currentContract != e.msg.sender;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    require _DummyERC20_rewardToken != e.msg.sender;
    require _SymbolicLendingPoolL1 != e.msg.sender;
    require _TransferStrategyHarness != e.msg.sender;
    

    require currentContract != user1;
    require _AToken != user1;
    require _RewardsController !=  user1;
    require _DummyERC20_aTokenUnderlying  != user1;
    require _DummyERC20_rewardToken != user1;
    require _SymbolicLendingPoolL1 != user1;
    require _TransferStrategyHarness != user1;
   
    require currentContract != user2;
    require _AToken != user2;
    require _RewardsController !=  user2;
    require _DummyERC20_aTokenUnderlying != user2;
    require _DummyERC20_rewardToken  != user2;
    require _SymbolicLendingPoolL1 != user2;
    require _TransferStrategyHarness != user2;
}

rule getClaimableRewards_stable_after_transfer(){

    env e;
    address to;
    uint256 amount;

    address user;

    //todo: review assumption
//    require (to != 0);
//    require (e.msg.sender != 0);
    require user != 0;


    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    transfer(e, to, amount);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter == claimableRewardsBefore;

}

rule getClaimableRewards_stable_after_transfer_from(){

    env e;
    address from;
    address to;
    uint256 amount;

    address user;

//    require (from != 0);
//    require (to != 0);
    require user != 0;

    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    transferFrom(e, from, to, amount);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter == claimableRewardsBefore;

}


rule getClaimableRewards_stable_after_deposit(){

    env e;
    calldataarg args;
    address user;
    uint256 assets;
    address recipient;
    uint16 referralCode;
    bool fromUnderlying;

    setup(e, user, recipient);    
  
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    deposit(e, assets, recipient, referralCode, fromUnderlying); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter == claimableRewardsBefore;
}


rule getClaimableRewards_decrease_17(method f)
    filtered { f -> !f.isView && !claimFunctions(f) }{

    env e;
    calldataarg args;
    address user;
    
    require user != 0;
    setup(e, user, user);    
  
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    f(e, args); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter <= claimableRewardsBefore;
}

rule getClaimableRewards_increase_17(method f) filtered { f -> !f.isView && !claimFunctions(f) }
{

    env e;
    calldataarg args;
    address user;
    
    require user != 0;
    setup(e, user, user);    
  
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    f(e, args); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter >= claimableRewardsBefore;
}


rule getClaimableRewards_decrease_after_mint(){

    env e;
    calldataarg args;
    address user;
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    mint(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter <= claimableRewardsBefore;

}

rule getClaimableRewards_increase_after_mint(){

    env e;
    calldataarg args;
    address user;
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    mint(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter >= claimableRewardsBefore;

}

//fail
rule getClaimableRewards_is_zero(method f)
  filtered { f -> claimFunctions(f) }
{
    env e;
    calldataarg args;
    address user;
    f(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter == 0;

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

rule sanity_metawDeposit    ()
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
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    metaWithdraw(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter == claimableRewardsBefore;

}

rule getClaimableRewards_stable_after_withdraw(){

    env e;
    calldataarg args;
    address user;
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    withdraw(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
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
