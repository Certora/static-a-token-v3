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
    totalAssets() returns (uint256) envfree

    getRewardTokensLength() returns (uint256) envfree 
    getRewardToken(uint256) returns (address) envfree
    isRegisteredRewardToken(address) envfree
    getRewardsIndexOnLastInteraction(address,address) returns (uint128) envfree

	_AToken.balanceOf(address) returns (uint256) envfree

    
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
    _RewardsController.getRewardsIndex(address,address)returns (uint256) envfree 
    
    _DummyERC20_rewardToken.balanceOf(address) returns (uint256) envfree

    /*******************
    *     Pool.sol     *
    ********************/

    //getReserveNormalizedIncome(address) returns (uint256) => ALWAYS(1000000000000000000000000000)

    //Called by RewardsController.sol
    //Defined in RewardsDistributor.sol
    getAssetIndex(address, address) returns (uint256, uint256) =>  DISPATCHER(true)
    
    //Called by AToken.sol
    //Defined in SupplyLogic.sol
    finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

    //Called by getAssetIndex
    // Defined in ScaledBalanceTokenBase.sol
    scaledTotalSupply() returns (uint256) envfree => DISPATCHER(true) 
    

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

    //Called by IncentivizedERC20.sol and by StaticATokenLM.sol
    handleAction(address,uint256,uint256) => DISPATCHER(true)

    //Called by RewardsController.sol
    //Defined in ScaledBalanceTokenBase.sol
    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => DISPATCHER(true)

    //Called by RewardsController._transferRewards()
    //Defined in TransferStrategyHarness as simple transfer() 
    performTransfer(address,address,uint256) returns (bool) =>  DISPATCHER(true)

 }

/// @title Claim rewards methods
definition claimFunctions(method f) returns bool = 
            f.selector == claimRewardsToSelf(address[]).selector ||
            f.selector == claimRewards(address, address[]).selector ||
            f.selector ==claimRewardsOnBehalf(address, address,address[]).selector ||
            f.selector == collectAndUpdateRewards(address).selector;



// /// @title Reward hook
// /// @notice allows a single reward
// /// @dev todo: hook may be omitted
// hook Sload address reward _rewardTokens[INDEX  uint256 i] STORAGE {
//    require reward == _DummyERC20_rewardToken;
// } 


/// @title Sum of balances of StaticATokenLM 
ghost sumAllBalance() returns mathint {
    init_state axiom sumAllBalance() == 0;
}

hook Sstore balanceOf[KEY address a] uint256 balance (uint256 old_balance) STORAGE {
  havoc sumAllBalance assuming sumAllBalance@new() == sumAllBalance@old() + balance - old_balance;
}

// hook Sload uint256 balance balanceOf[KEY address a] STORAGE {
//     require balance <= sumAllBalance();
// } 

invariant solvency_1_CASE_SPLIT_redeem(address user)
    balanceOf(user) <= _AToken.balanceOf(currentContract)
    filtered { f -> f.selector == redeem(uint256,address,address,bool).selector}
    {
        preserved redeem(uint256 shares, address receiver, address owner, bool toUnderlying) with (env e1) {
            require balanceOf(owner) <= totalSupply(); //todo: replace with requireInvariant
        }
    }

invariant solvency_1(address user)
    balanceOf(user) <= _AToken.balanceOf(currentContract)

invariant solvency_2()
    ((totalAssets() == 0) => (totalSupply() == 0))

invariant solvency_2_CASE_SPLIT_redeem()
    ((totalAssets() == 0) => (totalSupply() == 0))
    filtered { f -> f.selector == redeem(uint256,address,address,bool).selector}
    {
        preserved redeem(uint256 shares, address receiver, address owner, bool toUnderlying) with (env e1) {
            require balanceOf(owner) <= totalSupply(); //todo: replace with requireInvariant
        }
    }

invariant solvency_2_CASE_SPLIT_mint()
    ((totalAssets() == 0) => (totalSupply() == 0))
    filtered { f -> f.selector == mint(uint256,address).selector}
    
invariant solvency_3()
    (totalAssets() >= totalSupply())


