import "erc4626_base.spec"

// The following spec implements erc4626 properties according to the official eip described here:
// https://eips.ethereum.org/EIPS/eip-4626

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

// MINT

// passes
rule PreviewMintShouldMimicMint(
    env e,
    uint256 shares,
    address receiver
) {
    setup(e, receiver);

    requireInvariant TotalSupplyIsSumOfBalances();
    storage initalState = lastStorage;

    uint256 previewedAmount = previewMint(e, shares);
    uint256 mintedAmount = mint(e, shares, receiver) at initalState;

    assert previewedAmount == mintedAmount;
}

rule MintShouldNotAffectOthers(
    env e,
    uint256 shares,
    address receiver,
    address other
)
{
    setup(e, receiver);
    setup(e, other);
    requireInvariant TotalSupplyIsSumOfBalances();
    require other != e.msg.sender && other != receiver;

    // before
    uint256 _balanceOfOther = balanceOf(other);
    uint256 _ATokenBalanceOfOther = _AToken.balanceOf(e, other);

    // function call
    mint(e, shares, receiver);

    // after
    uint256 balanceOfOther_ = balanceOf(other);
    uint256 ATokenBalanceOfOther_ = _AToken.balanceOf(e, other);

    // asserts
    assert _ATokenBalanceOfOther == ATokenBalanceOfOther_, "AToken.balanceOf(other) affected";
    assert _balanceOfOther == balanceOfOther_, "balanceOf(other) affected";
}

rule MintShouldRevertIfSharesZeroOrGTMaxMint(
    env e,
    uint256 shares,
    address receiver
) {
    setup(e, receiver);
    require getRewardTokensLength() == 0;
    require shares > maxMint(receiver) || shares == 0;

    mint@withrevert(e, shares, receiver);

    assert lastReverted;
}

rule MintShouldDepositCorrectAmount(
    env e,
    uint256 shares,
    address receiver
) {
    setup(e, receiver);
    requireInvariant TotalSupplyIsSumOfBalances();

    require getRewardTokensLength() == 0;

    require _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2
         || _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1;
    // before
    uint256 _ATokenBalanceOfThis = _AToken.balanceOf(e, currentContract);
    uint256 _totalAssets = totalAssets(e);

    // function call
    uint256 assetsMinted = mint(e, shares, receiver);

    // after
    uint256 ATokenBalanceOfThis_ = _AToken.balanceOf(e, currentContract);
    uint256 totalAssets_ = totalAssets(e);
    // asserts
    assert _ATokenBalanceOfThis + assetsMinted == ATokenBalanceOfThis_,
        "incorrect AToken amount deposited";
    assert _totalAssets + assetsMinted == totalAssets_,
        "totalAssets() not increased by correct amount";
}

rule MintShouldSpendCorrectAmount(
    env e,
    uint256 shares,
    address receiver
) {
    setup(e, receiver);
    requireInvariant TotalSupplyIsSumOfBalances();
    //single_RewardToken_setup();
    require getRewardTokensLength() == 0;

    require _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2
         || _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1;

    // before
    uint256 _ATokenBalanceOfSender = _AToken.balanceOf(e, e.msg.sender);

    // function call
    uint256 assetsMinted = mint(e, shares, receiver);

    // after
    uint256 ATokenBalanceOfSender_ = _AToken.balanceOf(e, e.msg.sender);

    // asserts
    assert _ATokenBalanceOfSender - assetsMinted == ATokenBalanceOfSender_,
        "sender spent incorrect AToken amount";
}

rule MintShouldIncreaseReceiverBalance(
    env e,
    uint256 shares,
    address receiver
) {
    setup(e, receiver);
    requireInvariant TotalSupplyIsSumOfBalances();

    require getRewardTokensLength() == 0;

    require _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2
         || _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1;

    // before
    uint256 _balanceOfSender = balanceOf(e.msg.sender);
    uint256 _balanceOfReceiver = balanceOf(receiver);

    // function call
    uint256 assetsMinted = mint(e, shares, receiver);

    // after
    uint256 balanceOfSender_ = balanceOf(e.msg.sender);
    uint256 balanceOfReceiver_ = balanceOf(receiver);

    // asserts
    assert (e.msg.sender != receiver) => (_balanceOfSender == balanceOfSender_),
        "msg.sender's balance changed, when not the intended receiver";
    assert _balanceOfReceiver + shares == balanceOfReceiver_,
        "receiver's balance was not increased by correct amount";
}

