import "../methods/methods_base.spec"

/////////////////// Methods ////////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// Properties ///////////////////////

ghost uint256 SumOfBalances {
    init_state axiom SumOfBalances == 0;
}

hook Sstore balanceOf[KEY address a] uint new_value (uint old_value) STORAGE {
    SumOfBalances = SumOfBalances + new_value - old_value;
}

invariant TotalSupplyIsSumOfBalances()
    totalSupply() == SumOfBalances
    filtered { f -> !harnessOnlyMethods(f) }
    {
        preserved with (env e) {
                setup(e, e.msg.sender);
                single_RewardToken_setup();
        }
    }

//TODO rule additveWithdrawl() // 2*withdraw(x) == withdraw(2*x)

//rule redeem(underlying==true) <= maxRedeemUnderlying()
rule CannotRedeemMoreUnderlyingThanMaxRedeemUnderlying(
    env e,
    uint256 shares,
    address recipient,
    address owner
) {
    bool toUnderlying = true;

    setup(e, recipient);
    single_RewardToken_setup();
    requireInvariant TotalSupplyIsSumOfBalances();

    address pool_atoken = _SymbolicLendingPool.getATokenAddress();
    require _AToken == pool_atoken;

    // pre-assume active and !paused
    require _SymbolicLendingPool.reserveIsActive() == true;
    require _SymbolicLendingPool.assetIsPaused() == false;

    uint256 underlyingBalanceOfATokenContract = _DummyERC20_aTokenUnderlying.balanceOf(_AToken);

    uint256 amt_shares;
    uint256 amt_assets;
    storage init_state = lastStorage;

    uint256 _balanceOfMsgSender = balanceOf(e.msg.sender);
    uint256 _balanceOfMsgSenderInAssets = convertToAssets(e, _balanceOfMsgSender);
    uint256 msgSenderUnderlyingAssetsOfShares = convertToAssets(e, shares);

    // FIXME: This might be overfitting
    require _balanceOfMsgSenderInAssets > underlyingBalanceOfATokenContract;
    require msgSenderUnderlyingAssetsOfShares > underlyingBalanceOfATokenContract;

    // function calls
    uint256 max_shares = maxRedeemUnderlying(e, owner);
    uint256 max_assets = convertToAssets(e, max_shares) at init_state;


    amt_shares, amt_assets = redeem(e, shares, recipient, owner, toUnderlying) at init_state;
    // asserts
    assert (amt_shares <= max_shares) || (amt_assets <= max_assets) || (amt_assets <= 1 && amt_shares <=1);
}

rule MaxRedeemShouldBeConsistant(
    env e,
    address owner
) {
    setup(e, owner);
    single_RewardToken_setup();
    requireInvariant TotalSupplyIsSumOfBalances();
    storage init_state = lastStorage;

    uint256 max_shares0 = maxRedeemUnderlying(e, owner) at init_state;
    uint256 max_shares1 = maxRedeemUnderlying(e, owner) at init_state;

    assert (max_shares0 == max_shares1);
}

rule RedeemShouldBeConsistant(
    env e,
    uint256 shares,
    address recipient,
    address owner,
    bool toUnderlying
) {
    setup(e, recipient);
    setup(e, owner);
    single_RewardToken_setup();
    requireInvariant TotalSupplyIsSumOfBalances();
    storage init_state = lastStorage;

    uint256 amt_shares0;
    uint256 amt_assets0;
    amt_shares0, amt_assets0 = redeem(e, shares, recipient, owner, toUnderlying) at init_state;

    uint256 amt_shares1;
    uint256 amt_assets1;
    amt_shares1, amt_assets1 = redeem(e, shares, recipient, owner, toUnderlying) at init_state;

    assert (amt_assets0 == amt_assets1) && (amt_shares0 == amt_shares1);
}


rule ClaimRewardsOnBehalfDoesNotAffectAStaticTokenBalances(
    env e,
    address onBehalfOf,
    address receiver,
    address other
) {
    require receiver != other;
    setup(e, receiver);
    setup(e, other);
    single_RewardToken_setup();

    // before
    uint256 _balanceOfReceiver = balanceOf(receiver);
    uint256 _balanceOfOther = balanceOf(other);

    // function call
    claimSingleRewardOnBehalf(e, onBehalfOf, receiver, _DummyERC20_rewardToken);

    // after
    uint256 balanceOfReceiver_ = balanceOf(receiver);
    uint256 balanceOfOther_ = balanceOf(other);

    // asserts
    assert _balanceOfReceiver == balanceOfReceiver_;
    assert _balanceOfOther == balanceOfOther_;
}

rule CollectAndUpdateRewardsDoesNotAffectAStaticTokenBalances(
    env e,
    address reward,
    address other
) {
    require e.msg.sender != other;
    setup(e, other);
    single_RewardToken_setup();

    // before
    uint256 _balanceOfSender = balanceOf(e.msg.sender);
    uint256 _balanceOfOther = balanceOf(other);

    // function call
    collectAndUpdateRewards(e, reward);

    // after
    uint256 balanceOfSender_ = balanceOf(e.msg.sender);
    uint256 balanceOfOther_ = balanceOf(other);

    // asserts
    assert _balanceOfSender == balanceOfSender_;
    assert _balanceOfOther == balanceOfOther_;
}

