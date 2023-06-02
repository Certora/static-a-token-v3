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
    address owner,
    bool toUnderlying
) {
    //FIXME remove this
    require owner == e.msg.sender;
    require owner == recipient;
    setup(e, recipient);
    single_RewardToken_setup();
    requireInvariant TotalSupplyIsSumOfBalances();

    address pool_atoken = _SymbolicLendingPool.getATokenAddress();
    require _AToken == pool_atoken;

    // pre-assume active and !paused
    require _SymbolicLendingPool.reserveIsActive() == true;
    require _SymbolicLendingPool.assetIsPaused() == false;

    //requireInvariant SolvencyOfATokenContract();
    require _AToken.totalSupply(e) == _DummyERC20_aTokenUnderlying.balanceOf(_AToken);


    require toUnderlying == true;

    storage init_state = lastStorage;


    // function calls
    uint256 max_shares = maxRedeemUnderlying(e, owner);
    uint256 max_assets = convertToAssets(e, max_shares) at init_state;

    uint256 amt_shares;
    uint256 amt_assets;
    amt_shares, amt_assets = redeem(e, shares, recipient, owner, toUnderlying) at init_state;

    // asserts
    //assert amt_shares <= max_shares || ((amt_shares > max_shares) => (amt_assets == max_assets));
    assert (amt_shares <= max_shares) || (amt_assets <= max_assets) || (amt_assets <= 1 && amt_shares <=1);
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
// mint
 // redeem
 // redeemToUnderlying
 // tranfer  // have transferFrom

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


    // before
    uint256 _UnclaimedRewardsFrom = getClaimableRewards(e, e.msg.sender, getRewardToken(0));
    uint256 _UnclaimedRewardsTo = getClaimableRewards(e, receiver, getRewardToken(0));

    withdraw(e, assets, receiver, owner);

    // after
    uint256 UnclaimedRewardsFrom_ = getUnclaimedRewards(e.msg.sender, getRewardToken(0));
    uint256 UnclaimedRewardsTo_ = getUnclaimedRewards(receiver, getRewardToken(0));

    assert (_UnclaimedRewardsFrom == UnclaimedRewardsFrom_) && (_UnclaimedRewardsTo == UnclaimedRewardsTo_);
}

rule UnclaimedRewardsShouldNotChangeOnTransferFrom(
    env e,
    address from,
    address to,
    uint256 amount
) {
    setup(e, e.msg.sender);
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



rule UnclaimedRewardsGrowsWithTime(
    env e0,
    env e1
) {
    assert false;
}