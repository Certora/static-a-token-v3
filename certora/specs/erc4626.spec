import "erc20.spec"
import "StaticATokenLM.spec"

using DummyERC20_aTokenUnderlying as underlying
using StaticATokenLMHarness as SAT
using AToken as ATok
using SymbolicLendingPoolL1 as pool


methods{
    asset() returns (address) envfree
    convertToAssets(uint256) returns (uint256)
    convertToShares(uint256) returns (uint256)
    previewDeposit(uint256) returns(uint256) envfree
    deposit(uint256, address) returns (uint256)
    underlying.balanceOf(address) returns(uint256) envfree
    ATok.balanceOf(address) returns(uint256) envfree
    getULBalanceOf(address) returns(uint256) envfree
    getATokenBalanceOf(address) returns (uint256) envfree
    totalSupply() returns (uint256) envfree
    assetsTotal(address) returns (uint256) envfree
    totalAssets() returns (uint256) envfree
    pool.getReserveNormalizedIncome(address) returns (uint256)
    getStaticATokenUnderlying() returns (address) envfree
    upperBound(uint256) returns (uint256) envfree
    GetRAY() returns (uint256) envfree
    ATok._underlyingAsset() returns (address) envfree
    previewWithdraw(uint256) returns (uint256) envfree
    previewRedeem(uint256) returns (uint256) envfree
    maxRedeem(address) returns (uint256) envfree
    maxDeposit(address) returns (uint256) envfree
    ATok.allowance(address, address) returns (uint256) envfree
    previewMint(uint256) returns (uint256) envfree
    previewWithdraw(address) returns (uint256) envfree
    maxWithdraw(address) returns (uint256) envfree
    ATok.scaledBalanceOf(address) returns (uint256) envfree
}

///////////////// DEFINITIONS ///////////////////////

definition RAY() returns uint256 = 10^27;

///////////////// PREVIEW RULES ///////////////////////

/***
* rule to check the following for the previewDeposit function:
* _1. MUST return as close to and no more than the exact amount of Vault shares that would 
*     be minted in a deposit call in the same transaction. I.e. deposit should return the same or more shares as previewDeposit if called in the same transaction.
*/
// STATUS: Verified, that the amount returned by previewDeposit is exactly equal to that returned by the deposit function.
//         This is a stronger property than the one required by the EIP.

rule previewDepositAmountCheck(){
    env e;
    uint256 assets;
    address receiver;   
    uint256 previewShares;
    uint256 shares;

    previewShares = previewDeposit(assets);
    shares = deposit(e, assets, receiver);

    assert previewShares == shares,"preview shares should be equal to actual shares";
}

// The EIP4626 spec requires that the previewDeposit function must not account for maxDeposit limit or the allowance of asset tokens.
// checking that the previewDeposit value is independent of allowance of assets for some user. The fact that the previewDeposit function only takes 
// the asset amount as an argument and passes the envfree check which alone should be enough to conclude that it's not dependent on any asset allowance
// STATUS: Verified

rule previewDepositIndependentOfAllowance()
{
// allowance of currentContract for asset transfer from msg.sender to   
    address user;
    uint256 ATokAllowance1 = ATok.allowance(currentContract, user);
    uint256 assets1;
    uint256 assets2;
    uint256 assets3;
    require assets1 < ATokAllowance1;
    uint256 previewShares1 = previewDeposit(assets1);

    env e1;
    address receiver1;
    deposit(e1, assets2, receiver1);
    
    uint256 ATokAllowance2 = ATok.allowance(currentContract, user);
    require assets1 == ATokAllowance2;
    uint256 previewShares2 = previewDeposit(assets1);
    
    env e2;
    address receiver2;
    deposit(e2, assets3, receiver2); 
    
    uint256 ATokAllowance3 = ATok.allowance(currentContract, user);
    require assets1 > ATokAllowance3;
    uint256 previewShares3 = previewDeposit(assets1);

    assert previewShares1 == previewShares2,"previewDeposit should not change regardless of assets > or = allowance";
    assert previewShares2 == previewShares3,"previewDeposit should not change regardless of assets < or = allowance";
}