rule UnclaimedRewardsShouldNotDecrease(
    env e,
    method f,
    calldataarg args
) {
    setup(e, e.msg.sender);
    rewardsController_reward_setup();
    single_RewardToken_setup();

    uint256 _UnclaimedRewards = getUnclaimedRewards(e.msg.sender, getRewardToken(0));

    require !harnessOnlyMethods(f);
    require !claimFunctions(f);

    // function call
    f(e, args);

    uint256 UnclaimedRewards_ = getUnclaimedRewards(e.msg.sender, getRewardToken(0));

    assert _UnclaimedRewards <= UnclaimedRewards_, "unclaimedRewards decreased";
}

rule UnclaimedRewardsShouldNotChangeOnDeposit(
    env e,
    uint256 assets,
    address recipient,
    bool fromUnderlying
) {
    uint16 referralCode; // irrelvant

    require e.msg.sender != 0;
    require recipient != 0;

    setup(e, recipient);
    rewardsController_reward_setup();
    single_RewardToken_setup();

    require _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2
         || _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1;

    // before
    uint256 _UnclaimedRewardsFrom = getClaimableRewards(e, e.msg.sender, getRewardToken(0));
    uint256 _UnclaimedRewardsTo = getClaimableRewards(e, recipient, getRewardToken(0));

    // function call
    deposit(e, assets, recipient, referralCode, fromUnderlying);

    // after
    uint256 UnclaimedRewardsFrom_ = getUnclaimedRewards(e.msg.sender, getRewardToken(0));
    uint256 UnclaimedRewardsTo_ = getUnclaimedRewards(recipient, getRewardToken(0));

    assert (_UnclaimedRewardsFrom == UnclaimedRewardsFrom_) && (_UnclaimedRewardsTo == UnclaimedRewardsTo_);
}

rule UnclaimedRewardsShouldNotChangeOnWithdraw(
    env e,
    uint256 assets,
    address receiver,
    address owner
) {
    require e.msg.sender != 0;
    require receiver != 0;

    setup(e, receiver);
    setup(e, owner);
    rewardsController_reward_setup();
    single_RewardToken_setup();

    require _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2
         || _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1;

    // before
    uint256 _UnclaimedRewardsFrom = getClaimableRewards(e, e.msg.sender, getRewardToken(0));
    uint256 _UnclaimedRewardsTo = getClaimableRewards(e, receiver, getRewardToken(0));

    withdraw(e, assets, receiver, owner);

    // after
    uint256 UnclaimedRewardsFrom_ = getUnclaimedRewards(e.msg.sender, getRewardToken(0));
    uint256 UnclaimedRewardsTo_ = getUnclaimedRewards(receiver, getRewardToken(0));

    assert (_UnclaimedRewardsFrom == UnclaimedRewardsFrom_) && (_UnclaimedRewardsTo == UnclaimedRewardsTo_);
}

rule UnclaimedRewardsShouldNotChangeOnTransfer(
    env e,
    address to,
    uint256 amount
) {
    require e.msg.sender != 0;
    require to != 0;

    setup(e, to);
    rewardsController_reward_setup();
    single_RewardToken_setup();

    uint256 _UnclaimedRewardsFrom = getClaimableRewards(e, e.msg.sender, getRewardToken(0));
    uint256 _UnclaimedRewardsTo = getClaimableRewards(e, to, getRewardToken(0));

    transfer(e, to, amount);

    uint256 UnclaimedRewardsFrom_ = getUnclaimedRewards(e.msg.sender, getRewardToken(0));
    uint256 UnclaimedRewardsTo_ = getUnclaimedRewards(to, getRewardToken(0));

    assert (_UnclaimedRewardsFrom == UnclaimedRewardsFrom_) && (_UnclaimedRewardsTo == UnclaimedRewardsTo_);
    assert false;
}

rule UnclaimedRewardsShouldNotChangeOnTransferFrom(
    env e,
    address from,
    address to,
    uint256 amount
) {
    setup(e, from);
    setup(e, to);
    rewardsController_reward_setup();
    single_RewardToken_setup();

    require from != 0;
    require to != 0;

    uint256 _UnclaimedRewardsFrom = getClaimableRewards(e, from, getRewardToken(0));
    uint256 _UnclaimedRewardsTo = getClaimableRewards(e, to, getRewardToken(0));

    transferFrom(e, from, to, amount);

    uint256 UnclaimedRewardsFrom_ = getUnclaimedRewards(from, getRewardToken(0));
    uint256 UnclaimedRewardsTo_ = getUnclaimedRewards(to, getRewardToken(0));

    assert (_UnclaimedRewardsFrom == UnclaimedRewardsFrom_) && (_UnclaimedRewardsTo == UnclaimedRewardsTo_);
}