invariant solvency_3_CASE_SPLIT_redeem()
    (totalAssets() >= totalSupply())
    filtered { f -> f.selector == redeem(uint256,address,address,bool).selector}
    {
        preserved redeem(uint256 shares, address receiver, address owner, bool toUnderlying) with (env e1) {
            require balanceOf(owner) <= totalSupply(); //todo: replace with requireInvariant
        }
    }
    


/// @title a registered token in StaticATokenLM must exist in RewardsController._assets.[_atoken].availableRewards
/// @dev May fail becuase RewardsController can store the given reward at any index other than zero
//todo: check why it doesnt fail. it may fail with loop_iter=2
//error with --loop_iter=2 --rule_sanity basic
//https://vaas-stg.certora.com/output/99352/1719ac7a4e0943da9f9db0734696f14f/?anonymousKey=96f51b50dea2f5e8a6527b9817613207b7bacfdc

invariant registered_reward_exists_in_controller(address reward)
    (isRegisteredRewardToken(reward) =>  
    (_RewardsController.getAvailableRewardsCount(_AToken)  > 0
    && _RewardsController.getRewardsByAsset(_AToken, 0) == reward)) 
    filtered { f -> f.selector != initialize(address,string,string).selector }//Todo: remove filter and use preserved block when CERT-1706 is fixed
    {
        //preserved initialize(address newAToken,string staticATokenName, string staticATokenSymbol) {
        //     require newAToken == _AToken;
        // }
    }




/// @title Assumptions that should hold in any run
/// @dev Assume that the memory was configured by calling RewardsController.configureAssets(RewardsDataTypes.RewardsConfigInput[] memory rewardsInput) 
function setup(env e, address user)
{
    
    //assume a single reward
    require getRewardTokensLength() > 0;
//    require getRewardToken(0) == _DummyERC20_rewardToken;

    require _RewardsController.getAvailableRewardsCount(_AToken)  > 0;
    require _RewardsController.getRewardsByAsset(_AToken, 0) == _DummyERC20_rewardToken;

    require currentContract != e.msg.sender;
    // require _AToken != e.msg.sender;
    // require _RewardsController != e.msg.sender;
    // require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    // require _DummyERC20_rewardToken != e.msg.sender;
    // require _SymbolicLendingPoolL1 != e.msg.sender;
    // require _TransferStrategy != e.msg.sender;
    // require _ScaledBalanceToken != e.msg.sender;
    

    require currentContract != user;
    require _AToken != user;
    require _RewardsController !=  user;
    require _DummyERC20_aTokenUnderlying  != user;
    require _DummyERC20_rewardToken != user;
    require _SymbolicLendingPoolL1 != user;
    require _TransferStrategy != user;
    require _ScaledBalanceToken != user;
    require _TransferStrategy != user;
}

//pass
/// @title correct accrued value is fetched
/// @notice assume a single asset
//pass with rule_sanity basic except metaDeposit()
//https://vaas-stg.certora.com/output/99352/ab6c92a9f96d4327b52da331d634d3ab/?anonymousKey=abb27f614a8656e6e300ce21c517009cbe0c4d3a
//https://vaas-stg.certora.com/output/99352/d8c9a8bbea114d5caad43683b06d8ba0/?anonymousKey=a079d7f7dd44c47c05c866808c32235d56bca8e8
invariant singleAssetAccruedRewards(env e0, address asset, address reward, address user)
    ((_RewardsController.getAssetListLength() == 1 && _RewardsController.getAssetByIndex(0) == asset)
        => (_RewardsController.getUserAccruedReward(asset, reward, user) == _RewardsController.getUserAccruedRewards(reward, user)))
        {
            preserved with (env e1){
                setup(e1, user);
                require asset != _RewardsController;
                require asset != _TransferStrategy;
                require asset != _ScaledBalanceToken;
                require reward != _StaticATokenLM;
                require reward != _AToken;
                require reward != _ScaledBalanceToken;
                require reward != _TransferStrategy;
            }
        }



