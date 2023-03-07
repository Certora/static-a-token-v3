import "erc20.spec"
import "StaticATokenLM.spec"

using DummyERC20_aTokenUnderlying as underlying
using StaticATokenLMHarness as SAT
using AToken as ATok
using SymbolicLendingPoolL1 as pool

methods{
    convertToAssets(uint256) returns (uint256) envfree
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
}


definition RAY() returns uint256 = 10^27;
definition HALF_RAY() returns uint256 = 5 * 10^27;

///////////////// PREVIEW RULES ///////////////////////

/***
* rule to check the following for the previewDeposit function:
* _1. MUST return as close to and no more than the exact amount of Vault shares that would 
*     be minted in a deposit call in the same transaction. I.e. deposit should return the same or more shares as previewDeposit if called in the same transaction.
* 2. Must not account for maxDeposit limit or the allowance of asset tokens
*  a. Check against maxDeposit
*  b. Check against allowance
* 3. Must be inclusive of fees
* 4. Must not revert due to vault specific user/global limits
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
    // assert assets > maxdeposit() => !lastReverted; //investige this 
}


// checking that the previewDeposit value is independent of allowance of assets
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

    // address receiver;
    // uint256 maxDepositAssets1 = maxDeposit(receiver);
    // uint256 assets;
    // assert false;
    // require assets = maxDepositAssets1;
    // uint256 previewShares1 = previewDeposit(assets);
    
    // calldataarg args;
    // env e1;
    // f(e1, args);
    // uint256 maxDepositAssets2 = maxDeposit(receiver);
    
    // // require assets <= maxDepositAssets2;
    // uint256 previewShares2 = previewDeposit(assets);
    
    // assert previewShares2 == previewShares1,"previewDeposit should be independent of maxDeposit";
}

/***
* rule to check the following for the previewMint function:
* _1. MUST return as close to and no fewer than the exact amount of assets that would be deposited in a mint call in the same transaction. I.e. mint should return the same or fewer assets as previewMint if called in the same transaction.
* _2. MUST NOT account for mint limits like those returned from maxMint and should always act as though the mint would be accepted, regardless if the user has enough tokens approved
*  a. Check against maxDeposit
*  b. Check against allowance
* 3. MUST be inclusive of deposit fees. Integrators should be aware of the existence of deposit fees.
* 4. MUST NOT revert due to vault specific user/global limits
*/
// STATUS: Verified, that the amount returned by previewDeposit is exactly equal to that returned by the deposit function.
//         This is a stronger property than the one required by the EIP.
// Need to investigate the revert behaviour
rule previewMintAmountCheck(env e){
    uint256 shares;
    address receiver;
    uint256 previewAssets;
    uint256 assets;

    previewAssets = previewMint(shares);
    assets = mint(e, shares, receiver);

    // assert previewAssets >= assets,"previewMint should return assets more than or equal to actual assets returned by the mint function";
    // will not revert if the value passed in is greater than maxmint
    // assert !lastReverted,"should not revert";
    assert previewAssets == assets,"preview should be equal to actual";
}

// checking that the previewDeposit value is independent of allowance of assets
// STATUS: Verified

rule previewMintIndependentOfAllowance()
{
// allowance of currentContract for asset transfer from msg.sender to   
    address user;
    uint256 ATokAllowance1 = ATok.allowance(currentContract, user);
    uint256 shares1;
    uint256 assets1;
    uint256 assets2;
    require convertToAssets(shares1) < ATokAllowance1;
    uint256 previewAssets1 = previewMint(shares1);

    env e1;
    address receiver1;
    deposit(e1, assets1, receiver1);
    
    uint256 ATokAllowance2 = ATok.allowance(currentContract, user);
    require convertToAssets(shares1) == ATokAllowance2;
    uint256 previewAssets2 = previewDeposit(shares1);
    
    env e2;
    address receiver2;
    deposit(e2, assets2, receiver2); 
    
    uint256 ATokAllowance3 = ATok.allowance(currentContract, user);
    require convertToAssets(shares1) > ATokAllowance3;
    uint256 previewAssets3 = previewDeposit(shares1);

    assert previewAssets1 == previewAssets2,"previewMint should not change regardless of C2A(shares) > or = allowance";
    assert previewAssets2 == previewAssets3,"previewMint should not change regardless of C2A(shares) < or = allowance";
}


