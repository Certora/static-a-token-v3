import "../methods/methods_base.spec"

/////////////////// Methods ////////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// Properties ///////////////////////

invariant allCumulativeBalanceEqualToTotalSupply() 
    totalSupply() == allCumulativeBalance
    filtered { f -> harnessOnlyMethods(f) }
    {
        preserved with (env e) {
            setup(e, e.msg.sender);
            single_RewardToken_setup();
        }
    } 


invariant StaticTokenAndATokens(env e)
    totalSupply() <= _AToken.totalSupply(e)
    filtered { f -> !harnessOnlyMethods(f) }
    {
        preserved {
            requireInvariant allCumulativeBalanceEqualToTotalSupply();
            require e.msg.sender != _AToken;
            require e.msg.sender != _RewardsController;
            require _DummyERC20_aTokenUnderlying != e.msg.sender;
            require _DummyERC20_rewardToken != e.msg.sender;
            require _SymbolicLendingPool != e.msg.sender;
        }
    }


ghost uint256 allCumulativeBalance {
    init_state axiom allCumulativeBalance == 0;
}

hook Sstore balanceOf[KEY address a] uint valueAfter (uint valueBefore) STORAGE {
    allCumulativeBalance = allCumulativeBalance + valueAfter - valueBefore;
}


rule checkCorrectnessOfRedeem(
    env e,
    address receiver,
    address addr,
    uint256 sharesAmount,
    bool toUnderlying
) {
    setup(e, receiver);
    setup(e, addr);
    single_RewardToken_setup();
    requireInvariant allCumulativeBalanceEqualToTotalSupply();
    
    
    storage init_state = lastStorage;

    uint256 sharesAmountBefore;
    uint256 assetsAmountBefore;
    sharesAmountBefore, assetsAmountBefore = redeem(e, sharesAmount, receiver, addr, toUnderlying) at init_state;

    uint256 sharesAmountAfter;
    uint256 assetsAmountAfter;
    sharesAmountAfter, assetsAmountAfter = redeem(e, sharesAmount, receiver, addr, toUnderlying) at init_state;

    assert (sharesAmountBefore == assetsAmountBefore) && (assetsAmountBefore == assetsAmountAfter);
}

rule checkCorrectnessOfMaxRedeem(
    env e,
    address addr
) {
    setup(e, addr);
    single_RewardToken_setup();
    requireInvariant allCumulativeBalanceEqualToTotalSupply();
    storage init_state = lastStorage;

    uint256 maxSharesAmountBefore = maxRedeemUnderlying(e, addr) at init_state;
    uint256 maxSharesAmountAfter = maxRedeemUnderlying(e, addr) at init_state;

    assert (maxSharesAmountBefore == maxSharesAmountAfter);
}

rule CannotRedeemMoreUnderlyingThanMaxRedeemUnderlying(
    env e,
    address receiver,
    address addr,
    uint256 sharesAmount,
    bool toUnderlying
) {
    require addr == e.msg.sender;
    require addr == receiver;
    setup(e, receiver);
    single_RewardToken_setup();

    address aTokenAddress = _SymbolicLendingPool.getATokenAddress();
    
    require _AToken == aTokenAddress;
    requireInvariant allCumulativeBalanceEqualToTotalSupply();

    require  _SymbolicLendingPool.assetIsPaused() == false && _SymbolicLendingPool.reserveIsActive() == true;
    require toUnderlying == true;
    uint256 sharesAmountNew;
    uint256 assetsAmount;
    storage init_state = lastStorage;

    uint256 aTokenContractUnderlyingBalance = _DummyERC20_aTokenUnderlying.balanceOf(_AToken);
    uint256 senderBalanceBefore = balanceOf(e.msg.sender);
    uint256 senderUnderlyingBalance = convertToAssets(e, senderBalanceBefore);
    uint256 senderSharesBasedOnUnderlyingBalance = convertToAssets(e, sharesAmount);

    if( senderUnderlyingBalance <= aTokenContractUnderlyingBalance ||
        senderSharesBasedOnUnderlyingBalance <= aTokenContractUnderlyingBalance
    ) {
        sharesAmountNew, assetsAmount = redeem(e, sharesAmount, receiver, addr, toUnderlying) at init_state;
        uint256 senderBalanceAfter = balanceOf(e.msg.sender);

        assert (
                senderBalanceBefore - sharesAmount == senderBalanceAfter &&
                assetsAmount <= senderUnderlyingBalance
        );
    } else {

        uint256 maximumSharesAmount = maxRedeemUnderlying(e, addr);
        uint256 maximumAssetsAmount = convertToAssets(e, maximumSharesAmount) at init_state;
        sharesAmountNew, assetsAmount = redeem(e, sharesAmount, receiver, addr, toUnderlying) at init_state;

        assert (sharesAmountNew <= maximumSharesAmount) || (assetsAmount <= maximumAssetsAmount) || (sharesAmount <= 1 && assetsAmount <=1);
    }
}


