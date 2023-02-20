import "erc20.spec"
import "StaticATokenLM.spec"

using DummyERC20_aTokenUnderlying as underlying

methods{
    convertToAssets(uint256) returns (uint256)
    previewAndDepositCallHelper(uint256, address) returns (uint256, uint256)
    previewDeposit(uint256) returns(uint256) envfree
    deposit(uint256, address) returns (uint256)
    underlying.balanceOf(address) returns(uint256) envfree
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
    
    assets1         = convertToAssets@withrevert(e1, shares1)           at before;
    assets2         = convertToAssets           (e2, shares1)           at before;
    assets3         = convertToAssets           (e2, shares2)           at before;
    combinedAssets  = convertToAssets           (e3, shares1 +shares2)  at before;

    assert !lastReverted,"should not revert except for overflow";
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
* 1. Preview should return a value less than or equal to deposit
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

    // // require that the currentContract has enough allowance for assets
    // uint256 _allowance = underlying.allowance(e.msg.sender, currentContract);

    // uint256 maxDep = maxDeposit();

    previewShares, shares =
    previewAndDepositCallHelper(e, assets, recipient);

    // storage state = lastStorage;

    // previewDeposit@withrevert(assets) at state;

    // bool previewRevert = lastReverted;

    // deposit@withrevert(assets, recipient) at state;

    // bool depositRevert = lastReverted;

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
    uint256 contractAssetBalBefore = underlying.balanceOf(currentContract);
    uint256 userAssetBalBefore = underlying.balanceOf(e.msg.sender);
    
    uint256 shares = deposit@withrevert(e, assets, receiver);

    uint256 contractAssetBalAfter = underlying.balanceOf(currentContract);
    uint256 userAssetBalAfter = underlying.balanceOf(e.msg.sender);

    assert contractAssetBalAfter != contractAssetBalBefore + assets => lastReverted,"contract's assets should increase by the 'assets' amount";
}

/***
* rule to check the following for the maxMint function:
* 1. MUST return as close to and no fewer than the exact amount of assets that would be deposited in a mint call in the same transaction. I.e. mint should return the same or fewer assets as previewMint if called in the same transaction.
* 2. MUST NOT account for mint limits like those returned from maxMint and should always act as though the mint would be accepted, regardless if the user has enough tokens approved
* 3. MUST be inclusive of deposit fees. Integrators should be aware of the existence of deposit fees.
* 4. MUST NOT revert due to vault specific user/global limits
*/
// STATUS: WIP
rule previewMintCheck(env e){
    uint256 shares;
    address receiver;
    uint256 previewAssets;
    uint256 assets;
    previewAssets, assets = previewAndMintCallHelper@withrevert(e, shares, receiver);

    assert previewAssets <= assets,"previewMint should return assets less than or equal to actual assets returned by the mint function";
    assert !lastReverted,"should not revert";
}

/***
* rule to check the following for the mint function:
* 1. Mints exactly shares Vault shares to receiver by depositing assets of underlying tokens.
* 2. MUST emit the Deposit event.
* 3. MUST support EIP-20 approve / transferFrom on asset as a mint flow.
* 4. MUST revert if all of shares cannot be minted 
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
* 1. MUST return as close to and no fewer than the exact amount of Vault shares that would be burned in a withdraw call in the same transaction. I.e. withdraw should return the same or fewer shares as previewWithdraw if called in the same transaction
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

    previewShares, shares = previewAndWithdrawCallHelper@withrevert(e, assets, receiver, owner);

    assert previewShares <= shares,"previewWithdraw should return assets less than or equal to those returned by withdraw function";
    assert !lastReverted;
}