/***
* rule to check the following for the previewWithdraw function:
* _1. MUST return as close to and no fewer than the exact amount of Vault shares that would be burned in a withdraw call in the same transaction. I.e. withdraw should return the same or fewer shares as previewWithdraw if called in the same transaction
* 2. MUST NOT account for withdrawal limits like those returned from maxWithdraw and should always act as though the withdrawal would be accepted, regardless if the user has enough shares, etc.
* 3. MUST be inclusive of withdrawal fees
* 4. MUST NOT revert due to vault specific user/global limits.
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

// independent of maxWithdraw
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

// STATUS: Verified
// https://vaas-stg.certora.com/output/11775/f3b94b16a348c246559c/?anonymousKey=06dd3d3fcb718f74115c8b8e463225e37b25c005

rule previewWithdrawIndependentOfBalance(){
    env e1;
    env e2;
    address user;
    uint256 shareBal1 = balanceOf(user);
    uint256 assets1;
    uint256 assets2;
    uint256 assets3;
    address receiver1;
    address receiver2;
    
    require assets1 > convertToAssets(shareBal1);
    uint256 previewShares1 = previewWithdraw(assets1);

    deposit(e1, assets2, receiver1);
    uint256 shareBal2 = balanceOf(user);
    require assets1 ==  convertToAssets(shareBal2);
    uint256 previewShares2 = previewWithdraw(assets1);

    deposit(e2, assets3, receiver2);
    uint256 shareBal3 = balanceOf(user);
    require assets1 <  convertToAssets(shareBal3);
    uint256 previewShares3 = previewWithdraw(assets1);
    
    assert previewShares1 == previewShares2 && previewShares2 == previewShares3,"preview withdraw should be independent of allowance";
}

/***
* rule to check the following for the withdraw function:
* _1. MUST return as CLOSE to and no more than the exact amount of assets that would be withdrawn in a redeem call in the same transaction. I.e. redeem should return the same or more assets as previewRedeem if called in the same transaction.
* 2. MUST NOT account for redemption limits like those returned from maxRedeem and should always act as though the redemption would be accepted, regardless if the user has enough shares, etc.
* 3. MUST be inclusive of withdrawal fees. Integrators should be aware of the existence of withdrawal fees.
* 4. MUST NOT revert due to vault specific user/global limits. MAY revert due to other conditions that would also cause redeem to revert.
*/
// STATUS: Verified

rule previewRedeemAmountCheck(env e){
    uint256 shares;
    address receiver;
    address owner;
    uint256 previewAssets;
    uint256 assets;
    // allowance of the contract over the owner's shares
    // uint256 allowance = allowance(owner, currentContract);
    // actual share balance of owner
    // uint256 shareBalOwner = balanceOf(owner);
    // require shares > shareBalOwner;
    // require shares > allowance; 

    
    // require shares > maxRedeemableShares;
    previewAssets = previewRedeem(shares);
    assets = redeem(e, shares, receiver, owner);
    // assert false;
    // assert previewAssets <= assets,"preview should return no more than the actual assets received";
    assert previewAssets == assets,"preview should the same as the actual assets received";
    // assert !lastReverted;

}

// the preview function is independent of any user and should not be impacted in anyway by any user level restrictions
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
* 1. Must emit deposit event
* 2. MUST support EIP-20 approve / transferFrom on asset as a deposit flow
* 3. MUST revert if all of assets cannot be deposited
*/
// STATUS: Verified
// https://vaas-stg.certora.com/output/11775/ad5044ac72360e52ca0a/?anonymousKey=d12f43484902bab7d37b1499d45eb13cc04a8cc1