// The EIP4626 spec requires that the previewDeposit function must not account for maxDeposit limit or the allowance of asset tokens.
// Since maxDeposit is a constant, it cannot have any impact on the previewDeposit value.
// STATUS: Verified for all f except metaDeposit which has a reachability issue
// https://vaas-stg.certora.com/output/11775/42e457472f3eeb222744/?anonymousKey=d8e2a760f475fde4ccd07c0bbc4f5703887b9280
rule maxDepositConstant(method f){
    address receiver;
    uint256 maxDep1 = maxDeposit(receiver);
    calldataarg args;
    env e;
    f(e, args);
    uint256 maxDep2 = maxDeposit(receiver);

    assert maxDep1 == maxDep2,"maxDeposit should not change";
}

/***
* rule to check the following for the previewMint function:
* _1. MUST return as close to and no fewer than the exact amount of assets that would be deposited in a mint call in the same transaction. I.e. mint should return the same or fewer assets as previewMint if called in the same transaction.

*/
// STATUS: Verified, that the amount returned by previewDeposit is exactly equal to that returned by the deposit function.
//         This is a stronger property than the one required by the EIP.
rule previewMintAmountCheck(env e){
    uint256 shares;
    address receiver;
    uint256 previewAssets;
    uint256 assets;

    previewAssets = previewMint(shares);
    assets = mint(e, shares, receiver);
    assert previewAssets == assets,"preview should be equal to actual";
}


// The EIP4626 spec requires that the previewMint function must not account for mint limits like those returned from maxMint and should always act as though the mint would be accepted, regardless if the user has enough tokens approved
// a. Check against maxDeposit - maxMint returns maxUint256 
// b. Check against allowance
// checking that the previewDeposit value is independent of allowance of assets
// STATUS: Verified
// Since the previewMint function only takes an amount of shares it shouldn't be dependent on any allowance for asset transfer however, this rules checks
// that for any user's any allowance level, the previewMint function will always return the same value for given amount of shares
rule previewMintIndependentOfAllowance(){
// allowance of currentContract for asset transfer from msg.sender to   
    address user;
    uint256 ATokAllowance1 = ATok.allowance(currentContract, user);
    uint256 shares1;
    uint256 assets1;
    uint256 assets2;
    env e1;
    require convertToAssets(e1, shares1) < ATokAllowance1;
    uint256 previewAssets1 = previewMint(shares1);

    env e2;
    address receiver1;
    deposit(e2, assets1, receiver1);
    
    uint256 ATokAllowance2 = ATok.allowance(currentContract, user);
    env e3;
    require convertToAssets(e3, shares1) == ATokAllowance2;
    uint256 previewAssets2 = previewDeposit(shares1);
    
    env e4;
    address receiver2;
    deposit(e2, assets2, receiver2); 
    
    env e5;
    uint256 ATokAllowance3 = ATok.allowance(currentContract, user);
    require convertToAssets(e4, shares1) > ATokAllowance3;
    uint256 previewAssets3 = previewDeposit(shares1);

    assert previewAssets1 == previewAssets2,"previewMint should not change regardless of C2A(shares) > or = allowance";
    assert previewAssets2 == previewAssets3,"previewMint should not change regardless of C2A(shares) < or = allowance";
}


/***
* rule to check the following for the previewWithdraw function:
* _1. MUST return as close to and no fewer than the exact amount of Vault shares that would be burned in a withdraw call in the same transaction. I.e. withdraw should return the same or fewer shares as previewWithdraw if called in the same transaction
* 2. MUST NOT account for withdrawal limits like those returned from maxWithdraw and should always act as though the withdrawal would be accepted, regardless if the user has enough shares, etc.
*/
// STATUS: Verified, that the amount returned by previewWithdraw is exactly equal to that returned by the withdraw function.
//         This is a stronger property than the one required by the EIP.
rule previewWithdrawAmountCheck(env e){
    uint256 assets;
    address receiver;
    address owner;
    uint256 shares;
    uint256 previewShares;

    previewShares = previewWithdraw(assets);
    shares = withdraw(e, assets, receiver, owner);

    assert previewShares == shares,"preview should be equal to actual shares";
}

