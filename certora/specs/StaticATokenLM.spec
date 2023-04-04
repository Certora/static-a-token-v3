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
    convertToAssets(uint256) returns (uint256) envfree
    convertToShares(uint256) returns (uint256) envfree

    getRewardTokensLength() returns (uint256) envfree 
    getRewardToken(uint256) returns (address) envfree
    isRegisteredRewardToken(address) envfree
    getRewardsIndexOnLastInteraction(address,address) returns (uint128) envfree

	_AToken.balanceOf(address) returns (uint256) envfree
    _AToken.scaledTotalSupply() returns (uint256) envfree
    _AToken.scaledBalanceOf(address) returns (uint256) envfree


    
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


//fail
//todo: check if property should hold
//https://vaas-stg.certora.com/output/99352/5521be2ec21640feb23be9d8b1faa08a/?anonymousKey=e2a56ad93292b812fb66afa29a0ae8fcf53b4f37
//https://vaas-stg.certora.com/output/99352/c288ca4de50e4f7ab76bfa70fac1c7ff/?anonymousKey=9cf2d1fb28a3b4f47b952eae91f3d330ea346181
invariant solvency_user_balance_leq_total_asset_CASE_SPLIT_redeem_in_shares_4(address user)
    balanceOf(user) <= _AToken.scaledBalanceOf(currentContract)
    filtered { f -> f.selector == redeem(uint256,address,address,bool).selector}
    {
        preserved redeem(uint256 shares, address receiver, address owner, bool toUnderlying) with (env e1) {
            requireInvariant solvency_total_asset_geq_total_supply();
            require balanceOf(owner) <= totalSupply(); //todo: replace with requireInvariant
            require receiver != _AToken;
            require user != _SymbolicLendingPoolL1; // TODO: review !!!
        }
    }


invariant solvency_positive_total_supply_only_if_positive_asset()
    ((_AToken.scaledBalanceOf(currentContract) == 0) => (totalSupply() == 0))
    filtered { f -> f.selector != metaWithdraw(address,address,uint256,uint256,bool,uint256,(uint8,bytes32,bytes32)).selector }
    {
        preserved redeem(uint256 shares, address receiver, address owner, bool toUnderlying) with (env e1) {
            requireInvariant solvency_total_asset_geq_total_supply();
            require balanceOf(owner) <= totalSupply(); //todo: replace with requireInvariant
        }
        preserved redeem(uint256 shares, address receiver, address owner) with (env e2) {
            requireInvariant solvency_total_asset_geq_total_supply();
            require balanceOf(owner) <= totalSupply(); 
        }
        preserved withdraw(uint256 assets, address receiver, address owner)  with (env e3) {
            requireInvariant solvency_total_asset_geq_total_supply();
            require balanceOf(owner) <= totalSupply(); 
        }

    }



// //fail if e1.msg.sender == currentContract
// //https://vaas-stg.certora.com/output/99352/83c1362989b540658dd72714c68f4f6a/?anonymousKey=00b5efbeb76fc09cbb12b5c0a53248703a16f5fe
// //https://vaas-stg.certora.com/output/99352/a929ada034a5437ca001dd11b221038b/?anonymousKey=a90c16f056686fdd38110f16f6ec8f72a8d2062b
// invariant solvency_total_asset_geq_total_supply_CASE_SPLIT_deposit()
//     (_AToken.scaledBalanceOf(currentContract) >= totalSupply())
//     filtered { f -> f.selector == deposit(uint256,address).selector}
//     {
//         preserved deposit(uint256 assets, address receiver) with (env e1) {
//             require balanceOf(receiver) <= totalSupply(); //todo: replace with requireInvariant
//         }
//     }
// //pass
// invariant solvency_total_asset_geq_total_supply_CASE_SPLIT_deposit_2()
//     (_AToken.scaledBalanceOf(currentContract) >= totalSupply())
//     filtered { f -> f.selector == deposit(uint256,address).selector}
//     {
//         preserved deposit(uint256 assets, address receiver) with (env e1) {
//             require balanceOf(receiver) <= totalSupply(); //todo: replace with requireInvariant
//             require e1.msg.sender != currentContract;
//         }
//     }

// //fail on deposit
invariant solvency_total_asset_geq_total_supply()
    (_AToken.scaledBalanceOf(currentContract) >= totalSupply())
    filtered { f -> f.selector != metaWithdraw(address,address,uint256,uint256,bool,uint256,(uint8,bytes32,bytes32)).selector
                    && f.selector != redeem(uint256,address,address).selector}
    {
        preserved redeem(uint256 shares, address receiver, address owner, bool toUnderlying) with (env e1) {
            require balanceOf(owner) <= totalSupply(); //todo: replace with requireInvariant
        }
        preserved withdraw(uint256 assets, address receiver, address owner)  with (env e3) {
            require balanceOf(owner) <= totalSupply(); 
        }
        preserved deposit(uint256 assets, address receiver) with (env e4) {
            require balanceOf(receiver) <= totalSupply(); //todo: replace with requireInvariant
            require e4.msg.sender != currentContract; //todo: review
}
        preserved deposit(uint256 assets, address receiver,uint16 referralCode, bool fromUnderlying) with (env e5) {
            require balanceOf(receiver) <= totalSupply(); //todo: replace with requireInvariant
            require e5.msg.sender != currentContract; //todo: review
        }
        preserved mint(uint256 shares, address receiver) with (env e6) {
            require balanceOf(receiver) <= totalSupply(); //todo: replace with requireInvariant
            require e6.msg.sender != currentContract; //todo: review
        }
        
    }