rule depositCheck(env e){
    uint256 assets; //547
    address receiver;
    // uint256 userAtokenBalBefore = ATok.scaledBalanceOf(e, e.msg.sender);
    uint256 contractAssetBalBefore = ATok.balanceOf(currentContract);
    uint256 userAssetBalBefore = ATok.balanceOf(e.msg.sender);
    uint256 userStaticBalBefore = balanceOf(e.msg.sender);
    require getStaticATokenUnderlying() == ATok._underlyingAsset();
    uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());
    require e.msg.sender != currentContract;
    // uint256 a;
    // require index == 7* RAY();
    require assets * RAY() >= index;//keep the asset amount greater than 1 Atoken

    uint256 shares = deposit(e, assets, receiver); // 548
    // index ~= 10^27

    uint256 contractAssetBalAfter = ATok.balanceOf(currentContract);
    uint256 userAssetBalAfter = ATok.balanceOf(e.msg.sender); 
    uint256 userStaticBalAfter = balanceOf(e.msg.sender);

    // assert contractAssetBalAfter == contractAssetBalBefore + assets,"contract's assets should increase by the 'assets' amount";
    // assert contractAssetBalAfter <= contractAssetBalBefore + assets + index/(2 * RAY());
    // assert contractAssetBalAfter >= contractAssetBalBefore + assets - index/(2 * RAY());
    // assert contractAssetBalAfter == contractAssetBalBefore + assets;
    // assert contractAssetBalAfter == contractAssetBalBefore => userStaticBalAfter == userStaticBalBefore,"user shouldn't get shares is no assets are deposited";
    assert shares != 0;
    assert 2 * shares * index > 2 * assets * RAY() - index,"shares should not be more than 1 AToken less than the number of ATokensßß";  
}

// shares = (asset * RAY + index/2)/index
// 2 * shares * index = 2 * asset * RAY + index
// X.5 -> 0.4999999 - 0.5
// shares > (asset * RAY/index) - 1/2

// USER DEPOSITING ATLEAST 1 ATOKEN, THEY SHOULD GET NONZERO SHARES

// index/ (2*RAY())


/***
* rule to check the following for the mint function:
* 1. MUST emit the Deposit event.
* 2. MUST support EIP-20 approve / transferFrom on asset as a mint flow.
* _3. MUST revert if all of shares cannot be minted 
*/
// STATUS: FAILED
// When the index is less than RAY, the function can mint a higher number of shares than it was asked to
// https://vaas-stg.certora.com/output/11775/ea6a9c19c1b1b315017d/?anonymousKey=8d63aadfe646514e1229219e510e4bcb492144f0 (user asked for 101 shares but got 200, ref change in receiverBalBefore/After)
// 
rule mintCheck(env e){
    uint256 shares;
    address receiver;
    uint256 assets;
    require getStaticATokenUnderlying() == ATok._underlyingAsset();
    require e.msg.sender != currentContract;
    uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());

    uint256 receiverBalBefore = balanceOf(receiver);
    require 100 * index == RAY();
    
    assets = mint(e, shares, receiver);
    
    uint256 receiverBalAfter = balanceOf(receiver);
    // index to be RAY/100 *****CHECK THIS
    // index to be greater than ray. then check ifthe 1 error limit holds

    // assert receiverBalAfter == receiverBalBefore + shares,"receiver should get exactly the number of shares requested";
    assert receiverBalAfter <= receiverBalBefore + shares + 1,"receiver should get no more than the 1 extra share";
    assert receiverBalAfter >= receiverBalBefore + shares,"receiver should get no less than the amount of shares requested";
    
}

// (shares * <RAY/3 + RAY -1)/RAY = 1 
// (RAY  + index/2)/index 
// 


