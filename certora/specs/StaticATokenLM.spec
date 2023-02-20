import "erc20.spec"

methods
{

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

rule getClaimableRewards_stable_after_transfer(){

    env e;
    address to;
    uint256 amount;

    address user;

    require (to != 0);
    require (e.msg.sender != 0);

    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    transfer(e, to, amount);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter == claimableRewardsBefore;

}

//debug fail of deposit()
rule getClaimableRewards_decrease_after_mint(method f){

    env e;
    calldataarg args;
    address user;
    mathint claimableRewardsBefore = getClaimableRewards(e, user);
    mint(e, args);
    mathint claimableRewardsAfter = getClaimableRewards(e, user);
    assert claimableRewardsAfter <= claimableRewardsBefore;

}

rule getClaimableRewards_increase_after_mint(method f){

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