//timeout
//https://vaas-stg.certora.com/output/99352/cf6f23d546ed4834ae27bc4de2df81d7/?anonymousKey=a0ab74898224e42db0ef4770909848880d61abaa
invariant solvency_total_asset_geq_total_supply_CASE_SPLIT_redeem()
    (_AToken.scaledBalanceOf(currentContract) >= totalSupply())
    filtered { f -> f.selector == redeem(uint256,address,address).selector}
    {
        preserved redeem(uint256 shares, address receiver, address owner) with (env e2) {
            require balanceOf(owner) <= totalSupply(); 
        }
        preserved withdraw(uint256 assets, address receiver, address owner)  with (env e3) {
            require balanceOf(owner) <= totalSupply(); 
        }
    }
    
/// @title Assumptions that should hold in any run
/// @dev Assume that the memory was configured by calling RewardsController.configureAssets(RewardsDataTypes.RewardsConfigInput[] memory rewardsInput) 
function setup(env e, address user)
{
    require getRewardTokensLength() > 0;

    require _RewardsController.getAvailableRewardsCount(_AToken)  > 0;
    require _RewardsController.getRewardsByAsset(_AToken, 0) == _DummyERC20_rewardToken;

    require currentContract != e.msg.sender;
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
// rule totalClaimableRewards_stable(method f)
//     filtered { f -> !f.isView && !claimFunctions(f)  && f.selector != initialize(address,string,string).selector  }
// {
//     env e;
//     require e.msg.sender != currentContract;
//     setup(e, 0);
//     calldataarg args;
//     address reward;
//     require e.msg.sender != reward;
//     require currentContract != e.msg.sender;
//     require _AToken != e.msg.sender;
//     require _RewardsController != e.msg.sender;
//     require _DummyERC20_aTokenUnderlying  != e.msg.sender;
//     require _DummyERC20_rewardToken != e.msg.sender;
//     require _SymbolicLendingPoolL1 != e.msg.sender;
//     require _TransferStrategy != e.msg.sender;
//     require _ScaledBalanceToken != e.msg.sender;
    
//     require currentContract != reward;
//     require _AToken != reward;
//     require _RewardsController !=  reward;
//     require _DummyERC20_aTokenUnderlying  != reward;
//     require _SymbolicLendingPoolL1 != reward;
//     require _TransferStrategy != reward;
//     require _ScaledBalanceToken != reward;
//     require _TransferStrategy != reward;


//     mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
//     f(e, args); 
//     mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
//     assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
// }

// rule totalClaimableRewards_stable_less_requires_6(method f)
//     filtered { f -> !f.isView && !claimFunctions(f)  && f.selector != initialize(address,string,string).selector  }
// {
//     env e;
//     require e.msg.sender != currentContract;
//     setup(e, 0);
//     calldataarg args;
//     address reward;
//     require e.msg.sender != reward;
//     require currentContract != e.msg.sender;
//      require _RewardsController != e.msg.sender;
    
//     require currentContract != reward;
//     require _DummyERC20_aTokenUnderlying  != reward;
    

//     mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
//     f(e, args); 
//     mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
//     assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
// }
//
// 
rule totalClaimableRewards_stable_less_requires_7(method f)
    filtered { f -> !f.isView && !claimFunctions(f)
                    && f.selector != initialize(address,string,string).selector 
                    && f.selector != redeem(uint256,address,address,bool).selector 
                    && f.selector != redeem(uint256,address,address).selector 
                    && f.selector != withdraw(uint256,address,address).selector 
                    && f.selector != deposit(uint256,address).selector 
                    && f.selector != mint(uint256,address).selector 
                    && f.selector != metaWithdraw(address,address,uint256,uint256,bool,uint256,(uint8,bytes32,bytes32)).selector 
                    && f.selector !=claimSingleRewardOnBehalf(address,address,address).selector 
                    }
{
    env e;
    require e.msg.sender != currentContract;
    setup(e, 0);
    calldataarg args;
    address reward;
    require e.msg.sender != reward;
    require _ScaledBalanceToken != reward;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    
    require currentContract != reward;
    
    mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    f(e, args); 
    mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
}


//timeout
//https://vaas-stg.certora.com/output/99352/e755cdb34d84406ab17a782c4ffd6954/?anonymousKey=2efcab1e1dd4ea504c315b148b42ef3cec8acaa7
rule totalClaimableRewards_stable_less_requires_7_CASE_SPLIT_redeem(method f)
    filtered { f -> f.selector == redeem(uint256,address,address,bool).selector  }
{
    env e;
    require e.msg.sender != currentContract;
    setup(e, 0);
    calldataarg args;
    address reward;
    require e.msg.sender != reward;
    require _ScaledBalanceToken != reward;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    
    require currentContract != reward;
    
    mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    f(e, args); 
    mathint totalClaimableRewardsAfter = getTotalClaimableRewards(e, reward);
    assert totalClaimableRewardsAfter == totalClaimableRewardsBefore;
}


//timeout
//https://vaas-stg.certora.com/output/99352/bee8d3a583c549e195c0f755bb804b34/?anonymousKey=4b9e6f6791ede0049659d54a07db5e0f146b4a42
rule totalClaimableRewards_stable_less_requires_7_CASE_SPLIT_deposit(method f)
    filtered { f -> f.selector == deposit(uint256,address).selector  }
{
    env e;
    require e.msg.sender != currentContract;
    setup(e, 0);
    calldataarg args;
    address reward;
    require e.msg.sender != reward;
    require _ScaledBalanceToken != reward;
    require _AToken != e.msg.sender;
    require _RewardsController != e.msg.sender;
    
    require currentContract != reward;
    
    mathint totalClaimableRewardsBefore = getTotalClaimableRewards(e, reward);
    f(e, args); 
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
    require _RewardsController.getAvailableRewardsCount(_AToken)  > 0; //todo: review
    require _RewardsController.getRewardsByAsset(_AToken, 0) == reward; //todo: review
    f(e, args); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}
//timeout
rule getClaimableRewards_stable_6(method f)
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
    
    // require currentContract != user;
    // require _AToken != user;
    // require _RewardsController !=  user;
    // require _DummyERC20_aTokenUnderlying  != user;
    // require _DummyERC20_rewardToken != user;
    // require _SymbolicLendingPoolL1 != user;
    // require _TransferStrategy != user;
    // require _ScaledBalanceToken != user;
    
    // require currentContract != reward;
    // require _AToken != reward;
    // require _RewardsController !=  reward; //
    // require _DummyERC20_aTokenUnderlying  != reward;
    // require _SymbolicLendingPoolL1 != reward; 
    // require _TransferStrategy != reward;
    // require _ScaledBalanceToken != reward;
    
    //require isRegisteredRewardToken(reward); //todo: review the assumption
 
    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);

    require getRewardTokensLength() > 0;
    require getRewardToken(0) == reward; //todo: review
    require _RewardsController.getAvailableRewardsCount(_AToken)  > 0; //todo: review
    require _RewardsController.getRewardsByAsset(_AToken, 0) == reward; //todo: review
    f(e, args); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}