/// @title Claiming rewards should not affect totalAssets() 
//pass with --rule_sanity basic
//https://vaas-stg.certora.com/output/99352/4df615c845e2445b8657ece2db477ce5/?anonymousKey=76379915d60fc1056ed4e5b391c69cd5bba3cce0
rule totalAssets_stable(method f)
    filtered { f -> (f.selector == claimRewardsToSelf(address[]).selector ||
                    f.selector == claimRewards(address, address[]).selector ||
                    f.selector == claimRewardsOnBehalf(address, address,address[]).selector) }
{
    env e;
    calldataarg args;
    mathint totalAssetBefore = totalAssets();
    f(e, args); 
    mathint totalAssetAfter = totalAssets();
    assert totalAssetAfter == totalAssetBefore;
}

//pass
//https://vaas-stg.certora.com/output/99352/e67815032b314538b3eeca0fbd382ad6/?anonymousKey=b11c03daeef3c12990c8d5458335c4aab01bc673
/// @title Claiming rewards should not affect totalAssets() 
/// @dev case splitting
rule totalAssets_stable_after_collectAndUpdateRewards()
{
    env e;
    require _RewardsController.getRewardsByAsset(_AToken, 0) != _AToken;
    require _RewardsController.getUserAccruedReward(currentContract, _AToken, _AToken) ==0;
    address reward;
    mathint totalAssetBefore = totalAssets();
    collectAndUpdateRewards(e, reward); 
    mathint totalAssetAfter = totalAssets();
    assert totalAssetAfter == totalAssetBefore;
}


/// @title Receiving ATokens does not affect the amount of rewards fetched by collectAndUpdateRewards()
//pass
//timeout with rule_sanity 
//https://vaas-stg.certora.com/output/99352/7d2ce2bb69ad4d71b4a179daa08633e4/?anonymousKey=7446e8a015ea9aa79cbc542c10b932e04169a0ab
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

//timeout with rule_sanity
//https://vaas-stg.certora.com/output/99352/5fc909b8815c4cfbaddb61c2197e8663/?anonymousKey=e560e7071843fad5b3967eac0d22c81c77bb06bd
// timeout on mint, redeem, deposit, withdraw
/// @title getTotalClaimableRewards() is stable unless rewards were claimed
rule totalClaimableRewards_stable(method f)
    filtered { f -> !f.isView && !claimFunctions(f)  && f.selector != initialize(address,string,string).selector  }
{
    env e;
    require e.msg.sender != currentContract;
    setup(e, 0);
    calldataarg args;
    address reward;
    require e.msg.sender != reward;
    require currentContract != e.msg.sender;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    require _DummyERC20_rewardToken != e.msg.sender;
    require _SymbolicLendingPoolL1 != e.msg.sender;
    require _TransferStrategy != e.msg.sender;
    require _ScaledBalanceToken != e.msg.sender;
    
    require currentContract != reward;
    require _AToken != reward;
    require _RewardsController !=  reward;
    require _DummyERC20_aTokenUnderlying  != reward;
    require _SymbolicLendingPoolL1 != reward;
    require _TransferStrategy != reward;
    require _ScaledBalanceToken != reward;
    require _TransferStrategy != reward;


    mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    f(e, args); 
    mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
}


//should fail
//timeout
//timeout with rule_sanity
//https://vaas-stg.certora.com/output/99352/b7649460e64f4bee991a0a480b6240ee/?anonymousKey=36b52f602c157e15e357b5f0202ed5cb42d38771
rule totalClaimableRewards_stable_SANITY(method f)
    filtered { f -> f.selector == claimRewardsOnBehalf(address, address,address[]).selector   }
{
    env e;
    require e.msg.sender != currentContract;
    setup(e, 0);
    calldataarg args;
    address reward;
    require e.msg.sender != reward;
    require currentContract != e.msg.sender;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    require _DummyERC20_rewardToken != e.msg.sender;
    require _SymbolicLendingPoolL1 != e.msg.sender;
    require _TransferStrategy != e.msg.sender;
    require _ScaledBalanceToken != e.msg.sender;
    
    require currentContract != reward;
    require _AToken != reward;
    require _RewardsController !=  reward;
    require _DummyERC20_aTokenUnderlying  != reward;
    require _SymbolicLendingPoolL1 != reward;
    require _TransferStrategy != reward;
    require _ScaledBalanceToken != reward;
    require _TransferStrategy != reward;


    mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    f(e, args); 
    mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
}


