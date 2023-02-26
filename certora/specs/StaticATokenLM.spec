import "erc20.spec"

using AToken as _AToken 
using RewardsControllerHarness as _RewardsController 
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 
using DummyERC20_rewardToken as _DummyERC20_rewardToken 
using SymbolicLendingPoolL1 as _SymbolicLendingPoolL1 
using TransferStrategyHarness as _TransferStrategyHarness

methods
{

    totalSupply() returns uint256 envfree
	balanceOf(address) returns (uint256) envfree
    _AToken.totalSupply() returns uint256 envfree
	_AToken.balanceOf(address) returns (uint256) envfree
	_AToken.scaledTotalSupply() returns (uint256) envfree
    _AToken.scaledBalanceOf(address) returns (uint256) envfree
    _RewardsController.getavailableRewardsCount(address) returns (uint128) envfree
    _RewardsController.getDistributionEnd(address, address)  returns (uint256) envfree
    _RewardsController.getFirstRewardsByAsset(address) returns (address ) envfree

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

ghost sumAllATokenBalance() returns mathint {
    init_state axiom sumAllATokenBalance() == 0;
}

hook Sstore _AToken._userState[KEY address a] .(offset 0) uint128 balance (uint128 old_balance) STORAGE {
  havoc sumAllATokenBalance assuming sumAllATokenBalance@new() == sumAllATokenBalance@old() + balance - old_balance;
}

hook Sload uint128 balance _AToken._userState[KEY address a] .(offset 0) STORAGE {
    require balance <= sumAllATokenBalance();
} 


// INV #2
/**
* @title User's balance not greater than totalSupply()
*/
invariant inv_balanceOf_leq_totalSupply(address user)
	balanceOf(user) <= totalSupply()
	{
		preserved {
			requireInvariant sumAllBalance_eq_totalSupply();
		}
	}


invariant inv_atoken_balanceOf_leq_totalSupply(address user)
	_AToken.balanceOf(user) <= _AToken.totalSupply()
    {
		preserved {
			requireInvariant sumAllATokenBalance_eq_totalSupply();
		}
	}

invariant inv_atoken_scaled_balanceOf_leq_totalSupply(address user)
	_AToken.scaledBalanceOf(user) <= _AToken.scaledTotalSupply()

invariant sumAllBalance_eq_totalSupply()
	sumAllBalance() == totalSupply()
invariant sumAllATokenBalance_eq_totalSupply()
	sumAllATokenBalance() == _AToken.totalSupply()

rule getClaimableRewards_stable_after_transfer(){

    env e;
    address to;
    uint256 amount;

    address user;

    //todo: review assumption
    require (to != 0);
    require (e.msg.sender != 0);

    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    transfer(e, to, amount);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter == claimableRewardsBefore;

}

//under debugging
rule getClaimableRewards_decrease_after_deposit(method f){

    env e;
    calldataarg args;
    address user;
    uint256 assets;
    address recipient;
    uint16 referralCode;
    bool fromUnderlying;

    requireInvariant inv_balanceOf_leq_totalSupply(user);
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    deposit(e, assets, recipient, referralCode, fromUnderlying);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter <= claimableRewardsBefore;

}

rule getClaimableRewards_decrease_after_deposit_7(method f){

    env e;
    calldataarg args;
    address user;
    uint256 assets;
    address recipient;
    uint16 referralCode;
    bool fromUnderlying;

    mathint oldInd;
    mathint newInd;
    oldInd, newInd = _RewardsController.getAssetIndex(e, _AToken, _DummyERC20_rewardToken);
    require oldInd >= 1;

    mathint oldIndRewCtrl;
    mathint newIndRewCtrl;
    oldIndRewCtrl, newIndRewCtrl = _RewardsController.getAssetIndex(e, _AToken, _RewardsController);
    require oldIndRewCtrl >= 1;

    require (_RewardsController.getDistributionEnd(_AToken, _DummyERC20_rewardToken) > 0);
    require (_RewardsController.getDistributionEnd(_AToken, _RewardsController) > 0);
    require (_RewardsController.getDistributionEnd(_AToken, user) > 0);
    require (_RewardsController.getDistributionEnd(_AToken, recipient) > 0);




    require currentContract != e.msg.sender;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    require _DummyERC20_rewardToken  != e.msg.sender;
    require _SymbolicLendingPoolL1 != e.msg.sender;

    require currentContract != recipient;
    require _AToken != recipient;
    require _RewardsController !=  recipient;
    require _DummyERC20_aTokenUnderlying  != recipient;
    require _DummyERC20_rewardToken  != recipient;
    require _SymbolicLendingPoolL1 != recipient;

    require currentContract != user;
    require _AToken != user;
    require _RewardsController !=  user;
    require _DummyERC20_aTokenUnderlying  != user;
    require _DummyERC20_rewardToken  != user;
    require _SymbolicLendingPoolL1 != user;





    requireInvariant inv_balanceOf_leq_totalSupply(user);
    requireInvariant inv_balanceOf_leq_totalSupply(recipient);
    require ((balanceOf(user) + balanceOf(recipient) ) <= totalSupply());
    requireInvariant inv_atoken_balanceOf_leq_totalSupply(user);
    requireInvariant inv_atoken_balanceOf_leq_totalSupply(recipient);
    requireInvariant inv_atoken_balanceOf_leq_totalSupply(currentContract);
    require ((_AToken.balanceOf(user) + _AToken.balanceOf(recipient) + _AToken.balanceOf(currentContract) ) <= _AToken.totalSupply());
    requireInvariant inv_atoken_scaled_balanceOf_leq_totalSupply(user);
    requireInvariant inv_atoken_scaled_balanceOf_leq_totalSupply(recipient);
    requireInvariant inv_atoken_scaled_balanceOf_leq_totalSupply(currentContract);
    require ((_AToken.scaledBalanceOf(user) + _AToken.scaledBalanceOf(recipient) + _AToken.scaledBalanceOf(currentContract) ) <= _AToken.scaledTotalSupply());
    
    require totalSupply() <= _AToken.scaledTotalSupply();
    require totalSupply() <= _AToken.totalSupply();

    requireInvariant sumAllBalance_eq_totalSupply();
    requireInvariant sumAllATokenBalance_eq_totalSupply();

    require getUnclaimedRewards(e, user) == 0; 
    require getUnclaimedRewards(e, recipient) == 0; 
    
  
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    deposit(e, assets, recipient, referralCode, fromUnderlying); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter <= claimableRewardsBefore;

}


//bug report sent to customer Feb. 21 , 2023
rule getClaimableRewards_increase_after_deposit(method f){

    env e;
    calldataarg args;
    address user;
    uint256 assets;
    address recipient;
    uint16 referralCode;
    bool fromUnderlying;

    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    deposit(e, assets, recipient, referralCode, fromUnderlying); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter >= claimableRewardsBefore;

}


//counter example sent to customer on Feb, 23, 2023
rule getClaimableRewards_increase_after_deposit_7(method f){

    env e;
    calldataarg args;
    address user;
    uint256 assets;
    address recipient;
    uint16 referralCode;
    bool fromUnderlying;

    require currentContract != e.msg.sender;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;


    requireInvariant inv_balanceOf_leq_totalSupply(user);
    requireInvariant inv_balanceOf_leq_totalSupply(recipient);
    require ((balanceOf(user) + balanceOf(recipient) ) <= totalSupply());
    requireInvariant inv_atoken_balanceOf_leq_totalSupply(user);
    requireInvariant inv_atoken_balanceOf_leq_totalSupply(recipient);
    requireInvariant inv_atoken_balanceOf_leq_totalSupply(currentContract);
    require ((_AToken.balanceOf(user) + _AToken.balanceOf(recipient) + _AToken.balanceOf(currentContract) ) <= _AToken.totalSupply());
    requireInvariant inv_atoken_scaled_balanceOf_leq_totalSupply(user);
    requireInvariant inv_atoken_scaled_balanceOf_leq_totalSupply(recipient);
    requireInvariant inv_atoken_scaled_balanceOf_leq_totalSupply(currentContract);
    require ((_AToken.scaledBalanceOf(user) + _AToken.scaledBalanceOf(recipient) + _AToken.scaledBalanceOf(currentContract) ) <= _AToken.scaledTotalSupply());
    
    require totalSupply() <= _AToken.scaledTotalSupply();
    require totalSupply() <= _AToken.totalSupply();

    requireInvariant sumAllBalance_eq_totalSupply();
    requireInvariant sumAllATokenBalance_eq_totalSupply();

    require getUnclaimedRewards(e, user) == 0; 
    require getUnclaimedRewards(e, recipient) == 0; 
    
  
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    deposit(e, assets, recipient, referralCode, fromUnderlying); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter >= claimableRewardsBefore;

}

rule getClaimableRewards_increase_after_deposit_8(method f){

    env e;
    calldataarg args;
    address user;
    uint256 assets;
    address recipient;
    uint16 referralCode;
    bool fromUnderlying;

    
    mathint oldInd;
    mathint newInd;
    oldInd, newInd = _RewardsController.getAssetIndex(e, _AToken, _DummyERC20_rewardToken);
    require oldInd >= 1;
   require (_RewardsController.getavailableRewardsCount(_AToken) ) > 0;

     mathint oldIndRewCtrl;
    mathint newIndRewCtrl;
    oldIndRewCtrl, newIndRewCtrl = _RewardsController.getAssetIndex(e, _AToken, _RewardsController);
    require oldIndRewCtrl >= 1;

    address availableFirstRewards = _RewardsController.getFirstRewardsByAsset(_AToken);
    require (availableFirstRewards == _DummyERC20_rewardToken);

    require (_RewardsController.getDistributionEnd(_AToken, _DummyERC20_rewardToken) > 0);
    require (_RewardsController.getDistributionEnd(_AToken, _RewardsController) > 0);
    require (_RewardsController.getDistributionEnd(_AToken, user) > 0);
    require (_RewardsController.getDistributionEnd(_AToken, recipient) > 0);

    require currentContract != e.msg.sender;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    require _DummyERC20_rewardToken  != e.msg.sender;
    require _SymbolicLendingPoolL1 != e.msg.sender;
    require _TransferStrategyHarness != e.msg.sender;
    

    require currentContract != recipient;
    require _AToken != recipient;
    require _RewardsController !=  recipient;
    require _DummyERC20_aTokenUnderlying  != recipient;
    require _DummyERC20_rewardToken  != recipient;
    require _SymbolicLendingPoolL1 != recipient;
    require _TransferStrategyHarness != recipient;
   
    require currentContract != user;
    require _AToken != user;
    require _RewardsController !=  user;
    require _DummyERC20_aTokenUnderlying  != user;
    require _DummyERC20_rewardToken  != user;
    require _SymbolicLendingPoolL1 != user;
    require _TransferStrategyHarness != user;
   

    requireInvariant inv_balanceOf_leq_totalSupply(user);
    requireInvariant inv_balanceOf_leq_totalSupply(recipient);
    require ((balanceOf(user) + balanceOf(recipient) ) <= totalSupply());
    requireInvariant inv_atoken_balanceOf_leq_totalSupply(user);
    requireInvariant inv_atoken_balanceOf_leq_totalSupply(recipient);
    requireInvariant inv_atoken_balanceOf_leq_totalSupply(currentContract);
    require ((_AToken.balanceOf(user) + _AToken.balanceOf(recipient) + _AToken.balanceOf(currentContract) ) <= _AToken.totalSupply());
    requireInvariant inv_atoken_scaled_balanceOf_leq_totalSupply(user);
    requireInvariant inv_atoken_scaled_balanceOf_leq_totalSupply(recipient);
    requireInvariant inv_atoken_scaled_balanceOf_leq_totalSupply(currentContract);
    require ((_AToken.scaledBalanceOf(user) + _AToken.scaledBalanceOf(recipient) + _AToken.scaledBalanceOf(currentContract) ) <= _AToken.scaledTotalSupply());
    
    require totalSupply() <= _AToken.scaledTotalSupply();
    require totalSupply() <= _AToken.totalSupply();

    requireInvariant sumAllBalance_eq_totalSupply();
    requireInvariant sumAllATokenBalance_eq_totalSupply();

    require getUnclaimedRewards(e, user) == 0; 
    require getUnclaimedRewards(e, recipient) == 0; 
    
  
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    deposit(e, assets, recipient, referralCode, fromUnderlying); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter >= claimableRewardsBefore;
   // assert false;
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
//under debug
rule getClaimableRewards_increase(method f){

    env e;
    calldataarg args;
    address user;
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    f(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter >= claimableRewardsBefore;

}
rule getClaimableRewards_stable(method f){

    env e;
    calldataarg args;
    address user;
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    f(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter == claimableRewardsBefore;

}
//under debug
rule getClaimableRewards_zero(method f){

    env e;
    calldataarg args;
    address user;
    f(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter == 0;

}

//debug fail of deposit()
rule getClaimableRewards_decrease(method f){

    env e;
    calldataarg args;
    address user;
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    f(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter <= claimableRewardsBefore;

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