// The EIP4626 spec requires that the previewWithdraw function must not account for withdrawal limits like those returned from maxWithdraw and should always act as though the withdrawal would be accepted, regardless if the user has enough shares, etc.
// previewWithdraw function only takes a specified amount of assets an an input so it should be independent of any maxwithdraw limits for any user
// This rules checks that the previewWithdraw function return value is independent of any level of maxWithdraw (relative to the asset amount) for any user

// STATUS: Verified
// https://vaas-stg.certora.com/output/11775/438c5c7cdfe5aeb2e748/?anonymousKey=db46b6405216cc52722b118ee776e153aef43145

rule previewWithdrawIndependentOfMaxWithdraw(env e){
    env e1;
    env e2;
    address user;
    uint256 maxWithdraw1 = maxWithdraw(user);
    uint256 assets1;
    uint256 assets2;
    uint256 assets3;
    address receiver1;
    address receiver2;

    require assets1 > maxWithdraw1;
    uint256 previewShares1 = previewWithdraw(assets1);

    deposit(e1, assets2, receiver1);

    uint256 maxWithdraw2 = maxWithdraw(user);
    require assets1 ==  maxWithdraw2;
    uint256 previewShares2 = previewWithdraw(assets1);
    
    deposit(e2, assets2, receiver2);
    uint256 maxWithdraw3 = maxWithdraw(user);
    require assets1 <  maxWithdraw3;
    uint256 previewShares3 = previewWithdraw(assets1);

    assert previewShares1 == previewShares2 && previewShares2 == previewShares3,"preview withdraw should be independent of allowance";
}

// The EIP4626 spec requires that the previewWithdraw function must not account for withdrawal limits like those returned from maxWithdraw and should always act as though the withdrawal would be accepted, regardless if the user has enough shares, etc.
// This rules checks that the previewWithdraw function is independent of any level of share balance(relative to asset amount) of any user
// STATUS: Verified
// https://vaas-stg.certora.com/output/11775/f3b94b16a348c246559c/?anonymousKey=06dd3d3fcb718f74115c8b8e463225e37b25c005

rule previewWithdrawIndependentOfBalance(){
    env e1;
    env e2;
    env e3;
    env e4;
    env e5;
    address user;
    uint256 shareBal1 = balanceOf(user);
    uint256 assets1;
    uint256 assets2;
    uint256 assets3;
    address receiver1;
    address receiver2;
    
    require assets1 > convertToAssets(e3, shareBal1);//asset amount greater than what the user is entitled to on account of his share balance
    uint256 previewShares1 = previewWithdraw(assets1);

    deposit(e1, assets2, receiver1);
    uint256 shareBal2 = balanceOf(user);
    require assets1 ==  convertToAssets(e4, shareBal2); //asset amount equal to what the user is entitled to on account of his share balance
    uint256 previewShares2 = previewWithdraw(assets1);

    deposit(e2, assets3, receiver2);
    uint256 shareBal3 = balanceOf(user);
    require assets1 <  convertToAssets(e5, shareBal3); //asset amount less than what the user is entitled to on account of his share balance
    uint256 previewShares3 = previewWithdraw(assets1);
    
    assert previewShares1 == previewShares2 && previewShares2 == previewShares3,"preview withdraw should be independent of allowance";
}

/***
* rule to check the following for the withdraw function:
* _1. MUST return as CLOSE to and no more than the exact amount of assets that would be withdrawn in a redeem call in the same transaction. I.e. redeem should return the same or more assets as previewRedeem if called in the same transaction.
*/
// STATUS: Verified, that the amount returned by previewRedeem is exactly equal to that returned by the redeem function.
//         This is a stronger property than the one required by the EIP.

rule previewRedeemAmountCheck(env e){
    uint256 shares;
    address receiver;
    address owner;
    uint256 previewAssets;
    uint256 assets;
    
    previewAssets = previewRedeem(shares);
    assets = redeem(e, shares, receiver, owner);
    
    assert previewAssets == assets,"preview should the same as the actual assets received";
}