//fail
//totalClaimableRewards_stable_after_initialized
/// @title getTotalClaimableRewards() is stable after initialized()
rule totalClaimableRewards_stable_after_initialized()
{
    env e;
    require e.msg.sender != currentContract;
    setup(e, 0);
    calldataarg args;
    address reward;


    require e.msg.sender != reward;
 
    require currentContract != e.msg.sender;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    require _DummyERC20_rewardToken != e.msg.sender;
    require _SymbolicLendingPoolL1 != e.msg.sender;
    require _TransferStrategy != e.msg.sender;
    require _ScaledBalanceToken != e.msg.sender;
    
    require currentContract != reward;
    require _AToken != reward;
    require _RewardsController !=  reward;
    require _DummyERC20_aTokenUnderlying  != reward;
    require _SymbolicLendingPoolL1 != reward;
    require _TransferStrategy != reward;
    require _ScaledBalanceToken != reward;
    require _TransferStrategy != reward;

    address newAToken;
    string staticATokenName;
    string staticATokenSymbol;

    mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    initialize(e, newAToken, staticATokenName, staticATokenSymbol);
    mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
}

//todo: add separate rules for redeem, mint
//pass with rule_sanity basic, except metaDeposit, timeout withdraw(uint256,address,address)
//https://vaas-stg.certora.com/output/99352/ee42e7f2603740de96a8a0aaf7c676ff/?anonymousKey=f7aaa1b8ed030a8f600136ec0b94ae0bc81a0e0c
//pass
//https://vaas-stg.certora.com/output/99352/109a4a815a9a4c3abcee760bf77c5f7d/?anonymousKey=f215580ed8e698028fdedecf096752c7a3e9363c
rule getClaimableRewards_stable(method f)
    filtered { f -> !f.isView
                    && !claimFunctions(f)
                    && f.selector != initialize(address,string,string).selector
                    && f.selector != deposit(uint256,address,uint16,bool).selector
                    && f.selector != redeem(uint256,address,address).selector
                    && f.selector != redeem(uint256,address,address,bool).selector
                    && f.selector != mint(uint256,address).selector
                    && f.selector != metaWithdraw(address,address,uint256,uint256,bool,uint256,(uint8,bytes32,bytes32)).selector
    }
{
    env e;
    calldataarg args;
    address user;
    address reward;
 
    require user != 0;

    // require currentContract != e.msg.sender;
    // require _AToken != e.msg.sender;
    // require _RewardsController != e.msg.sender;
    // require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    // require _DummyERC20_rewardToken != e.msg.sender;
    // require _SymbolicLendingPoolL1 != e.msg.sender;
    // require _TransferStrategy != e.msg.sender;
    // require _ScaledBalanceToken != e.msg.sender;
    
    require currentContract != user;
    require _AToken != user;
    require _RewardsController !=  user;
    require _DummyERC20_aTokenUnderlying  != user;
    require _DummyERC20_rewardToken != user;
    require _SymbolicLendingPoolL1 != user;
    require _TransferStrategy != user;
    require _ScaledBalanceToken != user;
    
    require currentContract != reward;
    require _AToken != reward;
    require _RewardsController !=  reward; //
    require _DummyERC20_aTokenUnderlying  != reward;
    require _SymbolicLendingPoolL1 != reward; 
    require _TransferStrategy != reward;
    require _ScaledBalanceToken != reward;
    
    //require isRegisteredRewardToken(reward); //todo: review the assumption
 
    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);

    require getRewardTokensLength() > 0;
    require getRewardToken(0) == reward; //todo: review
    requireInvariant registered_reward_exists_in_controller(reward); //todo: review. invariant is not proven
    f(e, args); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}