//timeout
rule getClaimableRewards_stable_4(method f)
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
    
    // require currentContract != user;
    // require _AToken != user;
    // require _RewardsController !=  user;
    // require _DummyERC20_aTokenUnderlying  != user;
    // require _DummyERC20_rewardToken != user;
    // require _SymbolicLendingPoolL1 != user;
    // require _TransferStrategy != user;
    // require _ScaledBalanceToken != user;
    
    //to improve run time
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
    require _RewardsController.getAvailableRewardsCount(_AToken)  > 0; //todo: review
    require _RewardsController.getRewardsByAsset(_AToken, 0) == reward; //todo: review
    f(e, args); 
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}


//pass
rule getClaimableRewards_stable_after_deposit()
{
    env e;
    address user;
    address reward;
    
    uint256 assets;
    address recipient;
    uint16 referralCode;
    bool fromUnderlying;

    require user != 0;

    
    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    require getRewardTokensLength() > 0;
    require getRewardToken(0) == reward; //todo: review

    require _RewardsController.getAvailableRewardsCount(_AToken)  > 0; //todo: review
    require _RewardsController.getRewardsByAsset(_AToken, 0) == reward; //todo: review
    deposit(e, assets, recipient,referralCode,fromUnderlying);
    mathint claimableRewardsAfter = getClaimableRewards(e, user, reward);
    assert claimableRewardsAfter == claimableRewardsBefore;
}


 
//todo: remove
//pass with --loop_iter=2 --rule_sanity basic
//https://vaas-stg.certora.com/output/99352/290a1108baa64316ac4f20b5501b4617/?anonymousKey=930379a90af5aa498ec3fed2110a08f5c096efb3
/// @title getClaimableRewards() is stable unless rewards were claimed
rule getClaimableRewards_stable_after_refreshRewardTokens()
{

    env e;
    address user;
    address reward;

    mathint claimableRewardsBefore = getClaimableRewards(e, user, reward);
    refreshRewardTokens(e);

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
    
    mathint balanceBefore = _DummyERC20_rewardToken.balanceOf(onBehalfOf);
    mathint claimableRewardsBefore = getClaimableRewards(e, onBehalfOf, my_reward);
    claimRewardsOnBehalf(e, onBehalfOf, receiver, rewards);
    mathint balanceAfter = _DummyERC20_rewardToken.balanceOf(onBehalfOf);
    mathint deltaBalance = balanceAfter - balanceBefore;
   
    assert deltaBalance <= claimableRewardsBefore;
}



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
