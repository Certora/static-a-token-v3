import "erc20.spec"
import "StaticATokenLM.spec"

using DummyERC20_aTokenUnderlying as underlying
using StaticATokenLMHarness as SAT
using AToken as ATok

methods{
    convertToAssets(uint256) returns (uint256)
    previewAndDepositCallHelper(uint256, address) returns (uint256, uint256)
    previewDeposit(uint256) returns(uint256) envfree
    deposit(uint256, address) returns (uint256)
    underlying.balanceOf(address) returns(uint256) envfree
    ATok.balanceOf(address) returns(uint256) envfree
    getULBalanceOf(address) returns(uint256) envfree
    getATokenBalanceOf(address) returns (uint256) envfree
    totalSupply() returns (uint256) envfree
    assetsTotal(address) returns (uint256) envfree
}

/***
* rule to check the following for the covertToAssets function:
* 1. Independent of the user
* 2. No revert unless overflow
* 3. Must round down
*/
// STATUS: WIP
rule convertToAssetsCheck(){
    env e1;
    env e2;
    env e3;
    uint256 shares1;
    uint256 shares2;
    uint256 assets1;
    uint256 assets2;
    uint256 assets3;
    uint256 combinedAssets;
    storage before  = lastStorage;
    
    assets1         = convertToAssets(e1, shares1)           at before;
    assets2         = convertToAssets(e2, shares1)           at before;
    assets3         = convertToAssets(e2, shares2)           at before;
    combinedAssets  = convertToAssets(e3, shares1 +shares2)  at before;

    // assert !lastReverted,"should not revert except for overflow";
    assert assets1 == assets2,"conversion to assets should be independent of env such as msg.sender";
    assert assets1 + assets3 <= combinedAssets,"conversion should round down and not up";
}

/***
* rule to check the following for the covertToShares function:
* 1. Independent of the user
* 2. No revert unless overflow
* 3. Must round down
*/
// STATUS: WIP
rule convertToSharesCheck(){
    env e1;
    env e2;
    env e3;
    uint256 assets1;
    uint256 assets2;
    uint256 shares1;
    uint256 shares2;
    uint256 shares3;
    uint256 combinedShares;
    storage before  = lastStorage;
    
    shares1         = convertToShares@withrevert(e1, assets1)            at before;
    shares2         = convertToShares           (e2, assets1)            at before;
    shares3         = convertToShares           (e2, assets2)            at before;
    combinedShares  = convertToShares           (e3, assets1 + assets2)  at before;

    assert !lastReverted,"should not revert except for overflow";
    assert shares1 == shares2,"conversion to shares should be independent of env such as msg.sender";
    assert shares1 + shares3 <= combinedShares,"conversion should round down and not up";
}

// maxDeposit
// rule maxDepositCheck(){
//     address receiver;
//     uint256 maxDep = maxDeposit(receiver);
//     uint256 depositAmt;
//     require depositAmt > maxDep;

//     deposit(receiver, maxDep);
//     deposit@withrevert(receiver, depositAmt);
//     assert lastReverted,"should revert for any amount greater than maxDep";
// }


/***
* rule to check the following for the previewDeposit function:
* _1. Preview should return a value less than or equal to deposit
* 2. Must not account for maxDeposit limit or the allowance of asset tokens
* 3. Must be inclusive of fees
* 4. Must not revert due to vault specific user/global limits
*/
// STATUS: Passing; WIP, more assertions to be added
rule previewDepositCheck(){
    env e;
    uint256 assets;
    address recipient;
    uint256 previewShares;
    uint256 shares;

    previewShares, shares =
    // previewAndDepositCallHelper@withrevert(e, assets, recipient);
    previewAndDepositCallHelper(e, assets, recipient);

    assert shares >= previewShares,"preview should returns a number as close to but no more than actual deposit";

}

/***
* rule to check the following for the depost function:
* 1. Must emit deposit event
* 2. MUST support EIP-20 approve / transferFrom on asset as a deposit flow
* 3. MUST revert if all of assets cannot be deposited
*/
// STATUS: WIP