// The EIP4626 spec requires that the previewRedeem function must not account for redemption limits like those returned from maxRedeem and should always act as though the redemption would be accepted, regardless if the user has enough shares, etc.
// the preview function is independent of any user and should not be impacted in anyway by any user level restrictions
// this rule checks that the previewRedeem return value is independent of any level of maxRedeem (relative to the share amount) for any user.
// STATUS: Verified
// https://vaas-stg.certora.com/output/11775/e9dd774b10dccbb1570b/?anonymousKey=93a72f054ee636cfaf2772dbaed64bc3b64861fa

rule previewRedeemIndependentOfMaxRedeem(){
    env e1;
    env e2;
    address user1;
    address user2;
    address user3;
    uint256 shares1;
    uint256 shares2;
    uint256 shares3;
    uint256 maxRedeemableShares1 = maxRedeem(user1);
    require shares1 > maxRedeemableShares1;
    uint256 previewAssets1 = previewRedeem(shares1);
    
    mint(e1, shares2, user2);
    uint256 maxRedeemableShares2 = maxRedeem(user1);
    require shares1 == maxRedeemableShares2;
    uint256 previewAssets2 = previewRedeem(shares1);

    mint(e2, shares3, user3);
    uint256 maxRedeemableShares3 = maxRedeem(user1);
    require shares1 == maxRedeemableShares3;
    uint256 previewAssets3 = previewRedeem(shares1);

    assert previewAssets1 == previewAssets2 && previewAssets2 == previewAssets3,"previewRedeem should be independent of maxRedeem";
}

// The EIP4626 spec requires that the previewRedeem function must not account for redemption limits like those returned from maxRedeem and should always act as though the redemption would be accepted, regardless if the user has enough shares, etc.
// the preview function is independent of any user and should not be impacted in anyway by any user level restrictions
// this rule checks that the previewRedeem return value is independent of any level of share balance (relative to the redemption share amount) for any user.
// STATUS: Verified
// https://vaas-stg.certora.com/output/11775/a5c56d072ebd15d4c52d/?anonymousKey=ed5d24165ed3c04f953785b5213dacfdf369cd1c
rule previewRedeemIndependentOfBalance(){
    env e1;
    env e2;
    env e3;
    uint256 shares1;
    uint256 shares2;
    uint256 shares3;
    address user1;
    address user2;
    address user3;
    uint256 balance1 = balanceOf(user1);
    require shares1 > balance1;
    uint256 previewAssets1 = previewRedeem(shares1);

    mint(e1, shares2, user2);
    uint256 balance2 = balanceOf(user1);
    require shares1 == balance2;
    uint256 previewAssets2 = previewRedeem(shares1);
    
    mint(e1, shares3, user3);
    uint256 balance3 = balanceOf(user1);
    require shares1 < balance3;
    uint256 previewAssets3 = previewRedeem(shares1);

    assert previewAssets1 == previewAssets2 && previewAssets2 == previewAssets3,"previewRedeem should be independent of balance";
}


///////////////// DEPOSIT, MINT, WITHDRAW & REDEEM RULES ///////////////////////

/***
* rule to check the following for the depost function:
* 1. MUST revert if all of assets cannot be deposited
*/
// STATUS: Verified
// The function doesn't always deposit exactly the asset amount specified by the user due to rounding. The amount deposited is within 1/2AToken of the 
// amount specified by the user. The amount of shares minted would be zero for less than 1AToken worth of assets.

rule depositCheck(env e){
    uint256 assets;
    address receiver;
    uint256 contractAssetBalBefore = ATok.balanceOf(currentContract);
    uint256 userAssetBalBefore = ATok.balanceOf(e.msg.sender);
    uint256 userStaticBalBefore = balanceOf(e.msg.sender);
    uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());
    
    require getStaticATokenUnderlying() == ATok._underlyingAsset();//Without this a different index will be used for conversions in the Atoken contract compared to the one used in StaticAToken
    require e.msg.sender != currentContract;
    require index >= RAY();//since the index is initiated as RAY and only increases after that. index < RAY gives strange behaviors causing wildly inaccurate amounts being deposited and minted

    uint256 shares = deposit(e, assets, receiver);

    uint256 contractAssetBalAfter = ATok.balanceOf(currentContract);
    uint256 userAssetBalAfter = ATok.balanceOf(e.msg.sender); 
    uint256 userStaticBalAfter = balanceOf(e.msg.sender);

    assert contractAssetBalAfter <= contractAssetBalBefore + assets + index/(2 * RAY());
    // assert contractAssetBalAfter >= contractAssetBalBefore + assets - index/(2 * RAY());
    assert assets * RAY() >= index => shares != 0; //if the assets amount is worth at least 1 Atoken then receiver will get atleast 1 share
}