rule MintShouldIncreaseTotalSupplyByCorrectAmount(
    env e,
    uint256 shares,
    address receiver
) {
    setup(e, receiver);
    requireInvariant TotalSupplyIsSumOfBalances();

    require getRewardTokensLength() == 0;

    require _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2
         || _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1;

    // before
    uint256 _totalSupply = totalSupply();

    // function call
    uint256 assetsMinted = mint(e, shares, receiver);

    // after
    uint256 totalSupply_ = totalSupply();

    // assert
    assert _totalSupply + shares <= totalSupply_,
       "totalSupply was not increased by the correct amount";
}


rule DepositWithdrawCorrectness(
    env e,
    uint256 assets,
    address receiverOfDeposit,
    address receiverOfWithdrawl
) {
    setup(e, receiverOfDeposit);
    setup(e, receiverOfWithdrawl);
    requireInvariant TotalSupplyIsSumOfBalances();

    require getRewardTokensLength() == 0;

    require _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2
         || _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1;

    address owner = receiverOfDeposit;

    // before
    uint256 _totalAssets = totalAssets(e);

    // function calls
    uint256 sharesDeposited = deposit(e, assets, receiverOfDeposit);
    uint256 sharesWithdrawn = withdraw(e, assets, receiverOfWithdrawl, owner);

    // after
    uint256 totalAssets_ = totalAssets(e);


    // asserts
    assert _totalAssets < totalAssets_, "assets were lost";
}

rule DepositRedeemCorrectness(
    env e,
    uint256 assets,
    address receiverOfDeposit,
    address receiverOfRedeemed
) {
    setup(e, receiverOfDeposit);
    setup(e, receiverOfRedeemed);
    requireInvariant TotalSupplyIsSumOfBalances();

    require getRewardTokensLength() == 0;

    require _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2
         || _SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1;

    address owner = receiverOfDeposit;

    // before
    uint256 _totalAssets = totalAssets(e);

    // function calls
    uint256 sharesDeposited = deposit(e, assets, receiverOfDeposit);
    uint256 assetsWithdrawn = redeem(e, sharesDeposited, receiverOfRedeemed, owner);

    // after
    uint256 totalAssets_ = totalAssets(e);

    // asserts
    assert assets <= assetsWithdrawn;
    assert _totalAssets < totalAssets_, "assets were lost";
}

rule NoVariationInConvertToShares(
    env e0,
    env e1,
    uint256 amount
) {
    require e0.block.timestamp == e1.block.timestamp;
    assert convertToShares(e0, amount) == convertToShares(e1, amount), "Variation in convertToShares";
}

rule NoVariationInConvertToAssets(
    env e0,
    env e1,
    uint256 shares
) {
    require e0.block.timestamp == e1.block.timestamp;
    assert convertToAssets(e0, shares) == convertToAssets(e1, shares), "Variation in convertToShares";
}

rule RedeemMaxAmount(
    env e,
    uint256 shares,
    address recipient,
    address owner,
    bool toUnderlying
) {
    setup(e, recipient);
    single_RewardToken_setup();
    requireInvariant TotalSupplyIsSumOfBalances();

    bool paused = _SymbolicLendingPool.reserveIsActive();
    require paused == false;

    storage init_state = lastStorage;

    uint256 max_shares = maxRedeem(owner);

    uint256 amt_assets = redeem(e, shares, recipient, owner) at init_state;

    assert shares <= max_shares;
}

invariant ATokenVsStaticAtoken(env e)
    totalSupply() <= _AToken.totalSupply(e)
    filtered { f -> !harnessOnlyMethods(f) }
    {
        preserved {
            requireInvariant TotalSupplyIsSumOfBalances();
            require e.msg.sender != _AToken;
            require e.msg.sender != _RewardsController;
            require _DummyERC20_aTokenUnderlying != e.msg.sender;
            require _DummyERC20_rewardToken != e.msg.sender;
            require _SymbolicLendingPool != e.msg.sender;
        }
    }