rule depositCheck(env e){
    uint256 assets;
    address receiver;
    uint256 contractAssetBalBefore = ATok.balanceOf(currentContract);
    uint256 userAssetBalBefore = ATok.balanceOf(e.msg.sender);
    require e.msg.sender != currentContract;

    uint256 shares = deposit(e, assets, receiver);

    uint256 contractAssetBalAfter = ATok.balanceOf(currentContract);
    uint256 userAssetBalAfter = ATok.balanceOf(e.msg.sender);

    assert contractAssetBalAfter == contractAssetBalBefore + assets,"contract's assets should increase by the 'assets' amount";
}

rule metaDepositCheck(env e){
    
    calldataarg args;
    uint256 _ULBal = getULBalanceOf(currentContract);
    uint256 _ATBal = getATokenBalanceOf(currentContract);
    bool fromUnderlying;
    uint256 sharesReceived;
    uint256 value;
    
    fromUnderlying, value = metaDepositHelper(e, args);
    
    uint256 ULBal_ = getULBalanceOf(currentContract);
    uint256 ATBal_ = getATokenBalanceOf(currentContract);

    assert balanceCheck(fromUnderlying, _ULBal, ULBal_, _ATBal, ATBal_, value),"assets should be transferred correctly";
}

rule deposit4Check(env e){
    uint256 assets;
    address recipient;
    uint16 referralCode;
    bool fromUnderlying;

    uint256 _ULBal = getULBalanceOf(currentContract);
    uint256 _ATBal = getATokenBalanceOf(currentContract);

    uint256 sharesReceived;
    
    sharesReceived = deposit(e, assets, recipient, referralCode, fromUnderlying);

    uint256 ULBal_ = getULBalanceOf(currentContract);
    uint256 ATBal_ = getATokenBalanceOf(currentContract);

    assert balanceCheck(fromUnderlying, _ULBal, ULBal_, _ATBal, ATBal_, assets),"assets should be transferred correctly";
}
 
/***
* rule to check the following for the maxMint function:
* _1. MUST return as close to and no fewer than the exact amount of assets that would be deposited in a mint call in the same transaction. I.e. mint should return the same or fewer assets as previewMint if called in the same transaction.
* _2. MUST NOT account for mint limits like those returned from maxMint and should always act as though the mint would be accepted, regardless if the user has enough tokens approved
* 3. MUST be inclusive of deposit fees. Integrators should be aware of the existence of deposit fees.
* 4. MUST NOT revert due to vault specific user/global limits
*/
// STATUS: WIP
// Need to investigate the revert behaviour
rule previewMintCheck(env e){
    uint256 shares;
    address receiver;
    uint256 previewAssets;
    uint256 assets;
    require e.msg.value != 0;

    // previewAssets, assets = previewAndMintCallHelper@withrevert(e, shares, receiver);
    previewAssets, assets = previewAndMintCallHelper(e, shares, receiver);

    assert previewAssets >= assets,"previewMint should return assets more than or equal to actual assets returned by the mint function";
    // assert !lastReverted,"should not revert";
}

/***
* rule to check the following for the mint function:
* 1. Mints exactly shares Vault shares to receiver by depositing assets of underlying tokens.
* 2. MUST emit the Deposit event.
* 3. MUST support EIP-20 approve / transferFrom on asset as a mint flow.
* _4. MUST revert if all of shares cannot be minted 
*/
// STATUS: WIP
rule mintCheck(env e){
    uint256 shares;
    address receiver;
    uint256 assets;
    uint256 receiverBalBefore = balanceOf(receiver);
    assets = mint@withrevert(e, shares, receiver);
    uint256 receiverBalAfter = balanceOf(receiver);

    assert receiverBalAfter != receiverBalBefore + shares => lastReverted,"receiver should get the 'shares' amount minted to its account";

}