/***
* rule to check the following for the withdraw function:
* 1. MUST emit the Withdraw event.
* 2. MUST support a withdraw flow where the shares are burned from owner directly where owner is msg.sender.
* 3. MUST support a withdraw flow where the shares are burned from owner directly where msg.sender has EIP-20 approval over the shares of owner.
* 4. SHOULD check msg.sender can spend owner funds, assets needs to be converted to shares and shares should be checked for allowance.
* 5. MUST revert if all of assets cannot be withdrawn (due to withdrawal limit being reached, slippage, the owner not having enough shares, etc).
*/
// STATUS
rule withdrawCheck(env e){
    
    address owner;
    address receiver;
    uint256 assets;
    
    uint256 allowed = allowance(e, owner, e.msg.sender);
    uint256 balBefore = ATok.balanceOf(receiver);
    require getStaticATokenUnderlying() == ATok._underlyingAsset();
    uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());
    require e.msg.sender != currentContract;
    require assets * RAY() >= index;//keep the asset amount greater than 1 Atoken

    uint256 sharesBurnt;
    
    sharesBurnt = withdraw(e, assets, receiver, owner);

    uint256 balAfter = ATok.balanceOf(receiver);
    // assert msg.sender == owner || allowance(msg.sender, owner) >= shares
    assert allowed >= sharesBurnt,"msg.sender should have allowane to spend owner's shares";
    assert balBefore + assets == balAfter,"assets should be transferred correctly";
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

    require getStaticATokenUnderlying() == ATok._underlyingAsset();
    uint256 index = pool.getReserveNormalizedIncome(e, getStaticATokenUnderlying());
    require e.msg.sender != currentContract;
    
    assets = redeem(e, shares, receiver, owner);
    
    uint256 balAfter = balanceOf(owner);

    assert allowed >= balBefore - balAfter,"msg.sender should have allowance for transferring owner's shares";
    assert shares == balBefore -balAfter,"exactly the specified amount of shares must be burnt";

}


///////////////// NON-ERC4626 DEPOSIT, MINT, WITHDRAW & REDEEM RULES ///////////////////////
// rule metaDepositCheck(env e){
    
//     calldataarg args;
//     uint256 _ULBal = getULBalanceOf(currentContract);
//     uint256 _ATBal = getATokenBalanceOf(currentContract);
//     bool fromUnderlying;
//     uint256 sharesReceived;
//     uint256 value;
    
//     fromUnderlying, value = metaDepositHelper(e, args);
    
//     uint256 ULBal_ = getULBalanceOf(currentContract);
//     uint256 ATBal_ = getATokenBalanceOf(currentContract);

//     assert balanceCheck(fromUnderlying, _ULBal, ULBal_, _ATBal, ATBal_, value),"assets should be transferred correctly";
// }


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
* rule to check the following for the withdraw function:
* 1. MUST emit the Withdraw event.
* 2. MUST support a withdraw flow where the shares are burned from owner directly where owner is msg.sender.
* 3. MUST support a withdraw flow where the shares are burned from owner directly where msg.sender has EIP-20 approval over the shares of owner.
* _4. SHOULD check msg.sender can spend owner funds, assets needs to be converted to shares and shares should be checked for allowance.
* 5. MUST revert if all of assets cannot be withdrawn (due to withdrawal limit being reached, slippage, the owner not having enough shares, etc).
*/
// STATUS: WIP

// rule metaWithdrawCheck(env e){
    
//     address owner;
//     address recipient;
//     uint256 shares;
//     uint256 assets;
//     bool toUnderlying;
//     uint256 deadline;
//     uint8 v;
//     bytes32 r;
//     bytes32 s;
//     // SAT.SignatureParams SP;
//     calldataarg args;
    
//     uint256 allowed = allowance(e, owner, e.msg.sender);
//     uint256 _ULBal = getULBalanceOf(recipient);
//     uint256 _ATBal = getATokenBalanceOf(recipient);

//     uint256 sharesBurnt;
//     uint256 assetsReceived;
    