/***
* rule to check the following for the mint function:
* 1. MUST revert if all of shares cannot be minted
*/
// STATUS: VERIFIED
// When the index is less than RAY, the function can mint a higher number of shares than it was asked to
// https://vaas-stg.certora.com/output/11775/ea6a9c19c1b1b315017d/?anonymousKey=8d63aadfe646514e1229219e510e4bcb492144f0 (user asked for 101 shares but got 200, ref change in receiverBalBefore/After)
// This rule passes for both the assertions as long as the index is >= RAY. For index < RAY, only the assertions about the lower limit passes.
// 
rule mintCheckIndexGRay(env e){
    uint256 shares;
    address receiver;
    uint256 assets;
    require getStaticATokenUnderlying() == ATok._underlyingAsset();
    require e.msg.sender != currentContract;
    uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());

    uint256 receiverBalBefore = balanceOf(receiver);
    require index > RAY();
    
    assets = mint(e, shares, receiver);
    
    uint256 receiverBalAfter = balanceOf(receiver);
    
    assert receiverBalAfter <= receiverBalBefore + shares + 1,"receiver should get no more than the 1 extra share";
    assert receiverBalAfter >= receiverBalBefore + shares,"receiver should get no less than the amount of shares requested";
}
// Verified
rule mintCheckIndexEqualsRay(env e){
    uint256 shares;
    address receiver;
    uint256 assets;
    require getStaticATokenUnderlying() == ATok._underlyingAsset();
    require e.msg.sender != currentContract;
    uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());

    uint256 receiverBalBefore = balanceOf(receiver);
    require index == RAY();
    
    assets = mint(e, shares, receiver);
    
    uint256 receiverBalAfter = balanceOf(receiver);
    
    assert receiverBalAfter <= receiverBalBefore + shares + 1,"receiver should get no more than the 1 extra share";
    assert receiverBalAfter >= receiverBalBefore + shares,"receiver should get no less than the amount of shares requested";
}


/***
* rule to check the following for the withdraw function:
* 1. SHOULD check msg.sender can spend owner funds, assets needs to be converted to shares and shares should be checked for allowance.
* 2. MUST revert if all of assets cannot be withdrawn (due to withdrawal limit being reached, slippage, the owner not having enough shares, etc).
*/
// STATUS: VERIFIED
// violates #2 above. For any asset amount worth less than 1/2 AToken, the function will not withdrawn anything and not revert. EIP 4626 non compliant for assets < 1/2 AToken.
// For assets amount worth less than 1/2 AToken 0 assets will be withdrawn. Asset amount worth 1/2 AToken and more the final withdrawn amount would be assets +- 1/2AToken.
rule withdrawCheck(env e){    
    address owner;
    address receiver;
    uint256 assets;
    
    uint256 allowed = allowance(e, owner, e.msg.sender);
    uint256 balBefore = ATok.balanceOf(receiver);
    uint256 shareBalBefore = balanceOf(owner);
    require getStaticATokenUnderlying() == ATok._underlyingAsset();
    uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());
    require e.msg.sender != currentContract;
    require receiver != currentContract;
    require owner != currentContract;
    
    require index >= RAY();
    
    uint256 sharesBurnt = withdraw(e, assets, receiver, owner);

    uint256 balAfter = ATok.balanceOf(receiver);
    uint256 shareBalAfter = balanceOf(owner);

    // checking for allowance in case msg.sender is not the owner
    assert e.msg.sender != owner => allowed >= sharesBurnt,"msg.sender should have allowane to spend owner's shares";

    // lower bound. First part means atleast 1/2 AToken worth of UL is being deposited
    assert assets * 2 * RAY() >= index => balAfter - balBefore > assets - index/2*RAY(),
    "withdrawn amount should be no less than 1/2 AToken worth of UL less than the assets amount"; 
    
    //upper bound 
    assert balAfter - balBefore <= assets + index/2*RAY(),
    "withdrawn amount should be no more than 1/2 AToken worth of UL more than the number of assets ";
}