/***
* rule to check the following for the previewWithdraw function:
* _1. MUST return as close to and no fewer than the exact amount of Vault shares that would be burned in a withdraw call in the same transaction. I.e. withdraw should return the same or fewer shares as previewWithdraw if called in the same transaction
* 2. MUST NOT account for withdrawal limits like those returned from maxWithdraw and should always act as though the withdrawal would be accepted, regardless if the user has enough shares, etc.
* 3. MUST be inclusive of withdrawal fees
* 4. MUST NOT revert due to vault specific user/global limits.
*/
// STATUS: WIP
rule previewWithdrawCheck(env e){
    uint256 assets;
    address receiver;
    address owner;
    uint256 shares;
    uint256 previewShares;

    previewShares, shares = previewAndWithdrawCallHelper(e, assets, receiver, owner);
    // previewShares, shares = previewAndWithdrawCallHelper@withrevert(e, assets, receiver, owner);

    assert previewShares >= shares,"previewWithdraw should return assets less than or equal to those returned by withdraw function";
}


/***
* rule to check the following for the withdraw function:
* 1. MUST emit the Withdraw event.
* 2. MUST support a withdraw flow where the shares are burned from owner directly where owner is msg.sender.
* 3. MUST support a withdraw flow where the shares are burned from owner directly where msg.sender has EIP-20 approval over the shares of owner.
* _4. SHOULD check msg.sender can spend owner funds, assets needs to be converted to shares and shares should be checked for allowance.
* 5. MUST revert if all of assets cannot be withdrawn (due to withdrawal limit being reached, slippage, the owner not having enough shares, etc).
*/
// STATUS: WIP

rule metaWithdrawCheck(env e){
    
    address owner;
    address recipient;
    uint256 shares;
    uint256 assets;
    bool toUnderlying;
    uint256 deadline;
    uint8 v;
    bytes32 r;
    bytes32 s;
    // SAT.SignatureParams SP;
    calldataarg args;
    
    uint256 allowed = allowance(e, owner, e.msg.sender);
    uint256 _ULBal = getULBalanceOf(recipient);
    uint256 _ATBal = getATokenBalanceOf(recipient);

    uint256 sharesBurnt;
    uint256 assetsReceived;
    
    sharesBurnt, assetsReceived = metaWithdrawCallHelper(e, owner, recipient, shares, assets, toUnderlying, deadline, v, r, s);
    // sharesBurnt, assetsReceived = metaWithdrawCallHelper(e, owner, recipient, shares, assets, toUnderlying, deadline, v, r, s);
    
    uint256 ULBal_ = getULBalanceOf(recipient);
    uint256 ATBal_ = getATokenBalanceOf(recipient);

    // assertions
    // assert !lastReverted => allowed >= sharesBurnt,"msg.sender should have allowane to spend owner's shares";
    // assert !lastReverted => shares ==0 || assets == 0,"either shares or assets to be supplied";
    // assert !lastReverted => balanceCheck(toUnderlying, _ULBal, ULBal_, _ATBal, ATBal_, assetsReceived),"";
    assert allowed >= sharesBurnt,"msg.sender should have allowane to spend owner's shares";
    assert shares ==0 || assets == 0,"either shares or assets to be supplied";
    assert balanceCheck(toUnderlying, _ULBal, ULBal_, _ATBal, ATBal_, assetsReceived),"assets should be transferred correctly";
}

rule withdrawCheck(env e){
    
    address owner;
    address receiver;
    uint256 assets;
    
    uint256 allowed = allowance(e, owner, e.msg.sender);
    uint256 balBefore = ATok.balanceOf(receiver);
    

    uint256 sharesBurnt;
    uint256 assetsReceived;
    
    sharesBurnt = withdraw(e, assets, receiver, owner);

    uint256 balAfter = ATok.balanceOf(receiver);

    assert allowed >= sharesBurnt,"msg.sender should have allowane to spend owner's shares";
    assert balBefore + assets == balAfter,"assets should be transferred correctly";
}


function balanceCheck(bool toUnderlying, uint256 _ULBal, uint256 ULBal_, uint256 _ATBal, uint256 ATBal_, uint256 assetReceived) returns bool{
    if (toUnderlying){
        return(ULBal_ == _ULBal + assetReceived);
    }else{
        return(ATBal_ == _ATBal + assetReceived);
    }
}