//fail
//https://vaas-stg.certora.com/output/99352/1135c805b86b4a269dc28d822c6d1871/?anonymousKey=2c5aa6cc2ec507b70793d0ccecefa1aa74c61db0
rule getClaimableRewards_stable_SANITY(method f)
    filtered { f -> //claimFunctions(f)
                    f.selector == claimRewardsOnBehalf(address, address,address[]).selector   
    }
{
    env e;
    calldataarg args;
    address user;
    address reward;
 
    require user != 0;

    require currentContract != e.msg.sender;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    require _DummyERC20_rewardToken != e.msg.sender;
    require _SymbolicLendingPoolL1 != e.msg.sender;
    require _TransferStrategy != e.msg.sender;
    require _ScaledBalanceToken != e.msg.sender;
    
    require currentContract != user;
    require _AToken != user;
    require _RewardsController !=  user;
    require _DummyERC20_aTokenUnderlying  != user;
    require _DummyERC20_rewardToken != user;
    require _SymbolicLendingPoolL1 != user;
    require _TransferStrategy != user;
    require _ScaledBalanceToken != user;
    
    require currentContract != reward;
    require _AToken != reward;
    require _RewardsController !=  reward; //
    require _DummyERC20_aTokenUnderlying  != reward;
    require _SymbolicLendingPoolL1 != reward; 
    require _TransferStrategy != reward;
    require _ScaledBalanceToken != reward;
    
    //require isRegisteredRewardToken(reward); //todo: review the assumption
 
    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);

    require getRewardTokensLength() > 0;
    require getRewardToken(0) == reward; //todo: review
    f(e, args); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}


//pass with rule_sanity basic
//https://vaas-stg.certora.com/output/99352/8c515f3691e74a3e987b6a46b4f58a90/?anonymousKey=046fb50a9835c09af77408c1621e8e664669e031
rule getClaimableRewards_stable_after_deposit()
{
    env e;
    address user;
    address reward;
    // require currentContract != e.msg.sender;
    // require _AToken != e.msg.sender;
    // require _RewardsController != e.msg.sender;
    // require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    // require _DummyERC20_rewardToken != e.msg.sender;
    // require _SymbolicLendingPoolL1 != e.msg.sender;
    // require _TransferStrategy != e.msg.sender;
    // require _ScaledBalanceToken != e.msg.sender;
    
    uint256 assets;
    address recipient;
    uint16 referralCode;
    bool fromUnderlying;

    require user != 0;

    require currentContract != user;
    require _AToken != user;
    require _RewardsController !=  user;
    require _DummyERC20_aTokenUnderlying  != user;
    require _DummyERC20_rewardToken != user;
    require _SymbolicLendingPoolL1 != user;
    require _TransferStrategy != user;
    require _ScaledBalanceToken != user;
    
    require currentContract != recipient;
    require _AToken != recipient;
    require _RewardsController !=  recipient;
    require _DummyERC20_aTokenUnderlying  != recipient;
    require _DummyERC20_rewardToken != recipient;
    require _SymbolicLendingPoolL1 != recipient; //
    require _TransferStrategy != recipient;
    require _ScaledBalanceToken != recipient;
    
    require currentContract != reward;
    require _AToken != reward;
    require _RewardsController !=  reward; //
    require _DummyERC20_aTokenUnderlying  != reward;
    require _SymbolicLendingPoolL1 != reward; 
    require _TransferStrategy != reward;
    require _ScaledBalanceToken != reward;
    
    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    require getRewardTokensLength() > 0;
    require getRewardToken(0) == reward; //todo: review

    requireInvariant registered_reward_exists_in_controller(reward); //todo: review, unproven invariant
    deposit(e, assets, recipient,referralCode,fromUnderlying);
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}