rule checkDecrementOfUnclaimedRewards(
    env e,
    method f,
    calldataarg args
) {
    setup(e, e.msg.sender);
    rewardsController_reward_setup();
    single_RewardToken_setup();

    uint256 unclaimedRewardsBefore = getUnclaimedRewards(e.msg.sender, getRewardToken(0));

    require !harnessOnlyMethods(f);
    require !claimFunctions(f);
    f(e, args);

    uint256 unclaimedRewardsAfter = getUnclaimedRewards(e.msg.sender, getRewardToken(0));

    assert unclaimedRewardsBefore <= unclaimedRewardsAfter;
}

rule tranferFromShouldNotAffectUnclaimedRewards(
    env e,
    address from,
    address to,
    uint256 amount
) {
    setup(e, from);
    setup(e, to);
    rewardsController_reward_setup();
    single_RewardToken_setup();

    require from != 0 && to != 0;

    uint256 fromUnclaimedRewardsBefore = getClaimableRewards(e, from, getRewardToken(0));
    uint256 toUnclaimedRewardsBefore = getClaimableRewards(e, to, getRewardToken(0));

    transferFrom(e, from, to, amount);

    uint256 fromUnclaimedRewardsAfter = getUnclaimedRewards(from, getRewardToken(0));
    uint256 toUnclaimedRewardsAfter = getUnclaimedRewards(to, getRewardToken(0));

    assert (toUnclaimedRewardsBefore == toUnclaimedRewardsAfter) && (fromUnclaimedRewardsBefore == fromUnclaimedRewardsAfter);
}

rule tranferShouldNotAffectUnclaimedRewards(
    env e,
    address to,
    uint256 amount
) {
    require e.msg.sender != 0 && to != 0;

    setup(e, to);
    rewardsController_reward_setup();
    single_RewardToken_setup();

    uint256 fromUnclaimedRewardsBefore = getClaimableRewards(e, e.msg.sender, getRewardToken(0));
    uint256 toUnclaimedRewardsBefore = getClaimableRewards(e, to, getRewardToken(0));

    transfer(e, to, amount);

    uint256 fromUnclaimedRewardsAfter = getUnclaimedRewards(e.msg.sender, getRewardToken(0));
    uint256 toUnclaimedRewardsAfter = getUnclaimedRewards(to, getRewardToken(0));

    assert (toUnclaimedRewardsBefore == toUnclaimedRewardsAfter) && (fromUnclaimedRewardsBefore == fromUnclaimedRewardsAfter);
}

rule depositShouldNotAffectUnclaimedRewards(
    env e,
    address receiver,
    uint256 assetAmount,
    uint16 referralCode,
    bool fromUnderlying
) {
    require e.msg.sender != 0 && receiver != 0;

    setup(e, receiver);
    rewardsController_reward_setup();
    single_RewardToken_setup();

    uint256 fromUnclaimedRewardsBefore = getClaimableRewards(e, e.msg.sender, getRewardToken(0));
    uint256 toUnclaimedRewardsBefore = getClaimableRewards(e, receiver, getRewardToken(0));

    deposit(e, assetAmount, receiver, referralCode, fromUnderlying);

    uint256 fromUnclaimedRewardsAfter = getUnclaimedRewards(e.msg.sender, getRewardToken(0));
    uint256 toUnclaimedRewardsAfter = getUnclaimedRewards(receiver, getRewardToken(0));

    assert (toUnclaimedRewardsBefore == toUnclaimedRewardsAfter) && (fromUnclaimedRewardsBefore == fromUnclaimedRewardsAfter);
}


rule withdrawShouldNotAffectUnclaimedRewards(
    env e,
    address receiver,
    address addr,
    uint256 assetAmount
) {
    require e.msg.sender != 0 && receiver != 0;

    setup(e, receiver);
    setup(e, addr);
    rewardsController_reward_setup();
    single_RewardToken_setup();

    uint256 fromUnclaimedRewardsBefore = getClaimableRewards(e, e.msg.sender, getRewardToken(0));
    uint256 toUnclaimedRewardsBefore = getClaimableRewards(e, receiver, getRewardToken(0));

    withdraw(e, assetAmount, receiver, addr);

    uint256 fromUnclaimedRewardsAfter = getUnclaimedRewards(e.msg.sender, getRewardToken(0));
    uint256 toUnclaimedRewardsAfter = getUnclaimedRewards(receiver, getRewardToken(0));

    assert (toUnclaimedRewardsBefore == toUnclaimedRewardsAfter) && (fromUnclaimedRewardsBefore == fromUnclaimedRewardsAfter);
}