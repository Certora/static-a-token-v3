
import "methods_base.spec"

/////////////////// Methods ////////////////////////

    methods
    {
        permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET
    }

////////////////// FUNCTIONS //////////////////////

    /// @title Sum of scaled balances of AToken 
    ghost sumAllATokenScaledBalance() returns mathint {
        init_state axiom sumAllATokenScaledBalance() == 0;
    }


    /// @dev sample struct UserState {uint128 balance; uint128 additionalData; }
    hook Sstore _AToken._userState[KEY address a] .(offset 0) uint128 balance (uint128 old_balance) STORAGE {
    havoc sumAllATokenScaledBalance assuming sumAllATokenScaledBalance@new() == sumAllATokenScaledBalance@old() + balance - old_balance;
    }

    hook Sload uint128 balance _AToken._userState[KEY address a] .(offset 0) STORAGE {
        require balance <= sumAllATokenScaledBalance();
    } 

///////////////// Properties ///////////////////////

    /**
    * @title User AToken balance is fixed
    * Interaction with `StaticAtokenLM` should not change a user's AToken balance,
    * except for the following methods:
    * - `withdraw`
    * - `deposit`
    * - `redeem`
    * - `mint`
    * - `metaDeposit`
    * - `metaWithdraw`
    *
    * Note. Rewards methods are special cases handled in other rules below.
    *
    * Rules passed (with rule sanity): job-id=`5fdaf5eeaca249e584c2eef1d66d73c7`
    *
    * Note. `UNDERLYING_ASSET_ADDRESS()` was unresolved!
    */
    rule aTokenBalanceIsFixed(method f) filtered {
        // Exclude balance changing methods
        f -> (f.selector != deposit(uint256,address).selector) &&
            (f.selector != deposit(uint256,address,uint16,bool).selector) &&
            (f.selector != withdraw(uint256,address,address).selector) &&
            (f.selector != redeem(uint256,address,address).selector) &&
            (f.selector != redeem(uint256,address,address,bool).selector) &&
            (f.selector != mint(uint256,address).selector) &&
            (f.selector != metaDeposit(
                address,address,uint256,uint16,bool,uint256,
                (address,address,uint256,uint256,uint8,bytes32,bytes32),
                (uint8, bytes32, bytes32)
            ).selector) &&
            (f.selector != metaWithdraw(
                address,address,uint256,uint256,bool,uint256,
                (uint8, bytes32, bytes32)
            ).selector) &&
            // Exclude reward related methods - these are handled below
            (f.selector != collectAndUpdateRewards(address).selector) &&
            (f.selector != claimRewardsOnBehalf(address,address,address[]).selector) &&
            (f.selector != claimSingleRewardOnBehalf(address,address,address).selector) &&
            (f.selector != claimRewardsToSelf(address[]).selector) &&
            (f.selector != claimRewards(address,address[]).selector)
    } {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;

        env e;

        // Limit sender
        require e.msg.sender != currentContract;
        require e.msg.sender != _AToken;

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        calldataarg args;
        f(e, args);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by static interaction";
    }

    rule aTokenBalanceIsFixed_for_collectAndUpdateRewards() {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
        require _AToken != _DummyERC20_rewardToken;

        env e;

        // Limit sender
        require e.msg.sender != currentContract;
        require e.msg.sender != _AToken;
        require e.msg.sender != _DummyERC20_rewardToken;

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        collectAndUpdateRewards(e, _DummyERC20_rewardToken);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by collectAndUpdateRewards";
    }


    rule aTokenBalanceIsFixed_for_claimRewardsOnBehalf(address onBehalfOf, address receiver) {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
        require _AToken != _DummyERC20_rewardToken;

        // Create a rewards array
        address[] _rewards;
        require _rewards[0] == _DummyERC20_rewardToken;
        require _rewards.length == 1;

        env e;

        // Limit sender
        require (
            (e.msg.sender != currentContract) &&
            (onBehalfOf != currentContract) &&
            (receiver != currentContract)
        );
        require (
            (e.msg.sender != _DummyERC20_rewardToken) &&
            (onBehalfOf != _DummyERC20_rewardToken) &&
            (receiver != _DummyERC20_rewardToken)
        );
        require (e.msg.sender != _AToken) && (onBehalfOf != _AToken) && (receiver != _AToken);

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        claimRewardsOnBehalf(e, onBehalfOf, receiver, _rewards);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by claimRewardsOnBehalf";
    }


    rule aTokenBalanceIsFixed_for_claimSingleRewardOnBehalf(address onBehalfOf, address receiver) {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
        require _AToken != _DummyERC20_rewardToken;

        env e;

        // Limit sender
        require (
            (e.msg.sender != currentContract) &&
            (onBehalfOf != currentContract) &&
            (receiver != currentContract)
        );
        require (
            (e.msg.sender != _DummyERC20_rewardToken) &&
            (onBehalfOf != _DummyERC20_rewardToken) &&
            (receiver != _DummyERC20_rewardToken)
        );
        require (e.msg.sender != _AToken) && (onBehalfOf != _AToken) && (receiver != _AToken);

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        claimSingleRewardOnBehalf(e, onBehalfOf, receiver, _DummyERC20_aTokenUnderlying);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by claimSingleRewardOnBehalf";
    }


    rule aTokenBalanceIsFixed_for_claimRewardsToSelf() {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
        require _AToken != _DummyERC20_rewardToken;

        // Create a rewards array
        address[] _rewards;
        require _rewards[0] == _DummyERC20_rewardToken;
        require _rewards.length == 1;

        env e;

        // Limit sender
        require e.msg.sender != currentContract;
        require e.msg.sender != _AToken;
        require e.msg.sender != _DummyERC20_rewardToken;

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        claimRewardsToSelf(e, _rewards);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by claimRewardsToSelf";
    }


    rule aTokenBalanceIsFixed_for_claimRewards(address receiver) {
        require _AToken == asset();
        require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
        require _AToken != _DummyERC20_rewardToken;

        // Create a rewards array
        address[] _rewards;
        require _rewards[0] == _DummyERC20_rewardToken;
        require _rewards.length == 1;

        env e;

        // Limit sender
        require (e.msg.sender != currentContract) && (receiver != currentContract);
        require (
            (e.msg.sender != _DummyERC20_rewardToken) && (receiver != _DummyERC20_rewardToken)
        );
        require (e.msg.sender != _AToken) && (receiver != _AToken);

        uint256 preBalance = _AToken.balanceOf(e.msg.sender);

        claimRewards(e, receiver, _rewards);

        uint256 postBalance = _AToken.balanceOf(e.msg.sender);
        assert preBalance == postBalance, "aToken balance changed by claimRewards";
    }

    /// @title Sum of balances=totalSupply()
    //fail without Sload require balance <= sumAllBalance();
    //https://vaas-stg.certora.com/output/99352/1ada6d42ed4c4c03bb85b34d1da92be2/?anonymousKey=d27e10c2ac7220d8571d6374b4618b9e24f1a8a0
    // invariant sumAllBalance_eq_totalSupply()
    // 	sumAllBalance() == totalSupply()

    //fail without Sload require balance <= sumAllBalance();
    //https://vaas-stg.certora.com/output/99352/57f284feabc84b6ca392b781de221e9f/?anonymousKey=3554c35d0a060196775a71fdff3a14a6d2177861
    //todo: add presreved blocks and enable the invariant
    // invariant inv_balanceOf_leq_totalSupply(address user)
    // 	balanceOf(user) <= totalSupply()
    // 	{
    // 		preserved {
    // 			requireInvariant sumAllBalance_eq_totalSupply();
    // 		}
    // 	}

    /// @title AToken balancerOf(user) <= AToken totalSupply()
    //timeout on redeem metaWithdraw
    //error when running with rule_sanity
    //https://vaas-stg.certora.com/output/99352/509a56a1d46348eea0872b3a57c4d15a/?anonymousKey=3e15ac5a5b01e689eb3f71580e3532d8098e71b5
    invariant inv_atoken_balanceOf_leq_totalSupply(address user)
        _AToken.balanceOf(user) <= _AToken.totalSupply()
        filtered { f -> !f.isView && f.selector != redeem(uint256,address,address,bool).selector}
        {
            preserved with (env e){
                requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
            }
        }

    /// @title AToken balancerOf(user) <= AToken totalSupply()
    /// @dev case split of inv_atoken_balanceOf_leq_totalSupply
    //pass, times out with rule_sanity basic
    invariant inv_atoken_balanceOf_leq_totalSupply_redeem(address user)
        _AToken.balanceOf(user) <= _AToken.totalSupply()
        filtered { f -> f.selector == redeem(uint256,address,address,bool).selector}
        {
            preserved with (env e){
                requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
            }
        }

    //timeout when running with rule_sanity
    //https://vaas-stg.certora.com/output/99352/7840410509f94183bbef864770193ed9/?anonymousKey=b1a13994a4e51f586db837cc284b39c670532f50
    /// @title AToken sum of 2 balancers <= AToken totalSupply()
    // invariant inv_atoken_balanceOf_2users_leq_totalSupply(address user1, address user2)
    // 	(_AToken.balanceOf(user1) + _AToken.balanceOf(user2))<= _AToken.totalSupply()
    //     {
    // 		preserved with (env e1){
    //             setup(e1, user1);
    // 		    setup(e1, user2);
    // 		}
    //         preserved redeem(uint256 shares, address receiver, address owner) with (env e2){
    //             require user1 != user2;
    //             require _AToken.balanceOf(currentContract) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
    //         }
    //         preserved redeem(uint256 shares, address receiver, address owner, bool toUnderlying) with (env e3){
    //             require user1 != user2;
    //         	requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
    //             require _AToken.balanceOf(e3.msg.sender) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
    //             require _AToken.balanceOf(currentContract) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
    //         }
    //         preserved withdraw(uint256 assets, address receiver,address owner) with (env e4){
    //             require user1 != user2;
    //         	requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
    //             require _AToken.balanceOf(e4.msg.sender) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
    //             require _AToken.balanceOf(currentContract) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
    //         }

    //         preserved metaWithdraw(address owner, address recipient,uint256 staticAmount,uint256 dynamicAmount,bool toUnderlying,uint256 deadline,_StaticATokenLM.SignatureParams sigParams)
    //         with (env e5){
    //             require user1 != user2;
    //         	requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
    //             require _AToken.balanceOf(e5.msg.sender) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
    //             require _AToken.balanceOf(currentContract) + _AToken.balanceOf(user1) + _AToken.balanceOf(user2) <= _AToken.totalSupply();
    //         }

    // 	}

    /// @title Sum of AToken scaled balances = AToken scaled totalSupply()
    //pass with rule_sanity basic except metaDeposit()
    //https://vaas-stg.certora.com/output/99352/4f91637a96d647baab9accb1093f1690/?anonymousKey=53ccda4a9dd8988205d4b614d9989d1e4148533f
    invariant sumAllATokenScaledBalance_eq_totalSupply()
        sumAllATokenScaledBalance() == _AToken.scaledTotalSupply()


    /// @title AToken scaledBalancerOf(user) <= AToken scaledTotalSupply()
    //pass with rule_sanity basic except metaDeposit()
    //https://vaas-stg.certora.com/output/99352/6798b502f97a4cd2b05fce30947911c0/?anonymousKey=c5808a8997a75480edbc45153165c8763488cd1e
    invariant inv_atoken_scaled_balanceOf_leq_totalSupply(address user)
        _AToken.scaledBalanceOf(user) <= _AToken.scaledTotalSupply()
        {
            preserved {
                requireInvariant sumAllATokenScaledBalance_eq_totalSupply();
            }
        }

    // //from unregistered_atoken.spec
    // // fail
    // //todo: remove 
    // rule claimable_leq_total_claimable() {
    //     require _RewardsController.getAvailableRewardsCount(_AToken) == 1;
        
    // 	require _RewardsController.getRewardsByAsset(_AToken, 0) == _DummyERC20_rewardToken;

    //     env e;
    //     address user;
    
    //     require currentContract != user;
    //     require _AToken != user;
    //     require _RewardsController != user;
    //     require _DummyERC20_aTokenUnderlying  != user;
    //     require _DummyERC20_rewardToken != user;
    //     require _SymbolicLendingPoolL1 != user;
    //     require _TransferStrategy != user;
    //     require _ScaledBalanceToken != user;
    //     require _TransferStrategy != user;

    //     requireInvariant inv_atoken_balanceOf_leq_totalSupply(currentContract);
    //     requireInvariant inv_atoken_scaled_balanceOf_leq_totalSupply(currentContract);
        

    //     require getRewardsIndexOnLastInteraction(user, _DummyERC20_rewardToken) == 0;
    //     require getUnclaimedRewards(e, user, _DummyERC20_rewardToken) == 0;
        
    //     uint256 total = getTotalClaimableRewards(e, _DummyERC20_rewardToken);
    //     uint256 claimable = getClaimableRewards(e, user, _DummyERC20_rewardToken);
    //     assert claimable <= total, "Too much claimable";
    // }





    //The invariant fails, as suspected, with loop_iter=2.
    //The invariant is remove.
    //requireInvaraint are replaced with require in rules getClaimableRewards_stable*
    // invariant registered_reward_exists_in_controller(address reward)
    //     (isRegisteredRewardToken(reward) =>  
    //     (_RewardsController.getAvailableRewardsCount(_AToken)  > 0
    //     && _RewardsController.getRewardsByAsset(_AToken, 0) == reward)) 
    //     filtered { f -> f.selector != initialize(address,string,string).selector }//Todo: remove filter and use preserved block when CERT-1706 is fixed
    //     {
    //         //preserved initialize(address newAToken,string staticATokenName, string staticATokenSymbol) {
    //         //     require newAToken == _AToken;
    //         // }
    //     }