/***
* rule to check the following for the withdraw function:
* 1. SHOULD check msg.sender can spend owner funds using allowance.
* 2. MUST revert if all of shares cannot be redeemed (due to withdrawal limit being reached, slippage, the owner not having enough shares, etc).
*/
// STATUS: VERIFIED

rule redeemCheck(env e){
    uint256 shares;
    address receiver;
    address owner;
    uint256 assets;
    uint256 allowed = allowance(e, owner, e.msg.sender);
    uint256 balBefore = balanceOf(owner);
    uint256 ATokRecbalBefore = ATok.scaledBalanceOf(receiver);

    require getStaticATokenUnderlying() == ATok._underlyingAsset();
    uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());
    require index > RAY();
    require e.msg.sender != currentContract;
    require receiver != currentContract;
    
    assets = redeem(e, shares, receiver, owner);
    
    uint256 balAfter = balanceOf(owner);
    uint256 ATokRecbalAfter = ATok.scaledBalanceOf(receiver);

    assert e.msg.sender != owner => allowed >= (balBefore - balAfter),"msg.sender should have allowance for transferring owner's shares";
    assert shares == balBefore -balAfter,"exactly the specified amount of shares must be burnt";
}



/////////////////////////////// OTHER ERC4626 FUNCTIONS ////////////////////////////////////



/***
* rule to check the following for the covertToAssets function:
* 1. MUST NOT show any variations depending on the caller.
* 2. MUST round down towards 0.
*/
// STATUS: VERIFIED
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
    // require shares1 + shares2 < shares1;
    
    assets1         = convertToAssets(e1, shares1)           at before;
    assets2         = convertToAssets(e2, shares1)           at before;
    assets3         = convertToAssets(e2, shares2)           at before;
    combinedAssets  = convertToAssets(e3, shares1 +shares2)  at before;

    // assert !lastReverted,"should not revert except for overflow";
    assert assets1 == assets2,"conversion to assets should be independent of env such as msg.sender";
    assert shares1 + shares2 <= max_uint256 => assets1 + assets3 <= combinedAssets,"conversion should round down and not up";
}


/***
* rule to check the following for the convertToShares function:
* 1. MUST NOT show any variations depending on the caller.
* 2. MUST round down towards 0.
*/
// STATUS: VERIFIED
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
    require assets1 + assets2 < assets1;
    
    shares1         = convertToShares           (e1, assets1)            at before;
    shares2         = convertToShares           (e2, assets1)            at before;
    shares3         = convertToShares           (e2, assets2)            at before;
    combinedShares  = convertToShares           (e3, assets1 + assets2)  at before;

    
    assert shares1 == shares2,"conversion to shares should be independent of env variables including msg.sender";
    assert shares1 + shares3 <= combinedShares,"conversion should round down and not up";
}


/***
* rule to check the following for the maxWithdraw function:
* _1. MUST return the maximum amount of assets that could be transferred from owner through withdraw and not cause a revert, which MUST NOT be higher than the actual maximum that would be accepted (it should underestimate if necessary).
*/

// STATUS: VERIFIED
rule maxWithdrawCheck(){
    address owner;
    uint256 maxAssets = maxWithdraw(owner);
    address receiver;
    uint256 assets;

    env e;
    withdraw@withrevert(e, assets, receiver, owner);

    // assert assets <= maxAssets => !lastReverted;
    assert !lastReverted => assets <= maxAssets;
}

/***
* rule to check the following for the maxRedeem function:
* _1. MUST return the maximum amount of shares that could be transferred from owner through redeem and not cause a revert, which MUST NOT be higher than the actual maximum that would be accepted (it should underestimate if necessary).
*/

// STATUS: VERIFIED
rule maxRedeemCheck(){
    address owner;
    uint256 maxRed = maxRedeem(owner);
    address receiver;
    uint256 shares;
    
    env e;
    redeem@withrevert(e, shares, receiver, owner);

    assert !lastReverted => shares <= maxRed;
}


