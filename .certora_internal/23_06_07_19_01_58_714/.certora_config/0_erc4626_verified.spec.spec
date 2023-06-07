import "erc4626_base.spec"

// The following spec implements erc4626 properties according to the official eip described here:
// https://eips.ethereum.org/EIPS/eip-4626

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
            require DummyERC20_aTokenUnderlying != e.msg.sender;
            require DummyERC20_rewardToken != e.msg.sender;
            require SymbolicLendingPool != e.msg.sender;
        }
    }


ghost uint256 allCumulativeBalance {
    init_state axiom allCumulativeBalance == 0;
}

hook Sstore balanceOf[KEY address a] uint valueAfter (uint valueBefore) STORAGE {
    allCumulativeBalance = allCumulativeBalance + valueAfter - valueBefore;
}

rule checkMaxSharesRedeem(
    env e,
    address owner,
    address recipient,
    uint256 shares,
    bool toUnderlying
) {
    require owner == e.msg.sender;
    require owner == recipient;
    setup(e, recipient);
    single_RewardToken_setup();
    requireInvariant allCumulativeBalanceEqualToTotalSupply();

    require SymbolicLendingPool.reserveIsActive() == false;

    // storage init_state = lastStorage;

    uint256 maximumShares = maxRedeem(owner);

    //uint256 amt_assets = redeem(e, shares, recipient, owner) at init_state;

    uint256 assetsAmount = redeem(e, shares, recipient, owner) at init_state;

    assert maximumShares <= assetsAmount;
}

rule checkWithdrawalCorrectnessWithDeposit(
    env e,
    address depositReceiver,
    address withdrawReceiver,
    uint256 assetAmount

) {
    setup(e, depositReceiver);
    setup(e, withdrawReceiver);

    requireInvariant allCumulativeBalanceEqualToTotalSupply();

    require SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1 ||
            SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2;

    uint256 totalAssetsBefore = totalAssets(e);
    uint256 sharesDeposited = deposit(e, assetAmount, depositReceiver);
    uint256 sharesWithdrawn = withdraw(e, assetAmount, withdrawReceiver, depositReceiver);
    uint256 totalAssetsAfter = totalAssets(e);

    assert totalAssetsBefore < totalAssetsAfter, "Lost Assets";
}

rule checkRedeemCorrectnessWhenDeposit(
    env e,
    address depositReceiver,
    address redeemReceiver,
    uint256 assetAmount
) {
    setup(e, depositReceiver);
    setup(e, redeemReceiver);

    requireInvariant allCumulativeBalanceEqualToTotalSupply();

    require SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1 ||
            SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2;
    
    uint256 totalAssetsBefore = totalAssets(e);
    uint256 sharesDeposited = deposit(e, assetAmount, depositReceiver);
    uint256 assetsWithdrawn = redeem(e, sharesDeposited, redeemReceiver, depositReceiver);
    uint256 totalAssetsAfter = totalAssets(e);


    // asserts
    assert assetAmount <= assetsWithdrawn;
    assert totalAssetsAfter < totalAssetsAfter, "Lost Assets";
}

rule checkWithdrawCorrectnessWhenDeposit(
    env e,
    address depositReceiver,
    address withdrawReceiver,
    uint256 assetAmount
) {
    setup(e, depositReceiver);
    setup(e, withdrawReceiver);

    requireInvariant allCumulativeBalanceEqualToTotalSupply();

    require SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1 ||
            SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2;
    
    uint256 totalAssetsBefore = totalAssets(e);
    uint256 sharesDeposited = deposit(e, assetAmount, depositReceiver);
    uint256 sharesWithdrawn = withdraw(e, assetAmount, withdrawReceiver, depositReceiver);

    // after
    uint256 totalAssets_ = totalAssets(e);


    // asserts
    assert _totalAssets < totalAssets_, "assets were lost";
}

rule ValidAmountShouldBeDepositedOnMint(
    env e,
    address receiver,
    uint256 sharesAmount
) {
    setup(e, receiver);
    require sharesAmount != 0 && sharesAmount <= maxMint(receiver);
    

    requireInvariant allCumulativeBalanceEqualToTotalSupply();

    require SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1 ||
            SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2;
    

    uint256 aTokenBalanceBefore = AToken.balanceOf(e, currentContract);
    uint256 aTokenBalanceOfMinterBefore = AToken.balanceOf(e, e.msg.sender);
    uint256 totalAssetsBefore = totalAssets(e);
    uint256 totalSupplyBefore = totalSupply();
    uint256 senderBalanceBefore = balanceOf(e.msg.sender);
    uint256 receiverBalanceBefore = balanceOf(receiver);
    


    uint256 assetsAmount = mint(e, sharesAmount, receiver);

    uint256 aTokenBalanceAfter = AToken.balanceOf(e, currentContract);
    uint256 aTokenBalanceOfMinterAfter = AToken.balanceOf(e, e.msg.sender);
    uint256 totalAssetsAfter = totalAssets(e);
    uint256 totalSupplyAfter = totalSupply();
    uint256 senderBalanceAfter = balanceOf(e.msg.sender);
    uint256 receiverBalanceAfter = balanceOf(receiver);



    assert ( aTokenBalanceBefore + assetsAmount == aTokenBalanceAfte &&
             totalAssetsBefore + assetsAmount == totalAssetsAfter &&
             totalSupplyBefore + sharesAmount == totalSupplyAfter &&
             aTokenBalanceOfMinterBefore - assetsAmount == aTokenBalanceOfMinterAfter
           ), "Invalid Deposit";

    if (receiver != e.msg.sender) {
        assert (senderBalanceBefore != receiverBalanceAfter), "Invalid Deposit";
    }

    assert (receiverBalanceBefore + sharesAmount == receiverBalanceAfter), "Invalid Deposit";
}


rule correctAmountOnPreviewMint(
    env e,
    address receiver,
    uint256 sharesAmount
) {
    setup(e, receiver);

    requireInvariant allCumulativeBalanceEqualToTotalSupply();

    require SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 1 ||
            SymbolicLendingPool.getReserveNormalizedIncome(e,getStaticATokenUnderlying()) == 2;
            
    
    //storage initalState = lastStorage;

    uint256 estimatedMintAmount = previewMint(e, sharesAmount);
    uint256 actualMintAmount = mint(e, sharesAmount, receiver);
    
    //uint256 mintedAmount = mint(e, shares, receiver) at initalState;

    assert estimatedMintAmount == actualMintAmount, "Invalid PreviewMint";
}

rule ConvertToSharesCorrectness(
    env e1,
    env e2,
    uint256 assetAmount
) {
    require e1.block.timestamp == e2.block.timestamp;
    assert convertToShares(e1, assetAmount) == convertToShares(e2, assetAmount), "convertToShares function have mismatch";
}

rule ConvertToAssetsCorrectness(
    env e1,
    env e2,
    uint256 sharesAmount
) {
    require e1.block.timestamp == e2.block.timestamp;
    assert convertToAssets(e1, sharesAmount) == convertToAssets(e2, sharesAmount), "convertToAssets function have mismatch";
}