//fail as expected
//https://vaas-stg.certora.com/output/99352/1135c805b86b4a269dc28d822c6d1871/?anonymousKey=2c5aa6cc2ec507b70793d0ccecefa1aa74c61db0
//todo: verify the fail root-cause
rule getClaimableRewards_stable_after_deposit_SANITY()
{
    env e;
    address user;
    address reward;
    require currentContract != e.msg.sender;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    require _DummyERC20_aTokenUnderlying  != e.msg.sender;
    require _DummyERC20_rewardToken != e.msg.sender;
    require _SymbolicLendingPoolL1 != e.msg.sender;
    require _TransferStrategy != e.msg.sender;
    require _ScaledBalanceToken != e.msg.sender;
    
    uint256 assets;
    address recipient;
    uint16 referralCode;
    bool fromUnderlying;

    require user != 0;

    require currentContract != user;
    require _AToken != user;
    require _RewardsController !=  user;
    require _DummyERC20_aTokenUnderlying  != user;
    require _DummyERC20_rewardToken != user;
    require _SymbolicLendingPoolL1 != user;
    require _TransferStrategy != user;
    require _ScaledBalanceToken != user;
    
    require currentContract != recipient;
    require _AToken != recipient;
    require _RewardsController !=  recipient;
    require _DummyERC20_aTokenUnderlying  != recipient;
    require _DummyERC20_rewardToken != recipient;
    require _SymbolicLendingPoolL1 != recipient; //
    require _TransferStrategy != recipient;
    require _ScaledBalanceToken != recipient;
    
    require currentContract != reward;
    require _AToken != reward;
    require _RewardsController !=  reward; //
    require _DummyERC20_aTokenUnderlying  != reward;
    require _SymbolicLendingPoolL1 != reward; 
    require _TransferStrategy != reward;
    require _ScaledBalanceToken != reward;
    
    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    require getRewardTokensLength() > 0;
    //require getRewardToken(0) == reward; //todo: review
    
    deposit(e, assets, recipient,referralCode,fromUnderlying);
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}


// timeout
// timeout with rule_sanity
//https://vaas-stg.certora.com/output/99352/3a8f3cb41d244c7bbff58d03d6e933ca/?anonymousKey=991cd5e8f3ae50d167220adc04f2cff31b1e76ae
//todo: remove
/// @title getClaimableRewards() is stable unless rewards were claimed
/// @dev case splitting
rule getClaimableRewards_stable_after_atoken_transferFrom()
{
    env e;
    calldataarg args;
    address user;
    address reward;

    address sender;
    uint256 amount;
    
    require user != 0;
    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    _AToken.transferFrom(e, sender, currentContract, amount);
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}


// timeout
//timeout with rule sanity
//https://vaas-stg.certora.com/output/99352/fc7a6df8eaa04c9e80eb213e0c279ce9/?anonymousKey=80cca37444f2f933f7c28df9075cdb0cc3d575bc
//todo: remove
/// @title getClaimableRewards() is stable unless rewards were claimed
/// @dev case splitting, call setup()
rule getClaimableRewards_stable_after_atoken_transferFrom_1()
{
    env e;
    calldataarg args;
    address user;
    address reward;

    address sender;
    uint256 amount;
   // require isRegisteredRewardToken(reward); //todo: review the assumption
    require user != 0;
    setup(e, user);

    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    _AToken.transferFrom(e, sender, currentContract, amount);
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}
 
/// @title special case of rule getClaimableRewards_stable for initialize
//fail
//https://vaas-stg.certora.com/output/99352/e6d2c3c3eba84ff0adceacb6c4117a87/?anonymousKey=51ee72a41e2936755decbef08a134c348c368097
//todo: consider removing this rule. no method is called before initialize()
/// @title getClaimableRewards() is stable after initialize()
/// @dev case splitting
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
    require getRewardToken(0) == reward;
    setup(e, user);    
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}
//todo: remove
//pass with --loop_iter=2 --rule_sanity basic
//https://vaas-stg.certora.com/output/99352/290a1108baa64316ac4f20b5501b4617/?anonymousKey=930379a90af5aa498ec3fed2110a08f5c096efb3
/// @title getClaimableRewards() is stable unless rewards were claimed
/// @dev case splitting, call setup()
rule getClaimableRewards_stable_after_refreshRewardTokens()
{

    env e;
    address user;
    address reward;
    //require isRegisteredRewardToken(reward); //todo: review assumption

    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    refreshRewardTokens(e);

    //setup(e, user);    

    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}

// pass with rule_sanity
//https://vaas-stg.certora.com/output/99352/0bb74dd0bccd458597bd9bf79c26e98c/?anonymousKey=26ea39f49871aa2ecf8e076b534735a4cc9cfe7d
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



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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