//     sharesBurnt, assetsReceived = metaWithdrawCallHelper(e, owner, recipient, shares, assets, toUnderlying, deadline, v, r, s);
    
//     uint256 ULBal_ = getULBalanceOf(recipient);
//     uint256 ATBal_ = getATokenBalanceOf(recipient);

//     // assertions
//     // assert !lastReverted => allowed >= sharesBurnt,"msg.sender should have allowane to spend owner's shares";
//     // assert !lastReverted => shares ==0 || assets == 0,"either shares or assets to be supplied";
//     // assert !lastReverted => balanceCheck(toUnderlying, _ULBal, ULBal_, _ATBal, ATBal_, assetsReceived),"";
//     assert allowed >= sharesBurnt,"msg.sender should have allowane to spend owner's shares";
//     assert shares ==0 || assets == 0,"either shares or assets to be supplied";
//     assert balanceCheck(toUnderlying, _ULBal, ULBal_, _ATBal, ATBal_, assetsReceived),"assets should be transferred correctly";
// }


/////////////////////////////// OTHER ERC4626 FUNCTIONS ////////////////////////////////////

rule totalAssetCheck(){
    totalAssets@withrevert();
    assert !lastReverted;
}

// ghost to track sum of balances of atoken contract and check is equal to totalSupply
// rule totalAssetCheck(){

// }

// should be able to deposit an amount as long as it's less than maxdeposit amount
// rule maxDepositCheck(){
//     maxDeposit@withrevert();
//     assert !lastReverted;
// }

// 
// rule maxdepLimit(){
//     uint256 asset;
//     deposit@withrevert(assets);
    
//     assert !lastReverted => assets<= maxDeposit();
//     assert !lastReverted && assets == maxuint256 => maxDeposit() == maxuint;
// }

/***
* rule to check the following for the covertToAssets function:
* 1. Independent of the user
* 2. No revert unless overflow
* 3. Must round down
*/
// STATUS: WIP
// rule convertToAssetsCheck(){
//     env e1;
//     env e2;
//     env e3;
//     uint256 shares1;
//     uint256 shares2;
//     uint256 assets1;
//     uint256 assets2;
//     uint256 assets3;
//     uint256 combinedAssets;
//     storage before  = lastStorage;
    
//     assets1         = convertToAssets@withrevert(e1, shares1)           at before;
//     assets2         = convertToAssets@withrevert(e2, shares1)           at before;
//     assets3         = convertToAssets@withrevert(e2, shares2)           at before;
//     combinedAssets  = convertToAssets@withrevert(e3, shares1 +shares2)  at before;

//     // assert !lastReverted,"should not revert except for overflow";
//     assert assets1 == assets2,"conversion to assets should be independent of env such as msg.sender";
//     assert assets1 + assets3 <= combinedAssets,"conversion should round down and not up";
// }

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
* rule to check the following for the withdraw function:
* 1. MUST return the maximum amount of assets that could be transferred from owner through withdraw and not cause a revert, 
*    which MUST NOT be higher than the actual maximum that would be accepted (it should underestimate if necessary).
* 2. MUST factor in both global and user-specific limits, like if withdrawals are entirely disabled (even temporarily) it MUST return 0.
* 3. MUST NOT revert
*/

// STATUS: WIP
// rule maxWithdrawCheck(){

// }

// asset 200
// rate 100
// ray 10
// share 20

// asset 222
// rate 100
// ray 10
// share 22
// lost 20/100





function balanceCheck(bool toUnderlying, uint256 _ULBal, uint256 ULBal_, uint256 _ATBal, uint256 ATBal_, uint256 assetReceived) returns bool{
    if (toUnderlying){
        return(ULBal_ == _ULBal + assetReceived);
    }else{
        return(ATBal_ == _ATBal + assetReceived);
    }
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

invariant nonZeroSharesImplyNonZeroAssets()
    totalSupply() != 0 => ATok.balanceOf(currentContract) != 0