/***
* rule to check the following for the withdraw function:
* _1. MUST return as close to and no more than the exact amount of assets that would be withdrawn in a redeem call in the same transaction. I.e. redeem should return the same or more assets as previewRedeem if called in the same transaction.
* 2. MUST NOT account for redemption limits like those returned from maxRedeem and should always act as though the redemption would be accepted, regardless if the user has enough shares, etc.
* 3. MUST be inclusive of withdrawal fees. Integrators should be aware of the existence of withdrawal fees.
* 4. MUST NOT revert due to vault specific user/global limits. MAY revert due to other conditions that would also cause redeem to revert.
*/
// STATUS: WIP

rule previewRedeemCheck(env e){
    uint256 shares;
    address receiver;
    address owner;
    uint256 previewAssets;
    uint256 assets;
    previewAssets, assets = previewAndRedeemHelper(e, shares, receiver, owner);
    // previewAssets, assets = previewAndRedeemHelper@withrevert(e, shares, receiver, owner);

    assert previewAssets <= assets,"preview should return no more than the actual assets received";
    // assert !lastReverted;

}


/***
* rule to check the following for the withdraw function:
* 1. MUST emit the Withdraw event.
* 2. MUST support a redeem flow where the shares are burned from owner directly where owner is msg.sender.
* 3. MUST support a redeem flow where the shares are burned from owner directly where msg.sender has EIP-20 approval over the shares of owner.
* 4. SHOULD check msg.sender can spend owner funds using allowance.
* 5. MUST revert if all of shares cannot be redeemed (due to withdrawal limit being reached, slippage, the owner not having enough shares, etc).
*/
// STATUS: WIP

rule redeemCheck(env e){
    uint256 shares;
    address receiver;
    address owner;
    uint256 assets;
    uint256 allowed = allowance(e, owner, e.msg.sender);
    uint256 balBefore = balanceOf(owner);
    
    assets = redeem(e, shares, receiver, owner);
    
    uint256 balAfter = balanceOf(owner);

    assert allowed >= balBefore - balAfter,"msg.sender should have allowance for transferring owner's shares";
    assert shares == balBefore -balAfter,"exactly the specified amount of shares must be burnt";

}

/***
* If there is a non-zero supply of shares, there must be a non-zero amount of assets backing the shares
*/
// STATUS: WIP
invariant noSupplyIfNoAssets()
    totalSupply() != 0 => assetsTotal(currentContract) != 0


/***
* If a user converts some assets to shares and then converts back to assets or start with shares and convert to and back from assets,
* the user will have LE the starting amount
*/
// STATUS: WIP

// rule houseAlwaysWins(env e){
//     uint256 _assets;
//     uint256 _shares;
//     uint256 _assets_;
//     uint256 _shares_;
//     uint256 assets_;
//     uint256 shares_;
//     address a1;
//     address a2;
//     address a3;
//     address a4;
//     address a5;
//     address a6;

//     _assets_ = redeem(e, _shares, a1, a2);
//     shares_ = deposit(e, _assets_, a3);

//     _shares_ = deposit(e, _assets, a4);
//     assets_ = redeem
//     assert shares_ <= _shares,"shares after converting to and back from assets, should be less than before";


// }



/****************************
 *** Michael's properties ***
 ****************************/

 // A larger asset deposit will either give the same amount or more shares compared to a smaller deposit

rule moreAssetToDepositResultMoreShares(uint256 assets1, uint256 assets2){
    address recipient; uint16 referralCode; bool fromUnderlying; 
    env e;
    require assets2 > assets1;
    uint256 _userShares = balanceOf(recipient);
    
    storage init = lastStorage;
    
    uint256 shares1 = deposit(e, assets1, recipient, referralCode, fromUnderlying);
    uint256 userShares1_ = balanceOf(recipient);
    
    uint256 shares2 = deposit(e, assets2, recipient, referralCode, fromUnderlying) at init;
    uint256 userShares2_ = balanceOf(recipient);

    assert shares2 >= shares1;
    assert userShares2_ - _userShares >= userShares1_ - _userShares;
}